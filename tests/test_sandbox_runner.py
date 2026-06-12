from sandbox_runner import run_in_sandbox


def test_echo_runs_successfully_in_sandbox():
    result = run_in_sandbox("echo hello")

    assert result["allowed"] is True
    assert result["return_code"] == 0
    assert "hello" in result["stdout"]


def test_pwd_runs_inside_workspace():
    result = run_in_sandbox("pwd")

    assert result["allowed"] is True
    assert result["return_code"] == 0
    assert "/workspace" in result["stdout"]


def test_network_disabled_at_container_level():
    result = run_in_sandbox(
        "python3 -c \"import socket; socket.create_connection(('example.com', 80), timeout=2)\""
    )

    assert result["allowed"] is True
    assert result["return_code"] != 0
    assert "Network is unreachable" in result["stderr"] or "Temporary failure" in result["stderr"] or result["stderr"]


def test_timeout_stops_long_running_command():
    result = run_in_sandbox(
        "python3 -c \"import time; time.sleep(10)\""
    )

    assert result["allowed"] is True
    assert result["return_code"] == -1
    assert "timed out" in result["stderr"].lower()
