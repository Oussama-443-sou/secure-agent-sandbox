from pathlib import Path

from sandbox_runner import run_in_sandbox


def test_security_log_is_created():
    log_file = Path("logs/sandbox_events.jsonl")

    if log_file.exists():
        log_file.unlink()

    run_in_sandbox("echo hello")

    assert log_file.exists()

    content = log_file.read_text(encoding="utf-8")
    assert "echo hello" in content
    assert "Command allowed" in content
