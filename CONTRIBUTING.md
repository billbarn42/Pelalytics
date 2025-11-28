# Contributing

## Branching Strategy
- Create feature branches off `main` using prefixes:
  - `feature/<short-name>` for new features
  - `fix/<short-name>` for bug fixes
  - `docs/<short-name>` for documentation
- Keep branches focused and small for easier review.

## Pull Requests
- Open PRs targeting `main`.
- Provide a concise description and testing notes.
- Ensure CI is green (lint/format pass, minimal DB sanity).
- Prefer "Squash and merge" to keep linear history.

## Commit Style
- Use clear, imperative messages:
  - `Add FTP warmup pairing to plan generator`
  - `Fix overshoot handling in date range navigation`

## Code Quality
- Run `ruff check .` and `black --check .` locally.
- Avoid committing secrets or database files.
- Keep changes minimal and focused.

## Issues & Discussions
- File issues with reproduction steps and environment details.
- Use Discussions for roadmap ideas and larger design topics.

Thanks for contributing!