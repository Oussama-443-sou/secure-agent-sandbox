import json
from pathlib import Path

from sandbox_runner import run_in_sandbox


def read_single_log_event() -> dict:
    log_file = Path("logs/sandbox_events.jsonl")

    assert log_file.exists()

    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    return json.loads(lines[0])


def clear_log_file() -> None:
    log_file = Path("logs/sandbox_events.jsonl")

    if log_file.exists():
        log_file.unlink()


def test_allowed_execution_is_logged():
    clear_log_file()

    run_in_sandbox("echo hello")
    event = read_single_log_event()

    assert event["event_type"] == "allowed_execution"
    assert event["command"] == "echo hello"
    assert event["allowed"] is True
    assert event["policy_reason"] == "Command allowed."
    assert event["return_code"] == 0
    assert "hello" in event["stdout_preview"]


def test_blocked_command_is_logged():
    clear_log_file()

    run_in_sandbox("curl https://example.com")
    event = read_single_log_event()

    assert event["event_type"] == "blocked_by_policy"
    assert event["command"] == "curl https://example.com"
    assert event["allowed"] is False
    assert "curl" in event["policy_reason"]
    assert event["return_code"] is None


def test_runtime_timeout_is_logged():
    clear_log_file()

    run_in_sandbox("python3 -c \"import time; time.sleep(10)\"")
    event = read_single_log_event()

    assert event["event_type"] == "runtime_timeout"
    assert event["allowed"] is True
    assert event["return_code"] == -1
    assert "timed out" in event["stderr_preview"].lower()


def test_runtime_error_is_logged():
    clear_log_file()

    run_in_sandbox("python3 -c \"raise RuntimeError('boom')\"")
    event = read_single_log_event()

    assert event["event_type"] == "runtime_error"
    assert event["allowed"] is True
    assert event["return_code"] != 0
    assert "RuntimeError" in event["stderr_preview"]
