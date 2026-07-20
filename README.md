# Local Lingo for Home Assistant

Private-alpha local language learning for Home Assistant. Local Lingo currently targets German and Spanish, supports multiple learner profiles, stores progress locally, and provides two custom Lovelace cards:

- `custom:local-lingo-lesson-card`
- `custom:local-lingo-progress-card`

The visual style is playful and language-learning inspired, but the project does not use Duolingo branding, logos, mascots, assets, accounts, or services.

## Alpha scope

This first scaffold includes:

- Home Assistant config flow
- No preconfigured learner profiles
- Add-user support through the progress card and WebSocket API
- German and Spanish starter language packs
- Five-, ten-, and fifteen-question lessons
- Multiple-choice German/Spanish to English and English to German
- German article questions
- Local points, streaks, word exposure, and mastery tracking
- Resumable lesson sessions
- One compact progress sensor per learner and language
- GitHub Actions validation and installable config-overlay artifact

The included language packs are intentionally small starter datasets. The planned beta target is at least 1,000 reviewed entries per language.

## Repository layout

```text
custom_components/local_lingo/   Home Assistant backend and language packs
www/local_lingo/                 Lovelace card bundle
tests/                           Pure lesson-engine tests
scripts/                         Language-pack validation
.github/workflows/               Validation and packaging
```

## Private beta installation

1. Download the `local-lingo-config-overlay` artifact from a successful GitHub Actions run.
2. Extract it into the Home Assistant `/config` directory. It creates:
   - `/config/custom_components/local_lingo`
   - `/config/www/local_lingo`
3. Restart Home Assistant.
4. Open **Settings → Devices & services → Add integration** and add **Local Lingo**.
5. Register the frontend resource:

```yaml
url: /local/local_lingo/local-lingo-cards.js
resource_type: module
```

6. Add the progress card first so the first learner can be created:

```yaml
type: custom:local-lingo-progress-card
title: Learner Progress
language: de
```

7. Select **ADD USER**, create at least one learner, and then add the lesson card:

```yaml
type: custom:local-lingo-lesson-card
title: Language Practice
default_language: de
question_count: 10
```

## Current limitations

- Starter vocabulary only; not yet the planned 1,000 reviewed entries per language.
- No TTS or listening questions yet.
- Newly added profiles appear in the cards immediately, but summary sensors for them require an integration reload in this alpha.
- Review scheduling is not yet spaced repetition; current lessons use seeded random selection.
- Temporary-profile auto-reset is not implemented yet.
- Frontend is a direct JavaScript alpha implementation rather than the final Lit/TypeScript build.

## Development roadmap

### Alpha 1

- End-to-end lesson loop
- Profile creation
- German and Spanish starter packs
- Points, streaks, progress card
- Private artifact deployment

### Alpha 2

- Adaptive review queue
- Temporary-profile reset rules
- Edit, disable, and delete profile UI
- TTS configuration and listening questions
- Dynamic summary sensor creation

### Beta

- 1,000 reviewed German entries
- 1,000 reviewed Spanish entries
- Expanded question types
- Import/export and diagnostics
- Store schema migrations
- Tablet and phone usability testing

### Public-readiness

- Public repository decision
- HACS packaging
- Documentation, issue templates, security policy, and release automation

## Privacy

A fresh installation contains no learner profiles. Profile names, progress, and active sessions are stored through Home Assistant persistent storage only after an administrator creates them. No telemetry or cloud service is used by Local Lingo. Frontend files contain no learner progress or credentials.
