# Repo Agent Conventions — constituency-priorities

## Language and Formatting
- Python: use ruff for formatting and linting. Line length 100. Type annotations on all public functions.
- TypeScript: ESLint + Prettier. All components typed. No `any`.
- All UI strings must go through the i18n system (`frontend/lib/i18n/`). Never hardcode English strings in JSX.

## Testing
- Every function in `backend/app/scoring/` MUST have unit tests. The Gap Score formula is our core technical IP — judges will probe it.
- Classification tests must include at least 3 non-English test cases (Hindi, Telugu).
- Run `pytest backend/tests/` before every PR merge. CI will enforce this.

## Gemini Prompt Management
- All prompt templates live in `backend/app/nlp/prompts.py`. No inline prompt strings anywhere else in the codebase.
- Every prompt must have a version comment: `# v1.2 — added urgency extraction 2026-06-XX`
- When changing a prompt, bump the version and add a comment explaining why.
- Prototype new prompts in Google AI Studio first, then port the finalized version here.

## Architecture Rules (non-negotiable)
- `gap_score.py` is DETERMINISTIC. No LLM calls inside it. Ever.
- `justification.py` calls Gemini 2.5 Pro. It receives computed numbers, not raw submissions.
- Never call Gemini Pro in a per-submission hot path. Pro is only for per-priority operations (~20 calls/constituency, not 1000).
- Use Gemini 2.5 Flash for all per-submission classification and entity extraction.

## Git Conventions
- Branch naming: `feature/description`, `fix/description`, `data/description`
- Commit messages: `type(scope): description`
  - Examples:
    - `feat(nlp): add urgency extraction to Flash classifier`
    - `fix(scoring): handle zero-division in normalization`
    - `data(census): add ward-level data for Hyderabad constituency`
- **No squash merges.** Judges check commit history. Real incremental commits across the month matter.
- Tag release candidates: `v0.x-rc1`

## Environment Variables
- Never commit secrets. Use `.env.local` (gitignored) for local dev.
- All secrets managed via Cloud Run `--set-secrets` in production.
- Required vars documented in `frontend/.env.local.example` and `backend/.env.example`.

## Deployment
- Backend deploys to Cloud Run (asia-south1) on merge to `main`.
- Frontend deploys to Firebase Hosting on merge to `main`.
- **Never deploy for the first time the night before demo day.** CI/CD should be wired from Week 1.
- The deployed BQ dataset should NEVER be wiped once seeded with 300+ submissions.
