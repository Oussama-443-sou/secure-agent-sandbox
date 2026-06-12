from policy import is_command_allowed


def test_safe_echo_allowed():
    allowed, reason = is_command_allowed("echo hello")
    assert allowed is True


def test_empty_command_blocked():
    allowed, reason = is_command_allowed("")
    assert allowed is False
    assert "Empty command" in reason


def test_curl_blocked():
    allowed, reason = is_command_allowed("curl https://example.com")
    assert allowed is False
    assert "curl" in reason


def test_rm_blocked():
    allowed, reason = is_command_allowed("rm -rf /")
    assert allowed is False
    assert "rm" in reason


def test_unknown_command_blocked():
    allowed, reason = is_command_allowed("whoami")
    assert allowed is False
    assert "allowlist" in reason
