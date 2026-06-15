# Secure Agent Sandbox

A security-focused prototype for executing untrusted AI-agent commands inside restricted Docker containers.

The project explores how agentic systems can interact with tools and command-line environments without receiving unrestricted access to the host system.

## Overview

AI agents may generate unsafe commands because of:

* prompt injection;
* malicious user input;
* tool misuse;
* hallucinated actions;
* attempts to access sensitive resources;
* resource exhaustion.

This project applies a defense-in-depth approach:

1. A policy layer evaluates each requested command.
2. Allowed commands run inside a restricted Docker container.
3. Runtime behavior is monitored and classified.
4. Every execution is logged as a structured security event.
5. Automated tests verify expected security controls.

## Architecture

```text
AI agent or user command
          |
          v
+-------------------------+
| Command policy layer    |
| Allowlist and blocking  |
+-------------------------+
          |
          | allowed
          v
+-------------------------+
| Restricted Docker       |
| container               |
|                         |
| - no network            |
| - non-root user         |
| - read-only filesystem  |
| - CPU limit             |
| - memory limit          |
| - process limit         |
| - execution timeout     |
+-------------------------+
          |
          v
+-------------------------+
| Structured JSON logs    |
| Event classification    |
+-------------------------+
```

## Security Controls

The current prototype uses the following controls:

* **Command allowlisting** to restrict available executables.
* **Dangerous keyword detection** for known unsafe operations.
* **No network access** using Docker `--network none`.
* **Memory limitation** using `--memory 128m`.
* **CPU limitation** using `--cpus 0.5`.
* **Process limitation** using `--pids-limit 64`.
* **Read-only container filesystem** using `--read-only`.
* **Non-root execution** using `--user 1000:1000`.
* **Temporary workspace** mounted at `/workspace`.
* **Execution timeout** enforced by the Python runner.
* **Structured JSON Lines logging** for every execution.

## Security Event Classification

Each sandbox execution is classified as one of the following events:

| Event               | Meaning                                             |
| ------------------- | --------------------------------------------------- |
| `allowed_execution` | The command was allowed and completed successfully. |
| `blocked_by_policy` | The command was rejected before execution.          |
| `runtime_error`     | The command started but exited with an error.       |
| `runtime_timeout`   | The command exceeded the execution time limit.      |

Example log entry:

```json
{
  "timestamp": "2026-06-15T10:00:00+00:00",
  "event_type": "allowed_execution",
  "command": "echo hello",
  "allowed": true,
  "policy_reason": "Command allowed.",
  "return_code": 0,
  "duration_seconds": 0.48,
  "stdout_preview": "hello\n",
  "stderr_preview": ""
}
```

Logs are written to:

```text
logs/sandbox_events.jsonl
```

## Project Structure

```text
secure-agent-sandbox/
├── examples/
│   ├── malicious_filesystem.py
│   ├── malicious_network.py
│   └── safe_script.py
├── tests/
│   ├── conftest.py
│   ├── test_filesystem_escape.py
│   ├── test_forbidden_commands.py
│   ├── test_logging.py
│   ├── test_network_blocked.py
│   ├── test_policy.py
│   └── test_sandbox_runner.py
├── .gitignore
├── policy.py
├── requirements.txt
├── sandbox_runner.py
└── README.md
```

## Requirements

* Python 3.10 or later
* Docker
* pytest

Install the Python test dependency:

```bash
pip install -r requirements.txt
```

Verify that Docker is available:

```bash
docker --version
```

## Quick Start

Clone the repository:

```bash
git clone https://github.com/Oussama-443-sou/secure-agent-sandbox.git
cd secure-agent-sandbox
```

Run an allowed command:

```bash
python3 sandbox_runner.py "echo hello"
```

Expected result:

```text
Allowed: True
Return code: 0
STDOUT:
hello
```

Run a blocked command:

```bash
python3 sandbox_runner.py "curl https://example.com"
```

Expected result:

```text
Allowed: False
Policy reason: Forbidden keyword detected: curl
```

Test container-level network isolation:

```bash
python3 sandbox_runner.py \
"python3 -c \"import socket; socket.create_connection(('example.com', 80), timeout=2)\""
```

The policy allows Python, but the network connection should fail because the container uses `--network none`.

Test timeout enforcement:

```bash
python3 sandbox_runner.py \
"python3 -c \"import time; time.sleep(10)\""
```

The process should be stopped after the configured timeout and classified as:

```text
runtime_timeout
```

## Automated Security Tests

Run the full test suite:

```bash
pytest
```

The current suite contains **19 automated tests** covering:

* policy allowlisting;
* forbidden command blocking;
* sandbox execution;
* network isolation;
* filesystem isolation;
* temporary workspace behavior;
* runtime errors;
* runtime timeouts;
* structured security logging;
* security event classification.

Example result:

```text
======================== 19 passed ========================
```

## Threat Model

The sandbox assumes that commands requested by an AI agent are untrusted.

The prototype is designed to reduce the risk of:

* arbitrary command execution;
* unauthorized network access;
* access to host files;
* uncontrolled process creation;
* excessive CPU or memory consumption;
* long-running or hanging tasks;
* insufficient auditability.

The project uses several independent controls because no single mechanism should be treated as sufficient protection.

## Design Principles

### Least privilege

The agent receives only the permissions required for a limited task.

### Allowlist over blocklist

Unknown commands are rejected by default. Blocking only known dangerous commands would leave many bypass opportunities.

### Defense in depth

The policy layer, Docker restrictions, resource limits, timeout handling, and logging provide separate layers of protection.

### Observability

Every attempt is recorded, including blocked actions and runtime failures. Security controls are more useful when their decisions can be audited.

## Current Limitations

This project is an educational prototype and is not intended to be a production-ready security boundary.

Known limitations include:

* Docker containers share the host kernel.
* Containers do not protect against every kernel or container escape vulnerability.
* The command policy still relies partly on keyword matching.
* Commands currently run through `sh -c`.
* Shell syntax may allow policy bypass attempts.
* The project does not yet use a custom seccomp profile.
* The project does not yet use AppArmor or SELinux policies.
* Logs are stored locally rather than forwarded to a centralized monitoring system.
* The prototype does not yet implement controlled intercom services.

## Potential Improvements

Future work could include:

* replacing arbitrary shell commands with structured tool APIs;
* removing or restricting `sh -c`;
* adding custom seccomp profiles;
* adding AppArmor or SELinux policies;
* dropping additional Linux capabilities;
* comparing Docker isolation with gVisor or Firecracker;
* implementing controlled communication channels;
* adding centralized SIEM integration;
* adding GitHub Actions continuous integration;
* documenting abuse cases through a formal threat model;
* testing container escape and privilege escalation scenarios in a safe lab environment.

## Interview and Research Context

This project was created as a personal learning project to explore secure execution for AI agents and agentic workflows.

Its purpose is to demonstrate practical understanding of:

* container security;
* sandbox design;
* least privilege;
* security testing;
* monitoring;
* runtime isolation;
* AI-agent security risks.

## Disclaimer

This repository is intended for educational and defensive security research purposes.

It should not be treated as a hardened production sandbox without further security review and isolation controls.
