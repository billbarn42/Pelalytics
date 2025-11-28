# Git Hygiene TODO Plan

Repository: https://github.com/billbarn42/Pelalytics
Branch: `main`

## Status Summary (Done)
- [x] Initialize Git repo and commits
- [x] Create GitHub remote and push (`origin/main`)
- [x] Add `.gitignore` entries for `peloton_classes.db`, `.env`, `legacy/peloton_client_repo/`
- [x] Stop tracking `peloton_classes.db`
- [x] Remove embedded legacy repo `legacy/peloton_client_repo` from tracking
- [x] Migrate old files into `legacy/`

## Next Actions

### Licensing & Metadata
- [ ] Add `LICENSE` (MIT recommended) and update README with license badge
- [ ] Add project description, topics, and homepage in GitHub repo settings

### Contribution Workflow
- [ ] Add `CONTRIBUTING.md` (how to set up venv, run scrapers, style expectations)
- [ ] Add `CODE_OF_CONDUCT.md`
- [ ] Add PR template (`.github/pull_request_template.md`)
- [ ] Add issue templates (`.github/ISSUE_TEMPLATE/bug_report.md`, `feature_request.md`)
- [ ] Add `CODEOWNERS` (optional: `@billbarn42` for everything)

### CI / Automation
- [ ] GitHub Actions: Python workflow (setup, install, lint, run minimal checks)
  - [ ] Use `ruff` + `black --check`
  - [ ] Optional: `pytest` harness (once tests exist)
- [ ] Dependabot config for GitHub Actions and Python dependencies
- [ ] Release Drafter (optional) to auto-generate release notes

### Branch & Release Strategy
- [ ] Enable branch protection on `main` (require PRs, status checks)
- [ ] Tag releases (e.g., `v0.1.0`) when major scraper improvements land
- [ ] Changelog (`CHANGELOG.md`) or auto-generated via Release Drafter

### Security & Secrets
- [ ] Add `.env.example` with `PELOTON_USERNAME`/`PELOTON_PASSWORD` placeholders
- [ ] Link README to GitHub Actions secrets guidance (if CI will use secrets)
- [ ] Enable GitHub secret scanning alerts for repo

### Project Structure & Docs
- [ ] README: quick start, batch usage, DB schema, troubleshooting (stale DOM), examples
- [ ] Document monthly batch plan and data coverage goals
- [ ] Add simple `Makefile` tasks: `make setup`, `make scrape-month`, `make batch-2025`
- [ ] Document SQLite usage and backup strategy (DB is local-only)

### Dev Ergonomics
- [ ] Add formatter/linter configs: `.ruff.toml`, `pyproject.toml` for `black`
- [ ] Pre-commit hooks (`pre-commit`) for formatting and linting
- [ ] Pin dependency versions where sensible; consider `pip-tools` for lockfile

### Cleanup & Housekeeping
- [ ] Ensure all legacy-only scripts remain under `legacy/`
- [ ] Verify large files aren’t tracked; consider Git LFS only if needed
- [ ] Add badges to README (CI, license)

## Notes
- Stale DOM handling and aggressive/dynamic fast-forward are in place.
- Batch scraping is currently focused on 2025; expand as needed after validation.
- `.env` is ignored; ensure local creds are set via environment or `.env`.
