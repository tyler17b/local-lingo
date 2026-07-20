# Development notes

## Recommended branches

- `main`: installable alpha/beta releases
- `develop`: integrated upcoming work
- `agent/*` or `feature/*`: focused changes
- `release/*`: stabilization
- `hotfix/*`: urgent production fixes

## Validation

```bash
python scripts/validate_language_packs.py
python -m compileall custom_components/local_lingo
pytest -q
node --check custom_components/local_lingo/frontend/local-lingo-cards.js
python -m json.tool hacs.json >/dev/null
```

GitHub Actions also runs Home Assistant hassfest and HACS validation.

## Backend responsibilities

The integration owns profiles, language packs, sessions, answer scoring, points, streaks, and persistent state. The cards are thin authenticated clients over Home Assistant WebSocket commands.

The dashboard card bundle is packaged inside `custom_components/local_lingo/frontend` and is served at `/local_lingo/local-lingo-cards.js` after Home Assistant loads the integration.

## WebSocket commands

- `local_lingo/list_users`
- `local_lingo/upsert_user`
- `local_lingo/list_languages`
- `local_lingo/start_lesson`
- `local_lingo/get_active_session`
- `local_lingo/submit_answer`
- `local_lingo/get_progress_summary`
- `local_lingo/reset_progress`

## Storage keys

- `local_lingo_profiles`
- `local_lingo_progress`
- `local_lingo_sessions`

Never manually edit Home Assistant `.storage` files during ordinary use.
