from sandbox_runner import run_in_sandbox


def test_python_socket_network_access_is_blocked():
    result = run_in_sandbox(
        "python3 -c \"import socket; socket.create_connection(('example.com', 80), timeout=2)\""
    )

    assert result["allowed"] is True
    assert result["return_code"] != 0
    assert result["stderr"]
