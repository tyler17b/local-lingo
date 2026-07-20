const LL_COLORS = {
  green: "#58CC02",
  dark: "#46A302",
  blue: "#1CB0F6",
  red: "#FF4B4B",
  text: "#4B4B4B",
  border: "#E5E5E5",
  bg: "#F7F7F7",
};

const LL_PROGRESS_EVENT = "local_lingo_progress_updated";

const LL_STYLE = `
  :host {
    display: block;
    font-family: "Nunito", "Arial Rounded MT Bold", Arial, sans-serif;
  }
  ha-card {
    border: 2px solid ${LL_COLORS.border};
    border-radius: 20px;
    box-shadow: 0 5px 0 #d8d8d8;
    background: #fff;
    color: ${LL_COLORS.text};
    overflow: hidden;
  }
  .wrap { padding: 18px; }
  .top {
    display: grid;
    grid-template-columns: 1fr 1fr auto;
    gap: 10px;
    align-items: center;
    margin-bottom: 14px;
  }
  select, input {
    min-height: 44px;
    border: 2px solid ${LL_COLORS.border};
    border-radius: 12px;
    padding: 0 10px;
    background: #fff;
    color: ${LL_COLORS.text};
    font: inherit;
    font-weight: 800;
  }
  button {
    min-height: 52px;
    border: 0;
    border-radius: 15px;
    padding: 10px 14px;
    background: ${LL_COLORS.green};
    color: #fff;
    box-shadow: 0 5px 0 ${LL_COLORS.dark};
    font: inherit;
    font-weight: 900;
    cursor: pointer;
  }
  button:active {
    transform: translateY(3px);
    box-shadow: 0 2px 0 ${LL_COLORS.dark};
  }
  button:disabled { opacity: .5; }
  .secondary {
    background: ${LL_COLORS.blue};
    box-shadow: 0 5px 0 #1899d6;
  }
  .progress {
    height: 14px;
    border-radius: 999px;
    background: ${LL_COLORS.border};
    overflow: hidden;
    margin: 12px 0 8px;
  }
  .progress div {
    height: 100%;
    background: ${LL_COLORS.green};
    transition: width .2s ease;
  }
  .lesson-meta {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 18px;
    color: #777;
    font-size: .9rem;
    font-weight: 800;
  }
  .instruction {
    font-weight: 800;
    line-height: 1.45;
  }
  .prompt {
    text-align: center;
    font-size: clamp(30px, 6vw, 54px);
    font-weight: 900;
    margin: 20px 0;
  }
  .muted { color: #777; }
  .empty {
    padding: 18px;
    border: 2px dashed ${LL_COLORS.border};
    border-radius: 14px;
    background: ${LL_COLORS.bg};
    text-align: center;
  }
  .choices {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }
  .choice {
    background: #fff;
    color: ${LL_COLORS.text};
    border: 2px solid ${LL_COLORS.border};
    box-shadow: 0 4px 0 #d8d8d8;
  }
  .choice.selected {
    border-color: ${LL_COLORS.blue};
    background: #e9f8ff;
  }
  .feedback {
    margin: 16px 0;
    padding: 14px;
    border-radius: 14px;
    font-weight: 900;
  }
  .good {
    background: #e9ffd8;
    border: 2px solid ${LL_COLORS.green};
  }
  .bad, .error {
    background: #fff0f0;
    border: 2px solid ${LL_COLORS.red};
  }
  .error {
    border-radius: 12px;
    padding: 12px;
  }
  .stats {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 14px 0;
  }
  .pill {
    padding: 7px 11px;
    border: 2px solid ${LL_COLORS.border};
    border-radius: 999px;
    background: ${LL_COLORS.bg};
    font-weight: 900;
  }
  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 8px;
  }
  th {
    text-align: left;
    color: #777;
  }
  td {
    padding: 11px;
    background: ${LL_COLORS.bg};
    font-weight: 800;
  }
  td:first-child { border-radius: 12px 0 0 12px; }
  td:last-child { border-radius: 0 12px 12px 0; }
  @media (max-width: 650px) {
    .top { grid-template-columns: 1fr 1fr; }
    .choices { grid-template-columns: 1fr; }
    table { font-size: .84rem; }
  }
`;

