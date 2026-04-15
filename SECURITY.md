# Security Policy

## Supported Versions

This repository is maintained on the current `main` branch. Security fixes are applied to the active codebase and documented in the change history.

## Security Guidelines

- Keep secrets out of version control.
- Store database credentials, OpenAI keys, and environment-specific values in `.env`.
- Do not commit local overrides, dump files, or generated cache directories.
- Validate all PATCH and POST payloads on the backend.
- Prefer parameterized queries and ORM operations over raw SQL.

## Reporting a Vulnerability

If you discover a security issue, report it privately to the project maintainer before opening a public issue.

Include:

- A short description of the issue.
- The affected route, component, or database area.
- Steps to reproduce.
- Any logs, screenshots, or request payloads that help confirm the problem.

We will acknowledge the report, investigate it, and coordinate a fix before any public disclosure.
