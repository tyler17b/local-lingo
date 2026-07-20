const LL_COLORS = {
  green: "#58CC02",
  dark: "#46A302",
  blue: "#1CB0F6",
  red: "#FF4B4B",
  orange: "#FF9600",
  text: "#4B4B4B",
  border: "#E5E5E5",
  bg: "#F7F7F7",
};

export const LL_PROGRESS_EVENT = "local_lingo_progress_updated";

export const LL_STYLE = `
  :host {
    display: block;
    font-family: "Nunito", "Arial Rounded MT Bold", Arial, sans-serif;
    -webkit-tap-highlight-color: transparent;
  }
  * { box-sizing: border-box; }
  ha-card {
    border: 2px solid ${LL_COLORS.border};
    border-radius: 20px;
    box-shadow: 0 5px 0 #d8d8d8;
    background: var(--ha-card-background, #fff);
    color: var(--primary-text-color, ${LL_COLORS.text});
    overflow: hidden;
  }
  .wrap { padding: 20px; }
  h2 { margin: 0; line-height: 1.15; }
  button, select, input { font: inherit; touch-action: manipulation; }
  select, input {
    width: 100%; min-height: 52px; border: 2px solid ${LL_COLORS.border};
    border-radius: 14px; padding: 0 12px; background: var(--card-background-color, #fff);
    color: var(--primary-text-color, ${LL_COLORS.text}); font-weight: 800;
  }
  label.field { display: grid; gap: 6px; color: var(--secondary-text-color, #777); font-size: .82rem; font-weight: 900; }
  .setup-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }
  .active-header { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 8px; }
  .chip { padding: 8px 12px; border: 2px solid ${LL_COLORS.border}; border-radius: 999px; background: ${LL_COLORS.bg}; color: ${LL_COLORS.text}; font-size: .86rem; font-weight: 900; }
  button { min-height: 58px; border: 0; border-radius: 16px; padding: 12px 16px; background: ${LL_COLORS.green}; color: #fff; box-shadow: 0 5px 0 ${LL_COLORS.dark}; font-weight: 900; cursor: pointer; user-select: none; }
  button:active:not(:disabled) { transform: translateY(3px); box-shadow: 0 2px 0 ${LL_COLORS.dark}; }
  button:disabled { opacity: .48; cursor: default; }
  .primary-action { width: 100%; margin-top: 18px; min-height: 64px; }
  .secondary { background: ${LL_COLORS.blue}; box-shadow: 0 5px 0 #1899d6; }
  .progress { height: 14px; border-radius: 999px; background: ${LL_COLORS.border}; overflow: hidden; margin: 14px 0 8px; }
  .progress > div { height: 100%; background: ${LL_COLORS.green}; transition: width .2s ease; }
  .lesson-meta { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 18px; color: var(--secondary-text-color, #777); font-size: .9rem; font-weight: 900; }
  .instruction-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 8px; }
  .instruction { margin: 0; font-weight: 900; line-height: 1.4; }
  .prompt-row { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 10px; margin: 20px 0 24px; }
  .prompt { text-align: center; font-size: clamp(34px, 6vw, 58px); font-weight: 900; overflow-wrap: anywhere; }
  .speak-button { width: 54px; min-width: 54px; height: 54px; min-height: 54px; padding: 0; border-radius: 50%; background: ${LL_COLORS.blue}; box-shadow: 0 4px 0 #1899d6; display: inline-flex; align-items: center; justify-content: center; }
  .speak-button:active:not(:disabled) { box-shadow: 0 1px 0 #1899d6; }
  .speak-button ha-icon { --mdc-icon-size: 28px; }
  .choices { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
  .choice-row { display: grid; grid-template-columns: minmax(0, 1fr) 58px; gap: 8px; min-width: 0; }
  .choice-main { min-width: 0; min-height: 64px; background: var(--card-background-color, #fff); color: var(--primary-text-color, ${LL_COLORS.text}); border: 2px solid ${LL_COLORS.border}; box-shadow: 0 4px 0 #d8d8d8; overflow-wrap: anywhere; }
  .choice-main:active:not(:disabled) { box-shadow: 0 1px 0 #d8d8d8; }
  .choice-main.selected { border-color: ${LL_COLORS.blue}; background: #e9f8ff; }
  .choice-main.correct { border-color: ${LL_COLORS.green}; background: #e9ffd8; box-shadow: 0 4px 0 #b5df8a; }
  .choice-main.wrong { border-color: ${LL_COLORS.red}; background: #fff0f0; box-shadow: 0 4px 0 #efb6b6; }
  .choice-speak { min-width: 58px; min-height: 64px; padding: 0; background: ${LL_COLORS.blue}; box-shadow: 0 4px 0 #1899d6; }
  .choice-speak ha-icon { --mdc-icon-size: 27px; }
  .feedback { margin-top: 18px; padding: 16px; border-radius: 16px; font-weight: 900; }
  .feedback-title { font-size: 1.05rem; }
  .feedback-answer { margin-top: 8px; font-size: 1.25rem; }
  .feedback-translation { margin-top: 5px; color: var(--secondary-text-color, #666); font-size: .94rem; }
  .feedback-actions { display: flex; gap: 10px; align-items: center; margin-top: 12px; }
  .good { background: #e9ffd8; border: 2px solid ${LL_COLORS.green}; }
  .bad, .error { background: #fff0f0; border: 2px solid ${LL_COLORS.red}; }
  .error { border-radius: 12px; padding: 12px; }
  .audio-error { margin-top: 12px; padding: 10px; border: 2px solid ${LL_COLORS.orange}; border-radius: 12px; background: #fff8e8; font-weight: 800; }
  .muted { color: var(--secondary-text-color, #777); }
  .empty { padding: 20px; border: 2px dashed ${LL_COLORS.border}; border-radius: 14px; background: ${LL_COLORS.bg}; text-align: center; }
  .stats { display: flex; gap: 10px; flex-wrap: wrap; margin: 16px 0; }
  .pill { padding: 8px 12px; border: 2px solid ${LL_COLORS.border}; border-radius: 999px; background: ${LL_COLORS.bg}; font-weight: 900; }
  table { width: 100%; border-collapse: separate; border-spacing: 0 8px; }
  th { text-align: left; color: var(--secondary-text-color, #777); }
  td { padding: 12px; background: ${LL_COLORS.bg}; font-weight: 800; }
  td:first-child { border-radius: 12px 0 0 12px; }
  td:last-child { border-radius: 0 12px 12px 0; }
  .progress-top { display: grid; grid-template-columns: minmax(0, 1fr) minmax(150px, .65fr) auto; gap: 12px; align-items: center; margin-bottom: 18px; }
  @media (max-width: 720px) { .choices { grid-template-columns: 1fr; } .progress-top { grid-template-columns: 1fr 1fr; } .progress-top h2 { grid-column: 1 / -1; } }
  @media (max-width: 520px) { .wrap { padding: 16px; } .setup-grid { grid-template-columns: 1fr; } .lesson-meta { font-size: .82rem; } .prompt-row { grid-template-columns: 1fr; } .prompt-row .speak-button { justify-self: center; } .progress-top { grid-template-columns: 1fr; } table { font-size: .82rem; } }
`;

export const LL_EDITOR_STYLE = `
  :host { display: block; font-family: var(--paper-font-body1_-_font-family, sans-serif); }
  .editor { display: grid; gap: 14px; padding: 8px 0; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  label { display: grid; gap: 5px; font-weight: 600; }
  input, select { min-height: 42px; padding: 0 10px; }
  .check { display: flex; align-items: center; gap: 8px; }
  .check input { width: auto; min-height: 0; }
  .help { color: var(--secondary-text-color); font-size: .86rem; line-height: 1.35; }
  @media (max-width: 520px) { .grid { grid-template-columns: 1fr; } }
`;

export const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[char]);
export const encoded = (value) => encodeURIComponent(String(value ?? ""));
export const decoded = (value) => decodeURIComponent(value || "");
export const difficultyLabel = (value) => String(value) === "2" ? "Level 2 · Sentences" : String(value) === "mixed" ? "Mixed practice" : "Level 1 · Words";
