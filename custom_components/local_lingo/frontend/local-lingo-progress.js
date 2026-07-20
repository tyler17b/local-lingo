import { LL_PROGRESS_EVENT, LL_STYLE, esc } from "./local-lingo-shared.js";

export class LocalLingoProgressCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this.summary = [];
    this.languages = [];
    this.language = "de";
    this.error = null;
    this._unsubscribeProgress = null;
    this._refreshPending = false;
  }
  static getStubConfig() { return { title: "Learner Progress", language: "de" }; }
  setConfig(config) { this._config = config || {}; this.language = config.language || "de"; }
  set hass(hass) { this._hass = hass; if (!this.started) { this.started = true; this.load(); this.subscribeProgress(); } }
  disconnectedCallback() { if (this._unsubscribeProgress) { this._unsubscribeProgress(); this._unsubscribeProgress = null; } }
  getCardSize() { return 5; }
  getGridOptions() { return { columns: 12, min_columns: 6 }; }
  async subscribeProgress() { if (!this._hass?.connection || this._unsubscribeProgress) return; this._unsubscribeProgress = await this._hass.connection.subscribeEvents(() => this.scheduleRefresh(), LL_PROGRESS_EVENT); }
  scheduleRefresh() { if (this._refreshPending) return; this._refreshPending = true; queueMicrotask(async () => { try { await this.load(); } finally { this._refreshPending = false; } }); }
  async load() {
    if (!this._hass) return;
    try { [this.summary, this.languages] = await Promise.all([this._hass.callWS({ type: "local_lingo/get_progress_summary" }), this._hass.callWS({ type: "local_lingo/list_languages" })]); if (!this.languages.some((item) => item.code === this.language)) this.language = this.languages[0]?.code || "de"; this.error = null; }
    catch (error) { this.error = error.message || String(error); }
    this.render();
  }
  async addUser() { const displayName = window.prompt("New learner name"); if (!displayName?.trim()) return; await this._hass.callWS({ type: "local_lingo/upsert_user", display_name: displayName.trim(), default_language: this.language, daily_goal_points: 100 }); await this.load(); }
  render() {
    const rows = this.summary.filter((item) => item.language === this.language).map((item) => `<tr><td>${esc(item.display_name)}</td><td>${item.points_total}</td><td>${item.streak_current} day${item.streak_current === 1 ? "" : "s"}</td><td>${item.words_mastered}</td><td>${Math.min(100, Math.round((item.points_today / Math.max(1, item.daily_goal_points || 100)) * 100))}%</td></tr>`).join("");
    const content = rows ? `<table><thead><tr><th>Learner</th><th>XP</th><th>Streak</th><th>Mastered</th><th>Daily goal</th></tr></thead><tbody>${rows}</tbody></table>` : `<div class="empty"><p><strong>No learner profiles yet.</strong></p><p class="muted">Select ADD USER to create the first learner.</p></div>`;
    this.shadowRoot.innerHTML = `<style>${LL_STYLE}</style><ha-card><div class="wrap"><div class="progress-top"><h2>${esc(this._config.title || "Learner progress")}</h2><select id="language">${this.languages.map((item) => `<option value="${esc(item.code)}" ${item.code === this.language ? "selected" : ""}>${esc(item.name)}</option>`).join("")}</select><button id="add" class="secondary">ADD USER</button></div>${this.error ? `<div class="error">${esc(this.error)}</div>` : content}</div></ha-card>`;
    const language = this.shadowRoot.getElementById("language"); const add = this.shadowRoot.getElementById("add");
    if (language) language.onchange = (event) => { this.language = event.target.value; this.render(); };
    if (add) add.onclick = () => this.addUser();
  }
}
