# Secure Agent Sandbox

A small prototype sandbox for executing untrusted AI-agent commands inside restricted Docker containers.

This project was created to explore the security challenges involved in agentic workflows, especially when an AI agent needs to interact with tools, files, or command-line environments.

## Goal

The goal is to reduce the risk of unsafe agent actions by executing commands inside an isolated container with strict controls.

This first prototype focuses on:

- container isolation
- blocked network access
- resource limits
- temporary filesystem access
- non-root execution
- command allowlisting
- basic security logging

## Threat Model

The sandbox assumes that an AI agent may request unsafe commands, either because of:

- prompt injection
- malicious user input
- tool misuse
- hallucinated commands
- attempts to access sensitive files
- resource exhaustion attempts

The sandbox does not trust the command requested by the agent. Every command is checked by a policy layer before execution.

## Current Security Controls

The prototype uses Docker with:

- `--network none` to disable network access
- `--memory 128m` to limit memory usage
- `--cpus 0.5` to limit CPU usage
- `--pids-limit 64` to limit process creation
- `--read-only` to make the container filesystem read-only
- `--user 1000:1000` to avoid running as root
- a temporary mounted `/workspace` directory
- a Python timeout to stop long-running commands

## Example Usage

```bash
python3 sandbox_runner.py "echo hello"
