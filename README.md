# Local Lingo for Home Assistant

Local Lingo is a local-first, touch-friendly language-learning integration for Home Assistant. It supports German and Spanish, multiple learner profiles, locally stored progress, difficulty-based practice, and configurable pronunciation for both questions and answers.

Dashboard cards:

- `custom:local-lingo-lesson-card`
- `custom:local-lingo-progress-card`

The interface is playful and language-learning inspired, but the project does not use Duolingo branding, logos, mascots, assets, accounts, or services.

## Alpha 4 scope

- Home Assistant config flow with no preconfigured learner profiles
- 103 beginner vocabulary entries per language
- 30 reviewed sentence-completion exercises per language
- Level 1 word, translation, and article questions
- Level 2 sentence-context questions
- Mixed practice combining both levels
- Natural instructions such as “How do you say … in Spanish?”
- Touch-first answer controls and a clear **CHECK ANSWER → CONTINUE / TRY AGAIN** flow
- Immediate XP and progress-card updates
- Tappable pronunciation for the question, every answer option, and the complete correct answer
- On-device browser TTS or configurable Home Assistant `tts.speak`
- Optional automatic question and answer pronunciation
- Local points, streaks, word exposure, mastery, and resumable lesson sessions
- HACS-compatible repository structure and validation workflows

The long-term beta target remains at least 1,000 reviewed entries per language.

## Install with HACS

1. In HACS, open the three-dot menu and select **Custom repositories**.
2. Enter `https://github.com/tyler17b/local-lingo`.
3. Select **Integration**, then select **Add**.
4. Open Local Lingo in HACS and select **Download**.
5. Restart Home Assistant.
6. Open **Settings → Devices & services → Add integration** and add **Local Lingo**.

Register the bundled dashboard resource once under **Settings → Dashboards → Resources**:

```text
/local_lingo/local-lingo-cards.js
```

Resource type: **JavaScript module**.

## Add the dashboard cards

Add the progress card first:

```yaml
type: custom:local-lingo-progress-card
title: Learner Progress
language: de
grid_options:
  columns: 12
  rows: auto
```

Create at least one learner, then add the lesson card.

### On-device TTS

Browser mode speaks through the tablet or computer currently displaying the dashboard. It is the portable default and does not require a media-player entity.

```yaml
type: custom:local-lingo-lesson-card
title: Language Practice
default_language: de
question_count: 10
difficulty: 1
tts:
  mode: browser
  question: true
  answers: true
  auto_question: false
  auto_answer: false
  rate: 0.9
grid_options:
  columns: 12
  rows: auto
```

Both the question and every answer have separate pronunciation buttons. After checking an answer, the complete correct word or sentence can also be spoken.

### Home Assistant TTS

Use this mode when the dashboard device has a Home Assistant media-player entity or when audio should play on another speaker.

```yaml
type: custom:local-lingo-lesson-card
title: Language Practice
default_language: de
question_count: 10
difficulty: mixed
tts:
  mode: home_assistant
  entity_id: tts.google_translate_en_com
  media_player_entity_id: media_player.your_dashboard
  question: true
  answers: true
  auto_question: false
  auto_answer: true
  rate: 0.9
grid_options:
  columns: 12
  rows: auto
```

The card sends both questions and complete answers through `tts.speak`. Browser speech rate applies only to browser mode; provider behavior is controlled by the selected Home Assistant TTS integration.

The visual card editor exposes the language, default difficulty, lesson length, pronunciation mode, TTS and media-player entity IDs, pronunciation controls, and automatic speech options.

## Practice levels

- **Level 1 · Words** — English-to-target translations, target-to-English meanings, and supported article questions
- **Level 2 · Sentences** — choose the word that correctly completes a reviewed sentence
- **Mixed practice** — an even combination of Level 1 and Level 2 questions

Difficulty is selected before a lesson and is stored with resumable sessions.

## Language-pack structure

Each language directory can contain multiple `vocabulary.*.json` and `sentences.*.json` content shards. Local Lingo combines and validates them at startup. Language manifests provide full language names, TTS language codes, article choices, and available content counts.

Current packaged content:

| Language | Vocabulary | Sentence exercises |
|---|---:|---:|
| German | 103 | 30 |
| Spanish | 103 | 30 |

## Manual installation

1. Copy `custom_components/local_lingo` into `/config/custom_components/`.
2. Restart Home Assistant.
3. Add Local Lingo under **Settings → Devices & services**.
4. Register `/local_lingo/local-lingo-cards.js` as a JavaScript module.

## Current limitations

- The packs are expanded beginner alphas, not complete language courses.
- Browser TTS voice quality and availability depend on the operating system and browser.
- Home Assistant TTS requires the administrator to configure a TTS entity and playback media player.
- Review scheduling is not yet spaced repetition.
- Newly added profiles appear in the cards immediately, but summary sensors may require an integration reload.
- The dashboard resource must currently be registered once by the administrator.

## Roadmap

- Grow each language toward 250, then 500–1,000 reviewed entries
- Listening-only questions and typed recall
- Adaptive review and spaced repetition
- Profile editing, disabling, and deletion
- Dynamic summary-sensor creation
- Import/export, diagnostics, and storage migrations
- Additional languages through the same language-pack schema

## Privacy

A fresh installation contains no learner profiles. Profile names, progress, and active sessions are stored through Home Assistant persistent storage only after an administrator creates them. Local Lingo sends no telemetry. Browser pronunciation stays on the displaying device; Home Assistant pronunciation uses only the TTS and media-player services explicitly selected by the administrator. The bundled frontend contains no learner progress, credentials, or preconfigured household information.
