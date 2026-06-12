from sandbox_runner import run_in_sandbox


def test_rm_command_is_blocked_before_execution():
    result = run_in_sandbox("rm -rf /")

    assert result["allowed"] is False
    assert result["return_code"] is None
    assert "rm" in result["policy_reason"]


def test_curl_command_is_blocked_before_execution():
    result = run_in_sandbox("curl https://example.com")

    assert result["allowed"] is False
    assert result["return_code"] is None
    assert "curl" in result["policy_reason"]


def test_unknown_binary_is_blocked_before_execution():
    result = run_in_sandbox("whoami")

    assert result["allowed"] is False
    assert result["return_code"] is None
    assert "allowlist" in result["policy_reason"]
