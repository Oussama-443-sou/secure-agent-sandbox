from sandbox_runner import run_in_sandbox


def test_host_filesystem_is_not_mounted():
    result = run_in_sandbox(
        "python3 -c \"from pathlib import Path; print(Path('/host/etc/passwd').exists())\""
    )

    assert result["allowed"] is True
    assert result["return_code"] == 0
    assert "False" in result["stdout"]


def test_container_runs_in_temporary_workspace():
    result = run_in_sandbox("pwd")

    assert result["allowed"] is True
    assert result["return_code"] == 0
    assert "/workspace" in result["stdout"]