const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (char) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[char],
  );

class LocalLingoLessonCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this.users = [];
    this.languages = [];
    this.user = null;
    this.language = "de";
    this.count = 10;
    this.session = null;
    this.answer = null;
    this.feedback = null;
    this.error = null;
    this.loading = false;
  }

  setConfig(config) {
    this._config = config || {};
    this.language = config.default_language || "de";
    this.count = Number(config.question_count || 10);
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.started) {
      this.started = true;
      this.bootstrap();
    }
  }

  getCardSize() {
    return 6;
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6 };
  }

  async bootstrap() {
    this.loading = true;
    this.render();
    try {
      [this.users, this.languages] = await Promise.all([
        this._hass.callWS({ type: "local_lingo/list_users" }),
        this._hass.callWS({ type: "local_lingo/list_languages" }),
      ]);
      this.user = this._config.default_user || this.users[0]?.user_id || null;
      if (!this.users.some((item) => item.user_id === this.user)) {
        this.user = this.users[0]?.user_id || null;
      }
      if (!this.languages.some((item) => item.code === this.language)) {
        this.language = this.languages[0]?.code || "de";
      }
      if (this.user) {
        this.session = await this._hass.callWS({
          type: "local_lingo/get_active_session",
          user_id: this.user,
        });
      }
    } catch (error) {
      this.error = error.message || String(error);
    } finally {
      this.loading = false;
      this.render();
    }
  }

  async startLesson() {
    if (!this.user) return;
    this.loading = true;
    this.feedback = null;
    this.answer = null;
    this.render();
    try {
      this.session = await this._hass.callWS({
        type: "local_lingo/start_lesson",
        user_id: this.user,
        language: this.language,
        question_count: this.count,
      });
    } catch (error) {
      this.error = error.message || String(error);
    } finally {
      this.loading = false;
      this.render();
    }
  }

  async submit() {
    if (!this.answer || !this.session) return;
    this.loading = true;
    this.render();
    try {
      const result = await this._hass.callWS({
        type: "local_lingo/submit_answer",
        session_id: this.session.session_id,
        answer: this.answer,
      });
      this.feedback = result;
      this.session = result.session;
      this.answer = null;
    } catch (error) {
      this.error = error.message || String(error);
    } finally {
      this.loading = false;
      this.render();
    }
  }

  render() {
    if (!this.shadowRoot) return;

    const options = (items, value, key, label) =>
      items
        .map(
          (item) =>
            `<option value="${esc(item[key])}" ${
              item[key] === value ? "selected" : ""
            }>${esc(item[label])}</option>`,
        )
        .join("");

    const userOptions = this.users.length
      ? options(this.users, this.user, "user_id", "display_name")
      : '<option value="">No learners</option>';

    let body = "";

    if (this.error) {
      body = `<div class="error">${esc(this.error)}</div>`;
    } else if (this.loading && !this.session) {
      body = '<p class="muted">Loading Local Lingo…</p>';
    } else if (!this.users.length) {
      body = `
        <h2>${esc(this._config.title || "Local Lingo")}</h2>
        <div class="empty">
          <p><strong>No learner profiles yet.</strong></p>
          <p class="muted">Use the Local Lingo progress card to add the first learner.</p>
        </div>`;
    } else if (!this.session) {
      body = `
        <h2>${esc(this._config.title || "Local Lingo")}</h2>
        <p class="muted">Choose a learner and language, then start a short lesson.</p>
        <button id="start">START LESSON</button>`;
    } else if (this.session.completed) {
      const attempts =
        this.session.correct_count + this.session.incorrect_count || 1;
      body = `
        <div class="prompt">Lesson complete!</div>
        <div class="stats">
          <span class="pill">+${this.session.points_earned} XP</span>
          <span class="pill">${Math.round(
            (this.session.correct_count / attempts) * 100,
          )}% accuracy</span>
        </div>
        <button id="start">START ANOTHER LESSON</button>`;
    } else {
      const q = this.session.question || {};
      const completed = this.session.current_index;
      const questionNumber = Math.min(
        this.session.question_count,
        completed + 1,
      );
      const pct = Math.round(
        (completed / this.session.question_count) * 100,
      );
      const choices = (q.choices || [])
        .map(
          (choice) =>
            `<button class="choice ${
              choice === this.answer ? "selected" : ""
            }" data-answer="${esc(choice)}">${esc(choice)}</button>`,
        )
        .join("");
      const feedback = this.feedback
        ? `<div class="feedback ${
            this.feedback.correct ? "good" : "bad"
          }">${
            this.feedback.correct
              ? `Correct! +${this.feedback.points_awarded} XP`
              : `Not quite. Correct answer: ${esc(
                  this.feedback.correct_answer,
                )}`
          }</div>`
        : "";

      body = `
        <div class="progress"><div style="width:${pct}%"></div></div>
        <div class="lesson-meta">
          <span>Question ${questionNumber} of ${this.session.question_count}</span>
          <span>${this.session.points_earned} XP this lesson</span>
        </div>
        <p class="instruction">${esc(q.instruction)}</p>
        <div class="prompt">${esc(q.prompt)}</div>
        <div class="choices">${choices}</div>
        ${feedback}
        <button id="check" ${
          this.answer && !this.loading ? "" : "disabled"
        }>CHECK</button>`;
    }

    this.shadowRoot.innerHTML = `
      <style>${LL_STYLE}</style>
      <ha-card>
        <div class="wrap">
          <div class="top">
            <select id="user" ${this.users.length ? "" : "disabled"}>
              ${userOptions}
            </select>
            <select id="language">
              ${options(this.languages, this.language, "code", "name")}
            </select>
            <select id="count">
              ${[5, 10, 15]
                .map(
                  (n) =>
                    `<option value="${n}" ${
                      n === this.count ? "selected" : ""
                    }>${n} questions</option>`,
                )
                .join("")}
            </select>
          </div>
          ${body}
        </div>
      </ha-card>`;
    this.bind();
  }

  bind() {
    const by = (id) => this.shadowRoot.getElementById(id);
    if (by("user")) {
      by("user").onchange = async (event) => {
        this.user = event.target.value || null;
        this.session = this.user
          ? await this._hass.callWS({
              type: "local_lingo/get_active_session",
              user_id: this.user,
            })
          : null;
        this.render();
      };
    }
    if (by("language")) {
      by("language").onchange = (event) => {
        this.language = event.target.value;
      };
    }
    if (by("count")) {
      by("count").onchange = (event) => {
        this.count = Number(event.target.value);
      };
    }
    if (by("start")) by("start").onclick = () => this.startLesson();
    if (by("check")) by("check").onclick = () => this.submit();
    this.shadowRoot.querySelectorAll(".choice").forEach((button) => {
      button.onclick = () => {
        this.answer = button.dataset.answer;
        this.feedback = null;
        this.render();
      };
    });
  }
}

