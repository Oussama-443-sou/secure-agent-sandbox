import argparse
import subprocess
import tempfile
import time
from pathlib import Path
import json
from datetime import datetime, timezone

from policy import is_command_allowed


DOCKER_IMAGE = "python:3.12-slim"

def classify_event(result: dict) -> str:
    """
    Classify a sandbox execution result into a security event type.

    This makes logs easier to analyze, filter, and monitor.
    """

    if not result["allowed"]:
        return "blocked_by_policy"

    if result["return_code"] == -1:
        return "runtime_timeout"

    if result["return_code"] != 0:
        return "runtime_error"

    return "allowed_execution"

def write_security_log(result: dict) -> None:
    """
    Write one structured JSON log entry per sandbox execution.

    In a real system, these logs could be sent to a SIEM, stored centrally,
    or monitored for suspicious behavior.
    """

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
	"event_type": classify_event(result),
        "command": result["command"],
        "allowed": result["allowed"],
        "policy_reason": result["policy_reason"],
        "return_code": result["return_code"],
        "duration_seconds": result["duration_seconds"],
        "stdout_preview": result["stdout"][:200],
        "stderr_preview": result["stderr"][:200],
    }

    with open(log_dir / "sandbox_events.jsonl", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")

def run_in_sandbox(command: str) -> dict:
    """
    Execute a command inside a restricted Docker container.

    Security controls in this first prototype:
    - no network access
    - memory limit
    - CPU limit
    - process limit
    - temporary mounted working directory
    - non-root user inside the container
    - timeout enforced by Python
    """

    allowed, reason = is_command_allowed(command)

    result = {
        "command": command,
        "allowed": allowed,
        "policy_reason": reason,
        "return_code": None,
        "stdout": "",
        "stderr": "",
        "duration_seconds": 0,
    }

    if not allowed:
        write_security_log(result)
        return result

    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir)

        docker_command = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--memory",
            "128m",
            "--cpus",
            "0.5",
            "--pids-limit",
            "64",
            "--read-only",
            "--user",
            "1000:1000",
            "-v",
            f"{workdir}:/workspace:rw",
            "-w",
            "/workspace",
            DOCKER_IMAGE,
            "sh",
            "-c",
            command,
        ]

        start = time.time()

        try:
            completed = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                timeout=5,
            )

            result["return_code"] = completed.returncode
            result["stdout"] = completed.stdout
            result["stderr"] = completed.stderr

        except subprocess.TimeoutExpired:
            result["return_code"] = -1
            result["stderr"] = "Command timed out."

        result["duration_seconds"] = round(time.time() - start, 3)
    write_security_log(result)
    return result


def print_result(result: dict) -> None:
    print("=== Sandbox Execution Result ===")
    print(f"Command: {result['command']}")
    print(f"Allowed: {result['allowed']}")
    print(f"Policy reason: {result['policy_reason']}")
    print(f"Return code: {result['return_code']}")
    print(f"Duration: {result['duration_seconds']} seconds")

    print("\n--- STDOUT ---")
    print(result["stdout"] if result["stdout"] else "<empty>")

    print("\n--- STDERR ---")
    print(result["stderr"] if result["stderr"] else "<empty>")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an agent-requested command inside a restricted Docker sandbox."
    )
    parser.add_argument(
        "command",
        help="Command to execute inside the sandbox.",
    )

    args = parser.parse_args()
    result = run_in_sandbox(args.command)
    print_result(result)


if __name__ == "__main__":
    main()
