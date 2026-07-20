import { LL_STYLE, esc, encoded, decoded, difficultyLabel } from "./local-lingo-shared.js";

export class LocalLingoLessonCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this.users = [];
    this.languages = [];
    this.user = null;
    this.language = "de";
    this.count = 10;
    this.difficulty = 1;
    this.session = null;
    this.answer = null;
    this.reviewQuestion = null;
    this.feedback = null;
    this.error = null;
    this.audioError = null;
    this.loading = false;
    this.tts = {};
  }

  static getStubConfig() {
    return { title: "Language Practice", default_language: "de", question_count: 10, difficulty: 1, tts: { mode: "browser", question: true, answers: true, auto_question: false, auto_answer: false, rate: 0.9 } };
  }

  static getConfigElement() { return document.createElement("local-lingo-lesson-card-editor"); }

  setConfig(config) {
    if (!config) throw new Error("Local Lingo card configuration is required");
    this._config = config;
    this.language = config.default_language || "de";
    this.count = Number(config.question_count || 10);
    this.difficulty = config.difficulty ?? 1;
    const tts = config.tts || {};
    this.tts = { mode: tts.mode || "browser", entityId: tts.entity_id || "", mediaPlayerId: tts.media_player_entity_id || "", question: tts.question !== false, answers: tts.answers !== false, autoQuestion: Boolean(tts.auto_question), autoAnswer: Boolean(tts.auto_answer), rate: Math.min(2, Math.max(0.5, Number(tts.rate || 0.9))) };
  }

  set hass(hass) { this._hass = hass; if (!this.started) { this.started = true; this.bootstrap(); } }
  disconnectedCallback() { if (window.speechSynthesis) window.speechSynthesis.cancel(); }
  getCardSize() { return 7; }
  getGridOptions() { return { columns: 12, min_columns: 6 }; }
  currentLanguage() { return this.languages.find((item) => item.code === this.language) || null; }
  currentUser() { return this.users.find((item) => item.user_id === this.user) || null; }
  syncFromSession() { if (!this.session) return; this.language = this.session.language || this.language; this.count = Number(this.session.question_count || this.count); this.difficulty = this.session.difficulty ?? this.difficulty; }

  async bootstrap() {
    this.loading = true; this.render();
    try {
      [this.users, this.languages] = await Promise.all([this._hass.callWS({ type: "local_lingo/list_users" }), this._hass.callWS({ type: "local_lingo/list_languages" })]);
      this.user = this._config.default_user || this.users[0]?.user_id || null;
      if (!this.users.some((item) => item.user_id === this.user)) this.user = this.users[0]?.user_id || null;
      if (!this.languages.some((item) => item.code === this.language)) this.language = this.languages[0]?.code || "de";
      if (this.user) { this.session = await this._hass.callWS({ type: "local_lingo/get_active_session", user_id: this.user }); this.syncFromSession(); }
      this.error = null;
    } catch (error) { this.error = error.message || String(error); }
    finally { this.loading = false; this.render(); }
  }

  async startLesson() {
    if (!this.user) return;
    this.loading = true; this.feedback = null; this.reviewQuestion = null; this.answer = null; this.error = null; this.render();
    try { this.session = await this._hass.callWS({ type: "local_lingo/start_lesson", user_id: this.user, language: this.language, question_count: this.count, difficulty: this.difficulty }); this.syncFromSession(); }
    catch (error) { this.error = error.message || String(error); }
    finally { this.loading = false; this.render(); if (!this.error && this.tts.autoQuestion) this.speakCurrentQuestion(); }
  }

  async submit() {
    if (!this.answer || !this.session || this.feedback) return;
    this.loading = true;
    const reviewedQuestion = this.session.question;
    const selectedAnswer = this.answer;
    this.render();
    try {
      const result = await this._hass.callWS({ type: "local_lingo/submit_answer", session_id: this.session.session_id, answer: selectedAnswer });
      this.reviewQuestion = reviewedQuestion; this.feedback = result; this.session = result.session; this.answer = selectedAnswer; this.error = null;
    } catch (error) { this.error = error.message || String(error); }
    finally { this.loading = false; this.render(); if (this.feedback && this.tts.autoAnswer) this.speak(this.feedback.answer_tts, this.feedback.answer_tts_language); }
  }

  advanceReview() {
    const wasCorrect = Boolean(this.feedback?.correct);
    this.feedback = null; this.reviewQuestion = null; this.answer = null; this.render();
    if ((!this.session?.completed || !wasCorrect) && this.tts.autoQuestion) this.speakCurrentQuestion();
  }

  async speak(text, language) {
    if (!text || this.tts.mode === "off") return;
    this.audioError = null;
    try {
      if (this.tts.mode === "home_assistant") {
        if (!this.tts.entityId || !this.tts.mediaPlayerId) throw new Error("Home Assistant TTS requires both a TTS entity and a media-player entity.");
        await this._hass.callService("tts", "speak", { media_player_entity_id: this.tts.mediaPlayerId, message: text, language: String(language || "").split("-")[0] || undefined, cache: true }, { entity_id: this.tts.entityId });
      } else {
        if (!("speechSynthesis" in window)) throw new Error("This browser does not support on-device speech synthesis.");
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text); utterance.lang = language || "en-US"; utterance.rate = this.tts.rate; window.speechSynthesis.speak(utterance);
      }
    } catch (error) { this.audioError = error.message || String(error); this.render(); }
  }

  speakCurrentQuestion() { const question = this.reviewQuestion || this.session?.question; if (question) this.speak(question.question_tts, question.question_tts_language); }

  renderSetup() {
    const userOptions = this.users.length ? this.users.map((item) => `<option value="${esc(item.user_id)}" ${item.user_id === this.user ? "selected" : ""}>${esc(item.display_name)}</option>`).join("") : '<option value="">No learners</option>';
    const languageOptions = this.languages.map((item) => `<option value="${esc(item.code)}" ${item.code === this.language ? "selected" : ""}>${esc(item.name)}</option>`).join("");
    return `<div class="setup-grid"><label class="field">LEARNER<select id="user" ${this.users.length ? "" : "disabled"}>${userOptions}</select></label><label class="field">LANGUAGE<select id="language">${languageOptions}</select></label><label class="field">PRACTICE LEVEL<select id="difficulty"><option value="1" ${String(this.difficulty) === "1" ? "selected" : ""}>Level 1 · Words</option><option value="2" ${String(this.difficulty) === "2" ? "selected" : ""}>Level 2 · Sentences</option><option value="mixed" ${String(this.difficulty) === "mixed" ? "selected" : ""}>Mixed practice</option></select></label><label class="field">LESSON LENGTH<select id="count">${[5,10,15].map((n) => `<option value="${n}" ${n === this.count ? "selected" : ""}>${n} questions</option>`).join("")}</select></label></div>`;
  }

  renderActiveHeader() { return `<div class="active-header"><span class="chip">${esc(this.currentUser()?.display_name || "Learner")}</span><span class="chip">${esc(this.currentLanguage()?.name || this.language)}</span><span class="chip">${esc(difficultyLabel(this.difficulty))}</span><span class="chip">${this.count} questions</span></div>`; }

  renderQuestion() {
    const review = Boolean(this.feedback && this.reviewQuestion);
    const question = review ? this.reviewQuestion : this.session?.question;
    if (!question) return "";
    const completedIndex = Number(this.session?.current_index || 0);
    const questionIndex = review && this.feedback.correct ? Math.max(0, completedIndex - 1) : completedIndex;
    const questionNumber = Math.min(this.count, questionIndex + 1);
    const pct = Math.round((completedIndex / Math.max(1, this.count)) * 100);
    const choices = (question.choices || []).map((choice) => {
      const selected = choice === this.answer;
      const correct = review && choice === this.feedback.correct_answer;
      const wrong = review && selected && !this.feedback.correct;
      const stateClass = correct ? "correct" : wrong ? "wrong" : selected ? "selected" : "";
      const spoken = question.choice_tts?.[choice] || choice;
      return `<div class="choice-row"><button class="choice-main ${stateClass}" data-answer="${esc(choice)}" ${review || this.loading ? "disabled" : ""}>${esc(choice)}</button>${this.tts.answers && this.tts.mode !== "off" ? `<button class="choice-speak" data-speak="${encoded(spoken)}" data-lang="${esc(question.choice_tts_language || "")}" aria-label="Hear ${esc(choice)}"><ha-icon icon="mdi:volume-high"></ha-icon></button>` : ""}</div>`;
    }).join("");
    const feedback = review ? `<div class="feedback ${this.feedback.correct ? "good" : "bad"}"><div class="feedback-title">${this.feedback.correct ? `Correct! +${this.feedback.points_awarded} XP` : "Not quite — review the correct answer."}</div><div class="feedback-answer">${esc(this.feedback.completed_text || this.feedback.correct_answer)}</div>${this.feedback.translation ? `<div class="feedback-translation">${esc(this.feedback.translation)}</div>` : ""}${this.tts.answers && this.tts.mode !== "off" ? `<div class="feedback-actions"><button class="speak-button" id="answer-speak" aria-label="Hear the correct answer"><ha-icon icon="mdi:volume-high"></ha-icon></button><span>Hear the complete answer</span></div>` : ""}</div>` : "";
    return `<div class="progress"><div style="width:${pct}%"></div></div><div class="lesson-meta"><span>Question ${questionNumber} of ${this.count}</span><span>${this.session?.points_earned || 0} XP this lesson</span></div><div class="instruction-row"><p class="instruction">${esc(question.instruction)}</p></div><div class="prompt-row"><div class="prompt">${esc(question.prompt)}</div>${this.tts.question && this.tts.mode !== "off" ? `<button class="speak-button" id="question-speak" aria-label="Hear the question"><ha-icon icon="mdi:volume-high"></ha-icon></button>` : ""}</div><div class="choices">${choices}</div>${feedback}${review ? `<button class="primary-action" id="continue">${this.feedback.correct ? "CONTINUE" : "TRY AGAIN"}</button>` : `<button class="primary-action" id="check" ${this.answer && !this.loading ? "" : "disabled"}>CHECK ANSWER</button>`}`;
  }

  render() {
    if (!this.shadowRoot) return;
    const active = Boolean(this.session || this.reviewQuestion);
    let body = "";
    if (this.error) body = `<div class="error">${esc(this.error)}</div>`;
    else if (this.loading && !this.session) body = '<p class="muted">Loading Local Lingo…</p>';
    else if (!this.users.length) body = `<h2>${esc(this._config.title || "Local Lingo")}</h2><div class="empty"><p><strong>No learner profiles yet.</strong></p><p class="muted">Use the Local Lingo progress card to add the first learner.</p></div>`;
    else if (this.feedback && this.reviewQuestion) body = `${this.renderActiveHeader()}${this.renderQuestion()}`;
    else if (this.session?.completed) { const attempts = this.session.correct_count + this.session.incorrect_count || 1; body = `${this.renderActiveHeader()}<div class="prompt">Lesson complete!</div><div class="stats"><span class="pill">+${this.session.points_earned} XP</span><span class="pill">${Math.round((this.session.correct_count / attempts) * 100)}% accuracy</span></div><button class="primary-action" id="start">START ANOTHER LESSON</button>`; }
    else if (!this.session) body = `<h2>${esc(this._config.title || "Local Lingo")}</h2><p class="muted">Choose a learner, language, practice level, and lesson length.</p><button class="primary-action" id="start">START LESSON</button>`;
    else body = `${this.renderActiveHeader()}${this.renderQuestion()}`;
    this.shadowRoot.innerHTML = `<style>${LL_STYLE}</style><ha-card><div class="wrap">${active ? "" : this.renderSetup()}${body}${this.audioError ? `<div class="audio-error">${esc(this.audioError)}</div>` : ""}</div></ha-card>`;
    this.bind();
  }

  bind() {
    const by = (id) => this.shadowRoot.getElementById(id);
    if (by("user")) by("user").onchange = async (event) => { this.user = event.target.value || null; this.feedback = null; this.reviewQuestion = null; this.answer = null; this.session = this.user ? await this._hass.callWS({ type: "local_lingo/get_active_session", user_id: this.user }) : null; this.syncFromSession(); this.render(); };
    if (by("language")) by("language").onchange = (event) => (this.language = event.target.value);
    if (by("difficulty")) by("difficulty").onchange = (event) => { this.difficulty = event.target.value === "mixed" ? "mixed" : Number(event.target.value); };
    if (by("count")) by("count").onchange = (event) => (this.count = Number(event.target.value));
    if (by("start")) by("start").onclick = () => this.startLesson();
    if (by("check")) by("check").onclick = () => this.submit();
    if (by("continue")) by("continue").onclick = () => this.advanceReview();
    if (by("question-speak")) by("question-speak").onclick = () => this.speakCurrentQuestion();
    if (by("answer-speak")) by("answer-speak").onclick = () => this.speak(this.feedback?.answer_tts, this.feedback?.answer_tts_language);
    this.shadowRoot.querySelectorAll(".choice-main").forEach((button) => { button.onclick = () => { this.answer = button.dataset.answer; this.render(); }; });
    this.shadowRoot.querySelectorAll(".choice-speak").forEach((button) => { button.onclick = (event) => { event.stopPropagation(); this.speak(decoded(button.dataset.speak), button.dataset.lang); }; });
  }
}
