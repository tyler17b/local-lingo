import { LocalLingoLessonCard } from "./local-lingo-lesson.js";
import { LocalLingoProgressCard } from "./local-lingo-progress.js";
import { LocalLingoLessonCardEditor } from "./local-lingo-editor.js";

if (!customElements.get("local-lingo-lesson-card")) customElements.define("local-lingo-lesson-card", LocalLingoLessonCard);
if (!customElements.get("local-lingo-progress-card")) customElements.define("local-lingo-progress-card", LocalLingoProgressCard);
if (!customElements.get("local-lingo-lesson-card-editor")) customElements.define("local-lingo-lesson-card-editor", LocalLingoLessonCardEditor);

window.customCards = window.customCards || [];
window.customCards.push(
  { type: "local-lingo-lesson-card", name: "Local Lingo Lesson Card", description: "Touch-friendly German and Spanish practice with configurable question and answer TTS." },
  { type: "local-lingo-progress-card", name: "Local Lingo Progress Card", description: "Live learner progress by language." },
);
