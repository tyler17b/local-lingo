# Local Lingo for Home Assistant

Local Lingo is a local-first language-learning integration for Home Assistant. It currently supports German and Spanish, multiple learner profiles, locally stored progress, and two custom dashboard cards:

- `custom:local-lingo-lesson-card`
- `custom:local-lingo-progress-card`

The interface is playful and language-learning inspired, but the project does not use Duolingo branding, logos, mascots, assets, accounts, or services.

## Alpha scope

The current alpha includes:

- Home Assistant config flow
- No preconfigured learner profiles
- Learner creation through the progress card and authenticated WebSocket API
- German and Spanish starter language packs
- Five-, ten-, and fifteen-question lessons
- Multiple-choice target-language-to-English and English-to-target-language questions
- German article questions
- Local points, streaks, word exposure, and mastery tracking
- Resumable lesson sessions
- One compact progress sensor per learner and language
- HACS-compatible repository structure
- GitHub Actions validation with HACS and hassfest checks

The included language packs are intentionally small starter datasets. The planned beta target is at least 1,000 reviewed entries per language.

## Install with HACS

1. In HACS, open the three-dot menu and select **Custom repositories**.
2. Enter:

   ```text
   https://github.com/tyler17b/local-lingo
   ```

3. Select **Integration**, then select **Add**.
4. Open Local Lingo in HACS and select **Download**.
5. Restart Home Assistant.
6. Open **Settings → Devices & services → Add integration** and add **Local Lingo**.

Local Lingo bundles its dashboard cards inside the integration and serves them from Home Assistant. Register the resource once:

1. Open **Settings → Dashboards**.
2. Open the three-dot menu and select **Resources**.
3. Add this URL as a **JavaScript module**:

   ```text
   /local_lingo/local-lingo-cards.js
   ```

4. Refresh Home Assistant after saving the resource.

## Add the dashboard cards

Add the progress card first so the first learner can be created:

```yaml
type: custom:local-lingo-progress-card
title: Learner Progress
language: de
```

Select **ADD USER**, create at least one learner, and then add the lesson card:

```yaml
type: custom:local-lingo-lesson-card
title: Language Practice
default_language: de
question_count: 10
```

## Manual installation

1. Copy `custom_components/local_lingo` into your Home Assistant `/config/custom_components/` directory.
2. Restart Home Assistant.
3. Add the Local Lingo integration from **Settings → Devices & services**.
4. Register `/local_lingo/local-lingo-cards.js` as a JavaScript module under Dashboard Resources.

## Repository layout

```text
custom_components/local_lingo/           Home Assistant integration
custom_components/local_lingo/frontend/  Bundled dashboard cards
scripts/                                 Language-pack validation
tests/                                   Lesson-engine tests
.github/workflows/                       HACS, hassfest, and project validation
hacs.json                                HACS repository metadata
```

## Current limitations

- Starter vocabulary only; not yet the planned 1,000 reviewed entries per language.
- No text-to-speech or listening questions yet.
- Newly added profiles appear in the cards immediately, but summary sensors for them require an integration reload in this alpha.
- Review scheduling is not yet spaced repetition; current lessons use seeded random selection.
- Temporary-profile auto-reset is not implemented yet.
- The frontend is a direct JavaScript alpha implementation rather than the final Lit/TypeScript build.
- The dashboard resource must currently be registered once by the Home Assistant administrator.

## Development roadmap

### Alpha 2

- Adaptive review queue
- Temporary-profile reset rules
- Edit, disable, and delete profile UI
- Text-to-speech configuration and listening questions
- Dynamic summary sensor creation

### Beta

- 1,000 reviewed German entries
- 1,000 reviewed Spanish entries
- Expanded question types
- Import/export and diagnostics
- Store schema migrations
- Tablet and phone usability testing

## Privacy

A fresh installation contains no learner profiles. Profile names, progress, and active sessions are stored through Home Assistant persistent storage only after an administrator creates them. No telemetry or cloud service is used by Local Lingo. The bundled frontend contains no learner progress, credentials, or preconfigured household information.