class LocalLingoProgressCard extends HTMLElement {
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

  setConfig(config) {
    this._config = config || {};
    this.language = config.language || "de";
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.started) {
      this.started = true;
      this.load();
      this.subscribeProgress();
    }
  }

  disconnectedCallback() {
    if (this._unsubscribeProgress) {
      this._unsubscribeProgress();
      this._unsubscribeProgress = null;
    }
  }

  getCardSize() {
    return 5;
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6 };
  }

  async subscribeProgress() {
    if (!this._hass?.connection || this._unsubscribeProgress) return;
    this._unsubscribeProgress = await this._hass.connection.subscribeEvents(
      () => this.scheduleRefresh(),
      LL_PROGRESS_EVENT,
    );
  }

  scheduleRefresh() {
    if (this._refreshPending) return;
    this._refreshPending = true;
    queueMicrotask(async () => {
      try {
        await this.load();
      } finally {
        this._refreshPending = false;
      }
    });
  }

  async load() {
    if (!this._hass) return;
    try {
      [this.summary, this.languages] = await Promise.all([
        this._hass.callWS({ type: "local_lingo/get_progress_summary" }),
        this._hass.callWS({ type: "local_lingo/list_languages" }),
      ]);
      if (!this.languages.some((item) => item.code === this.language)) {
        this.language = this.languages[0]?.code || "de";
      }
      this.error = null;
    } catch (error) {
      this.error = error.message || String(error);
    }
    this.render();
  }

  async addUser() {
    const displayName = window.prompt("New learner name");
    if (!displayName?.trim()) return;
    await this._hass.callWS({
      type: "local_lingo/upsert_user",
      display_name: displayName.trim(),
      default_language: this.language,
      daily_goal_points: 100,
    });
    await this.load();
  }

  render() {
    const rows = this.summary
      .filter((item) => item.language === this.language)
      .map(
        (item) =>
          `<tr>
            <td>${esc(item.display_name)}</td>
            <td>${item.points_total}</td>
            <td>${item.streak_current} day${
              item.streak_current === 1 ? "" : "s"
            }</td>
            <td>${item.words_mastered}</td>
            <td>${Math.min(
              100,
              Math.round(
                (item.points_today /
                  Math.max(1, item.daily_goal_points || 100)) *
                  100,
              ),
            )}%</td>
          </tr>`,
      )
      .join("");

    const content = rows
      ? `<table>
          <thead>
            <tr>
              <th>Learner</th>
              <th>XP</th>
              <th>Streak</th>
              <th>Mastered</th>
              <th>Daily goal</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>`
      : `<div class="empty">
          <p><strong>No learner profiles yet.</strong></p>
          <p class="muted">Select ADD USER to create the first learner.</p>
        </div>`;

    this.shadowRoot.innerHTML = `
      <style>${LL_STYLE}</style>
      <ha-card>
        <div class="wrap">
          <div class="top">
            <h2>${esc(this._config.title || "Learner progress")}</h2>
            <select id="language">
              ${this.languages
                .map(
                  (item) =>
                    `<option value="${esc(item.code)}" ${
                      item.code === this.language ? "selected" : ""
                    }>${esc(item.name)}</option>`,
                )
                .join("")}
            </select>
            <button id="add" class="secondary">ADD USER</button>
          </div>
          ${this.error ? `<div class="error">${esc(this.error)}</div>` : content}
        </div>
      </ha-card>`;

    const lang = this.shadowRoot.getElementById("language");
    const add = this.shadowRoot.getElementById("add");
    if (lang) {
      lang.onchange = (event) => {
        this.language = event.target.value;
        this.render();
      };
    }
    if (add) add.onclick = () => this.addUser();
  }
}

if (!customElements.get("local-lingo-lesson-card")) {
  customElements.define("local-lingo-lesson-card", LocalLingoLessonCard);
}
if (!customElements.get("local-lingo-progress-card")) {
  customElements.define("local-lingo-progress-card", LocalLingoProgressCard);
}

window.customCards = window.customCards || [];
window.customCards.push(
  {
    type: "local-lingo-lesson-card",
    name: "Local Lingo Lesson Card",
    description:
      "Local German and Spanish lessons with learner profiles and points.",
  },
  {
    type: "local-lingo-progress-card",
    name: "Local Lingo Progress Card",
    description: "Progress by learner and language.",
  },
);
