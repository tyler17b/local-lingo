import { LL_EDITOR_STYLE, esc } from "./local-lingo-shared.js";
import { LocalLingoLessonCard } from "./local-lingo-lesson.js";

export class LocalLingoLessonCardEditor extends HTMLElement {
  constructor() { super(); this.attachShadow({ mode: "open" }); this._config = LocalLingoLessonCard.getStubConfig(); }
  set hass(hass) { this._hass = hass; }
  setConfig(config) { this._config = { ...LocalLingoLessonCard.getStubConfig(), ...(config || {}), tts: { ...LocalLingoLessonCard.getStubConfig().tts, ...((config || {}).tts || {}) } }; this.render(); }
  changed() { this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: this._config }, bubbles: true, composed: true })); }
  render() {
    if (!this.shadowRoot) return;
    const tts = this._config.tts || {};
    this.shadowRoot.innerHTML = `<style>${LL_EDITOR_STYLE}</style><div class="editor"><div class="grid"><label>Title<input id="title" value="${esc(this._config.title || "")}"></label><label>Default language<select id="default_language"><option value="de" ${this._config.default_language === "de" ? "selected" : ""}>German</option><option value="es" ${this._config.default_language === "es" ? "selected" : ""}>Spanish</option></select></label><label>Default practice level<select id="difficulty"><option value="1" ${String(this._config.difficulty) === "1" ? "selected" : ""}>Level 1 · Words</option><option value="2" ${String(this._config.difficulty) === "2" ? "selected" : ""}>Level 2 · Sentences</option><option value="mixed" ${String(this._config.difficulty) === "mixed" ? "selected" : ""}>Mixed</option></select></label><label>Question count<select id="question_count">${[5,10,15].map((n) => `<option value="${n}" ${Number(this._config.question_count) === n ? "selected" : ""}>${n}</option>`).join("")}</select></label></div><hr><div class="grid"><label>Pronunciation mode<select id="tts_mode"><option value="browser" ${tts.mode === "browser" ? "selected" : ""}>This browser/device</option><option value="home_assistant" ${tts.mode === "home_assistant" ? "selected" : ""}>Home Assistant TTS</option><option value="off" ${tts.mode === "off" ? "selected" : ""}>Off</option></select></label><label>Speech rate<input id="tts_rate" type="number" min="0.5" max="2" step="0.1" value="${esc(tts.rate ?? 0.9)}"></label><label>TTS entity<input id="tts_entity" placeholder="tts.google_translate_en_com" value="${esc(tts.entity_id || "")}"></label><label>Playback media player<input id="tts_media" placeholder="media_player.dashboard" value="${esc(tts.media_player_entity_id || "")}"></label></div><label class="check"><input id="tts_question" type="checkbox" ${tts.question !== false ? "checked" : ""}>Show question pronunciation button</label><label class="check"><input id="tts_answers" type="checkbox" ${tts.answers !== false ? "checked" : ""}>Show answer pronunciation buttons</label><label class="check"><input id="auto_question" type="checkbox" ${tts.auto_question ? "checked" : ""}>Automatically speak each new question</label><label class="check"><input id="auto_answer" type="checkbox" ${tts.auto_answer ? "checked" : ""}>Automatically speak the complete answer after checking</label><div class="help">Browser mode speaks on the tablet or computer displaying the card. Home Assistant mode sends both questions and answers to the configured media player.</div></div>`;
    const update = (id, callback, eventName = "change") => { const element = this.shadowRoot.getElementById(id); if (element) element.addEventListener(eventName, () => { callback(element); this.changed(); }); };
    update("title", (el) => (this._config.title = el.value), "input");
    update("default_language", (el) => (this._config.default_language = el.value));
    update("difficulty", (el) => (this._config.difficulty = el.value === "mixed" ? "mixed" : Number(el.value)));
    update("question_count", (el) => (this._config.question_count = Number(el.value)));
    update("tts_mode", (el) => (this._config.tts.mode = el.value));
    update("tts_rate", (el) => (this._config.tts.rate = Number(el.value)));
    update("tts_entity", (el) => (this._config.tts.entity_id = el.value.trim()), "input");
    update("tts_media", (el) => (this._config.tts.media_player_entity_id = el.value.trim()), "input");
    update("tts_question", (el) => (this._config.tts.question = el.checked));
    update("tts_answers", (el) => (this._config.tts.answers = el.checked));
    update("auto_question", (el) => (this._config.tts.auto_question = el.checked));
    update("auto_answer", (el) => (this._config.tts.auto_answer = el.checked));
  }
}
