// Cucu replay-view player — a single Lit web component that owns the entire view: navigation,
// playback engine, timeline rendering, screenshot carousel, and the cucu/browser/stdout/stderr/
// errors log panels. Per-scenario data is read from the inline JSON island at #replay-data.
//
// Shadow DOM gives us:
//   - scoped styles (no global replay.css)
//   - upgrade-over-server-tag pattern (template emits <cucu-replay-app></cucu-replay-app> and we
//     render everything inside the shadow root)
//
// The light DOM around us still owns: the inline theme-init script (must run before paint), the
// `.container` wrapping override (in the small global <style>), and the JSON data island.
import { LitElement, html, css, nothing } from "./lit-3.3.2.min.js";

// =====================================================================================
// Helpers
// =====================================================================================

function pad(n, w) {
  let s = String(n);
  while (s.length < (w || 2)) s = "0" + s;
  return s;
}

function formatPlayheadTime(epochMs) {
  const d = new Date(epochMs);
  return (
    d.getFullYear() +
    "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
    " " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()) +
    "." + pad(d.getMilliseconds(), 3) + "000"
  );
}

// Convert an HTML string (e.g. pre-escaped ANSI-coloured cucu output) into a DocumentFragment
// that Lit can embed as a child. A fresh fragment is returned each call so re-renders work.
function rawHtml(s) {
  const tmpl = document.createElement("template");
  tmpl.innerHTML = s;
  return tmpl.content.cloneNode(true);
}

function stepFrameCount(s) {
  return Math.max(1, s.screenshots.length);
}

// =====================================================================================
// Styles — ported from replay.css verbatim, scoped to the component's shadow root
// =====================================================================================

const STYLES = css`
  :host {
    display: block;
    width: 100%;
    background: var(--vp-bg);
    color: var(--vp-text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }

  /* NAV */
  #vp-nav {
    background: var(--vp-surface);
    border-bottom: 1px solid var(--vp-border);
    padding: 8px 16px;
    display: flex; align-items: center; gap: 10px;
    position: sticky; top: 0; z-index: 1000; flex-wrap: wrap;
  }
  #vp-nav a { color: var(--vp-link); text-decoration: none; font-size: 13px; }
  #vp-nav a:hover { color: var(--vp-link-hover); text-decoration: underline; }
  .vp-sep { color: var(--vp-border); user-select: none; }
  .vp-nav-right { margin-left: auto; display: flex; align-items: center; gap: 10px; }
  .vp-meta { color: var(--vp-text3); font-size: 12px; font-family: monospace; white-space: nowrap; }

  /* Logs dropdown */
  #log-menu-wrap { position: relative; display: inline-block; }
  #log-dd {
    display: none; position: absolute; top: calc(100% + 6px); left: 0;
    background: var(--vp-surface); border: 1px solid var(--vp-border); border-radius: 6px;
    min-width: 200px; z-index: 200; padding: 4px 0;
    box-shadow: 0 8px 24px var(--vp-shadow);
  }
  #log-dd.open { display: block; }
  #log-dd a { display: block; padding: 6px 14px; color: var(--vp-link); font-size: 12px; text-decoration: none; }
  #log-dd a:hover { background: var(--vp-inset); }

  /* Theme toggle */
  #theme-toggle {
    background: transparent; border: 1px solid var(--vp-border); color: var(--vp-text2);
    padding: 3px 8px; border-radius: 4px; cursor: pointer; font-size: 14px; line-height: 1.4;
    transition: background 0.12s, color 0.12s, border-color 0.12s;
  }
  #theme-toggle:hover { color: var(--vp-text); border-color: var(--vp-link); }

  /* HEADER */
  #vp-header { background: var(--vp-surface); border-bottom: 1px solid var(--vp-border); padding: 10px 20px; }
  .vp-feature-label { color: var(--vp-text3); font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }
  .vp-feature-row   { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 4px; }
  .vp-feature-name  { color: var(--vp-text2); font-size: 13px; }
  .vp-feature-name a { color: var(--vp-link); text-decoration: none; }
  .vp-feature-name a:hover { text-decoration: underline; }
  .vp-mht-link { font-size: 12px; white-space: nowrap; flex-shrink: 0; }
  .vp-mht-link a { color: var(--vp-text3); text-decoration: none; }
  .vp-mht-link a:hover { color: var(--vp-link); text-decoration: underline; }
  .vp-scenario-name { color: var(--vp-text);  font-size: 17px; font-weight: 600; margin-bottom: 4px; }
  .vp-tags          { color: var(--vp-text3); font-size: 11px; font-family: monospace; }

  /* STAGE */
  #vp-stage {
    background: var(--vp-stage); height: 520px;
    display: flex; align-items: center; justify-content: center;
    position: relative; overflow: hidden; transition: background 0.2s;
  }
  #stage-resize-handle {
    height: 5px; background: transparent; cursor: ns-resize; flex-shrink: 0;
    border-top: 1px solid var(--vp-border);
  }
  #stage-resize-handle:hover, #stage-resize-handle.dragging { background: var(--vp-accent); }
  .step-frame {
    width: 100%; height: 100%;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 0 32px;
  }
  .stage-screenshots { display: flex; flex-direction: column; align-items: center; width: 100%; height: 100%; justify-content: center; }
  .screenshot-wrapper { display: none; position: relative; max-height: 100%; }
  .screenshot-wrapper.active { display: inline-flex; align-items: center; justify-content: center; max-height: 100%; }
  .stage-img { max-height: 100%; max-width: 100%; object-fit: contain; border-radius: 6px; box-shadow: 0 8px 32px var(--vp-stage-shadow); display: block; }
  .highlight-overlay {
    position: absolute; pointer-events: none;
    border: 2px solid rgba(255, 80, 80, 0.9); border-radius: 3px;
    box-shadow: 0 0 0 2px rgba(255,80,80,0.2), inset 0 0 0 1px rgba(255,80,80,0.15);
  }
  :host(.hide-highlights) .highlight-overlay { display: none; }
  #step-pic-nav {
    display: inline-flex; align-items: center; gap: 3px;
    background: var(--vp-inset); border: 1px solid var(--vp-border); border-radius: 6px;
    padding: 4px 8px; font-size: 12px; color: var(--vp-text); white-space: nowrap; font-family: monospace;
  }
  #step-pic-nav.disabled { opacity: 0.35; pointer-events: none; }
  .step-pic-nav-label { color: var(--vp-text2); margin-right: 2px; }
  .step-pic-nav-btn { background: transparent; border: none; color: var(--vp-text); cursor: pointer; padding: 0 2px; font-size: 11px; line-height: 1; }
  .step-pic-nav-btn:hover { color: var(--vp-link); }
  .no-screenshot-display { text-align: center; padding: 40px 20px; max-width: 700px; }
  .no-screenshot-display .step-line {
    display: flex; align-items: baseline; justify-content: center; flex-wrap: wrap; gap: 0.4em; line-height: 1.4;
  }
  .no-screenshot-display .step-keyword-large { color: var(--vp-text2); font-size: 20px; font-weight: bold; font-family: monospace; }
  .no-screenshot-display .step-keyword-large.status-passed   { color: var(--vp-passed); }
  .no-screenshot-display .step-keyword-large.status-failed,
  .no-screenshot-display .step-keyword-large.status-error    { color: var(--vp-failed); }
  .no-screenshot-display .step-keyword-large.status-skipped,
  .no-screenshot-display .step-keyword-large.status-untested { color: var(--vp-untested); }
  .no-screenshot-display .step-name-large { color: var(--vp-text); font-size: 24px; }
  .no-screenshot-display .step-skipped-label { font-size: 20px; font-weight: bold; font-family: monospace; margin-bottom: 6px; }
  .no-screenshot-display .step-skipped-label.status-skipped { color: var(--vp-untested); }
  .substep-prefix { color: var(--vp-text3); }
  .no-screenshot-display .step-detail-pre {
    color: var(--vp-text2); font-family: monospace; font-size: 13px; margin-top: 20px; text-align: left;
    background: var(--vp-surface); padding: 12px 16px; border-radius: 6px; white-space: pre-wrap;
    border: 1px solid var(--vp-border); max-width: 600px;
  }
  .stage-nav-btn {
    position: absolute; top: 50%; transform: translateY(-50%);
    background: var(--vp-overlay); border: 1px solid var(--vp-border);
    color: var(--vp-text); font-size: 22px; padding: 16px 12px; border-radius: 6px;
    cursor: pointer; opacity: 0; transition: opacity 0.2s, background 0.15s; z-index: 10;
  }
  #vp-stage:hover .stage-nav-btn { opacity: 1; }
  .stage-nav-btn:hover { background: var(--vp-overlay); filter: brightness(1.2); }
  #stage-btn-prev { left: 12px; }
  #stage-btn-next { right: 12px; }

  /* STEP INFO BAR */
  #vp-step-info {
    background: var(--vp-surface);
    border-top: 1px solid var(--vp-border); border-bottom: 1px solid var(--vp-border);
    padding: 10px 16px; display: flex; align-items: center; gap: 12px; min-height: 48px;
  }
  #step-num-badge {
    display: inline-flex; align-items: center; gap: 3px;
    background: var(--vp-inset); border: 1px solid var(--vp-border); border-radius: 6px;
    padding: 4px 8px; font-size: 12px; color: var(--vp-text); white-space: nowrap; font-family: monospace;
  }
  .step-nav-label { color: var(--vp-text2); margin-right: 2px; }
  .step-nav-btn { background: transparent; border: none; color: var(--vp-text); cursor: pointer; padding: 0 2px; font-size: 11px; line-height: 1; }
  .step-nav-btn:hover:not(:disabled) { color: var(--vp-link); }
  .step-nav-btn:disabled { opacity: 0.3; cursor: not-allowed; }
  #step-timing-text { color: var(--vp-text3); font-size: 12px; white-space: nowrap; font-family: monospace; margin-left: auto; }
  #pic-caption { color: var(--vp-text2); font-size: 12px; font-style: italic; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .status-pill {
    padding: 3px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
    white-space: nowrap; display: inline-block; font-family: monospace;
    background: var(--vp-inset); color: var(--vp-text); border: 1px solid var(--vp-border);
  }
  .status-pill.disabled { opacity: 0.4; }
  .ctrl-btn {
    background: transparent; border: 1px solid var(--vp-border); color: var(--vp-text);
    padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 14px; line-height: 1;
    transition: background 0.12s, border-color 0.12s; flex-shrink: 0;
  }
  .ctrl-btn:hover:not(:disabled) { background: var(--vp-inset); border-color: var(--vp-link); }
  .ctrl-btn:disabled { opacity: 0.3; cursor: not-allowed; }
  #btn-play-pause {
    background: var(--vp-accent); border-color: var(--vp-accent);
    color: #fff; font-size: 15px; padding: 4px 14px; font-weight: bold;
  }
  #btn-play-pause:hover:not(:disabled) { background: var(--vp-accent-hover); border-color: var(--vp-accent-hover); }

  /* TIMELINE */
  #timeline-track {
    flex: 1; position: relative; height: 14px; background: var(--vp-bg);
    border: 1px solid var(--vp-border); border-radius: 3px; cursor: pointer; overflow: visible; align-self: center;
  }
  .step-bar {
    position: absolute; top: 2px; height: calc(100% - 4px);
    border-radius: 2px; cursor: pointer; min-width: 3px;
    opacity: 0.72; z-index: 5; box-sizing: border-box;
    transition: top 0.1s, height 0.1s, opacity 0.1s;
  }
  .step-bar:hover { opacity: 1; top: 1px; height: calc(100% - 2px); z-index: 15; }
  .step-bar.active {
    opacity: 1; top: 0; height: 100%; border-radius: 3px; z-index: 20;
    box-shadow: 0 0 0 2px var(--vp-bg), 0 0 0 3px currentColor;
  }
  .step-bar                  { background: var(--vp-link);     color: var(--vp-link); }
  .step-bar.status-passed    { background: var(--vp-passed);   color: var(--vp-passed); }
  .step-bar.status-failed,
  .step-bar.status-error     { background: var(--vp-failed);   color: var(--vp-failed); }
  .step-bar.status-skipped,
  .step-bar.status-untested  { background: var(--vp-untested); color: var(--vp-untested); }
  .step-bar.heading          { background: var(--vp-text);     color: var(--vp-text);  opacity: 1; }
  #timeline-playhead {
    position: absolute; top: -3px; bottom: -3px; width: 2px;
    background: var(--vp-text); border-radius: 1px;
    pointer-events: none; z-index: 30; left: 0%; transform: translateX(-50%);
  }
  .panel-header-track {
    flex: 1; position: relative; height: 14px; background: var(--vp-bg);
    border: 1px solid var(--vp-border); border-radius: 3px; cursor: pointer; overflow: visible; align-self: center;
  }
  .tl-step-bar {
    position: absolute; top: 0; height: 100%; border-radius: 1px;
    pointer-events: none; min-width: 2px; background: var(--vp-link); opacity: 0.55;
  }
  .pics-tick {
    position: absolute; top: -1px; height: calc(100% + 2px); width: 2px;
    background: var(--vp-link); opacity: 0.95; border-radius: 1px; pointer-events: none;
  }
  .pics-tick.pics-tick-passed    { background: var(--vp-passed); }
  .pics-tick.pics-tick-failed,
  .pics-tick.pics-tick-error     { background: var(--vp-failed); }
  .pics-tick.pics-tick-skipped,
  .pics-tick.pics-tick-untested  { background: var(--vp-untested); opacity: 0.7; }
  .tl-tick { position: absolute; top: -1px; height: calc(100% + 2px); border-radius: 1px; pointer-events: none; }
  .tl-tick.tl-info    { width: 1px; background: var(--vp-link);   opacity: 0.55; }
  .tl-tick.tl-warning { width: 2px; background: #e87d0d;          opacity: 0.85; }
  .tl-tick.tl-error   { width: 2px; background: var(--vp-failed); opacity: 0.95; }
  .tl-cursor {
    position: absolute; top: -4px; bottom: -4px; width: 2px;
    background: var(--vp-link); border-radius: 1px;
    pointer-events: none; z-index: 30; left: 0%; transform: translateX(-50%);
  }

  /* LOG PANELS */
  .vp-log-panel { border-top: 1px solid var(--vp-border); }
  .vp-log-header {
    background: var(--vp-surface); border-bottom: 1px solid var(--vp-border);
    padding: 7px 16px; display: flex; align-items: center; gap: 8px;
    font-size: 12px; color: var(--vp-text2); user-select: none;
  }
  .log-toggle-area {
    display: flex; align-items: center; gap: 8px; cursor: pointer;
    margin: -7px 0 -7px -16px; padding: 7px 8px 7px 16px;
  }
  .log-toggle-area:hover { background: var(--vp-inset); }
  .vp-log-header .log-title { font-weight: 500; color: var(--vp-text); width: 64px; flex-shrink: 0; }
  .vp-log-header .log-count { color: var(--vp-text3); font-size: 11px; font-family: monospace; }
  .log-collapse-chevron { font-size: 22px; color: var(--vp-text3); transition: transform 0.15s; flex-shrink: 0; width: 20px; text-align: center; line-height: 1; }
  .vp-log-panel.collapsed .log-collapse-chevron { transform: rotate(-90deg); }
  .vp-log-panel.collapsed .vp-log-body { display: none; }
  .log-follow-label, .log-follow-spacer {
    display: flex; align-items: center; gap: 4px;
    width: 80px; flex-shrink: 0; margin-left: auto; color: var(--vp-text2); font-size: 11px;
  }
  .log-follow-label { cursor: pointer; }
  .log-follow-label input { cursor: pointer; accent-color: var(--vp-accent); }
  .vp-log-resize {
    height: 5px; background: transparent; cursor: ns-resize;
    border-bottom: 1px solid var(--vp-border); transition: background 0.1s;
  }
  .vp-log-resize:hover, .vp-log-resize.dragging { background: var(--vp-accent); }
  .vp-log-content {
    height: 200px; overflow-y: auto; background: var(--vp-bg);
    font-family: monospace; font-size: 11.5px; line-height: 1.55; padding: 2px 0;
  }
  .log-line {
    padding: 0 16px; white-space: pre-wrap; word-break: break-all;
    color: var(--vp-text3); border-left: 2px solid transparent;
  }
  .log-line.log-current { background: var(--vp-inset); color: var(--vp-text); border-left-color: var(--vp-accent); }
  .log-step-group { border-top: 1px solid var(--vp-border); }
  .log-step-group:first-child { border-top: none; }
  .log-step-label {
    padding: 3px 16px; font-size: 10.5px; color: var(--vp-text3);
    background: var(--vp-surface); position: sticky; top: 0; z-index: 1;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .log-step-group.step-current .log-step-label { color: var(--vp-accent); background: var(--vp-inset); }
  .log-step-group.step-current .log-line { color: var(--vp-text); }
  .stderr-line { color: #e87d0d; }
  .error-line  { color: var(--vp-failed); }
  .browser-log-line.bl-warning { color: #e87d0d; }
  .browser-log-line.bl-error   { color: var(--vp-failed); }

  /* Steps panel */
  .steps-row { cursor: pointer; }
  .steps-row:hover .log-line { background: var(--vp-inset); }
  #vp-steps-content .log-step-group.step-current .log-line {
    background: var(--vp-inset); border-left-color: var(--vp-accent);
  }
  #vp-steps-content .log-step-group.step-previous .log-line {
    background: var(--vp-surface); border-left-color: var(--vp-text3); opacity: 0.85;
  }
  .steps-kw { font-weight: bold; font-family: monospace; flex-shrink: 0; min-width: 6.5ch; }
  .steps-passed   { color: var(--vp-passed); }
  .steps-failed   { color: var(--vp-failed); }
  .steps-error    { color: var(--vp-failed); }
  .steps-skipped  { color: var(--vp-untested); }
  .steps-untested { color: var(--vp-untested); }
  .steps-substep  { padding-left: 28px; }
  .steps-heading .steps-kw,
  .steps-heading .steps-name { color: var(--vp-text3); font-weight: bold; }
  #steps-breadcrumb {
    background: var(--vp-surface); border-bottom: 1px solid var(--vp-border);
    font-family: monospace; font-size: 11.5px; line-height: 1.55;
    color: var(--vp-text); font-weight: bold;
  }
  #steps-breadcrumb:empty { display: none; }
  #steps-breadcrumb .log-line { padding: 2px 16px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  #vp-steps-content { min-height: calc(11.5px * 1.35 + 2px); }
  #vp-steps-content .log-line {
    display: flex; align-items: baseline; white-space: nowrap; overflow: hidden;
    padding: 1px 8px; line-height: 1.35;
  }
  #vp-steps-content .steps-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

  /* ANSI colours inside cucu log lines */
  .log-line .ansi-bold    { font-weight: bold; }
  .log-line .ansi-black   { color: var(--vp-text3); }
  .log-line .ansi-red     { color: var(--vp-failed); }
  .log-line .ansi-green   { color: var(--vp-passed); }
  .log-line .ansi-yellow  { color: var(--vp-heading); }
  .log-line .ansi-blue    { color: var(--vp-link); }
  .log-line .ansi-magenta { color: #bc8cff; }
  .log-line .ansi-cyan    { color: #39c5cf; }
  .log-line .ansi-white   { color: var(--vp-text); }
  .log-line .ansi-gray    { color: var(--vp-text2); }
`;

// =====================================================================================
// The component
// =====================================================================================

const THEME_CYCLE = ["auto", "light", "dark"];
const THEME_ICONS = { auto: "🖥", light: "☀", dark: "🌙" };
const THEME_TITLES = {
  auto: "Theme: auto (follows system)",
  light: "Theme: light",
  dark: "Theme: dark",
};

// `STYLES` would normally be installed via Lit's `static styles`, but that requires shadow DOM.
// Cucu's fuzzy.find uses jQuery against `document.body`, which can't pierce shadow roots — so we
// render into light DOM and emit the styles as a single <style> child instead. Same scoping
// achieved via specific selectors; cost is the styles being part of the DOM tree once.
const STYLES_TEXT = STYLES.toString();

class CucuReplayApp extends LitElement {
  static properties = {
    theme: { state: true },
    currentTimeSec: { state: true },
    shownStepIdx: { state: true },
    shownImgIdx: { state: true },
    isPlaying: { state: true },
    highlightVisible: { state: true },
    browserFollowing: { state: true },
    logsDropdownOpen: { state: true },
    _tick: { state: true }, // bumped to invalidate non-state object mutations
  };

  constructor() {
    super();
    this.theme = this._readTheme();
    this.currentTimeSec = 0;
    this.shownStepIdx = -1;
    this.shownImgIdx = -1;
    this.isPlaying = false;
    this.highlightVisible = true;
    this.browserFollowing = true;
    this.logsDropdownOpen = false;
    this._tick = 0;

    this.data = null;
    this.derived = null; // {playEnd, hasTiming, picOffsets, totalPics}

    this.panelCollapsed = {};
    this.panelHeight = {};
    this.stepPanelFollowing = {};
    this.stageHeight = null;

    this._lastRafTime = null;
    this._rafId = null;
    this._scrollBusy = {};
    this._browserTimedLines = null;
  }

  // ---------------------------------------------------------------------------
  // Theme
  // ---------------------------------------------------------------------------

  _readTheme() {
    try {
      return localStorage.getItem("vp-theme") || "auto";
    } catch (e) {
      return "auto";
    }
  }

  _applyTheme(mode) {
    const prefersDark =
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
    const dark = mode === "dark" || (mode === "auto" && prefersDark);
    document.documentElement.classList.toggle("theme-dark", dark);
  }

  _cycleTheme() {
    const next = THEME_CYCLE[(THEME_CYCLE.indexOf(this.theme) + 1) % THEME_CYCLE.length];
    try {
      localStorage.setItem("vp-theme", next);
    } catch (e) {
      // ignore
    }
    this.theme = next;
    this._applyTheme(next);
  }

  // ---------------------------------------------------------------------------
  // Data load & derived computations
  // ---------------------------------------------------------------------------

  _loadData() {
    const node = document.getElementById("replay-data");
    if (!node) return;
    this.data = JSON.parse(node.textContent);

    const steps = this.data.steps;
    const hasTiming =
      this.data.scenarioDuration > 0 &&
      steps.some((s) => s.startOffset !== null && s.duration > 0);

    // Synthesise startOffset/duration for untimed steps so they integrate with seeking.
    if (hasTiming) {
      const marker = this.data.scenarioDuration * 0.005;
      let lastEnd = 0;
      steps.forEach((s) => {
        if (s.startOffset !== null) {
          lastEnd = s.startOffset + (s.duration || 0);
        } else {
          s.startOffset = lastEnd;
          s.duration = marker;
          lastEnd += marker;
        }
      });
    }

    const picOffsets = [];
    let sum = 0;
    steps.forEach((s) => {
      picOffsets.push(sum);
      sum += stepFrameCount(s);
    });
    const totalPics = steps.length
      ? picOffsets[picOffsets.length - 1] + stepFrameCount(steps[steps.length - 1])
      : 0;

    let playEnd;
    if (!hasTiming) {
      playEnd = Math.max(steps.length - 1, 0);
    } else {
      let last = 0;
      steps.forEach((s) => {
        if (s.startOffset !== null) last = Math.max(last, s.startOffset + (s.duration || 0));
      });
      playEnd = last > 0 ? last : this.data.scenarioDuration;
    }

    this.derived = { hasTiming, picOffsets, totalPics, playEnd };

    // Init follow state for each step-panel content id
    ["vp-steps-content", "vp-cucu-content", "vp-stdout-content", "vp-stderr-content", "vp-errors-content"].forEach((id) => {
      this.stepPanelFollowing[id] = true;
    });
  }

  _restorePanelState() {
    [
      "vp-pics-panel", "vp-steps-panel", "vp-cucu-panel", "vp-browser-panel",
      "vp-stdout-panel", "vp-stderr-panel", "vp-errors-panel",
    ].forEach((id) => {
      try {
        if (localStorage.getItem("vp-" + id + "-collapsed") === "1") this.panelCollapsed[id] = true;
        const h = parseInt(localStorage.getItem("vp-" + id + "-height"), 10);
        if (h >= 60) this.panelHeight[id] = h;
      } catch (e) {
        // ignore
      }
    });
    try {
      const sh = parseInt(localStorage.getItem("vp-stage-height"), 10);
      if (sh >= 120) this.stageHeight = sh;
    } catch (e) {
      // ignore
    }
  }

  // ---------------------------------------------------------------------------
  // Lifecycle
  // ---------------------------------------------------------------------------

  connectedCallback() {
    super.connectedCallback();
    this._loadData();
    this._restorePanelState();
    this._applyTheme(this.theme);
    this._osDarkListener = () => {
      if (this.theme === "auto") this._applyTheme("auto");
    };
    window.matchMedia?.("(prefers-color-scheme: dark)").addEventListener("change", this._osDarkListener);
    this._keydown = (e) => this._onKeydown(e);
    document.addEventListener("keydown", this._keydown);
    this._docClick = (e) => {
      if (!this.logsDropdownOpen) return;
      const path = e.composedPath();
      if (!path.some((n) => n.id === "log-menu-wrap")) this.logsDropdownOpen = false;
    };
    document.addEventListener("click", this._docClick);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    window.matchMedia?.("(prefers-color-scheme: dark)").removeEventListener("change", this._osDarkListener);
    document.removeEventListener("keydown", this._keydown);
    document.removeEventListener("click", this._docClick);
    if (this._rafId) cancelAnimationFrame(this._rafId);
  }

  firstUpdated() {
    if (!this.data) return;
    // Firefox defers loading="lazy" images until they near the viewport; hidden step frames never
    // trigger that intersection until shown. Force eager loading so screenshots are ready.
    if (navigator.userAgent.toLowerCase().indexOf("firefox") > -1) {
      this.renderRoot.querySelectorAll('img[loading="lazy"]').forEach((img) => img.setAttribute("loading", "eager"));
    }

    // Initial playhead position: hash deep-link wins, else first failing step.
    let startTime = 0;
    const hash = window.location.hash;
    if (hash && hash.indexOf("#step_") === 0) {
      const n = parseInt(hash.replace("#step_", ""), 10);
      if (!isNaN(n) && n >= 1 && n <= this.data.steps.length) {
        startTime = this._stepIdxToTime(n - 1);
      }
    } else {
      const failIdx = this.data.steps.findIndex((s) => s.status === "failed" || s.status === "errored");
      if (failIdx >= 0) startTime = this._stepIdxToTime(failIdx);
    }
    this.seekToTime(startTime);
  }

  // (updated() is defined further below — consolidated with attach-once logic)

  // ---------------------------------------------------------------------------
  // Time ↔ step resolution
  // ---------------------------------------------------------------------------

  _timeToStepIdx(t) {
    const { hasTiming } = this.derived;
    const steps = this.data.steps;
    if (!hasTiming) return Math.min(Math.round(t), steps.length - 1);
    let best = 0;
    for (let i = 0; i < steps.length; i++) {
      if (steps[i].startOffset !== null && steps[i].startOffset <= t) best = i;
    }
    return best;
  }

  _timeToImgIdx(stepIdx, t) {
    const step = this.data.steps[stepIdx];
    const n = step.screenshots.length;
    if (n <= 1 || step.duration <= 0 || step.startOffset === null) return 0;
    const within = Math.max(0, t - step.startOffset);
    return Math.min(Math.floor((within / step.duration) * n), n - 1);
  }

  _stepIdxToTime(idx) {
    if (!this.derived.hasTiming) return idx;
    const steps = this.data.steps;
    for (let i = idx; i >= 0; i--) {
      if (steps[i].startOffset !== null) return steps[i].startOffset;
    }
    return 0;
  }

  // ---------------------------------------------------------------------------
  // Seeking / playback / navigation
  // ---------------------------------------------------------------------------

  _reengageFollow() {
    this.browserFollowing = true;
    Object.keys(this.stepPanelFollowing).forEach((k) => {
      this.stepPanelFollowing[k] = true;
    });
  }

  seekToTime(t) {
    const playEnd = this.derived.playEnd;
    this.currentTimeSec = Math.max(0, Math.min(t, playEnd));
    const newStepIdx = this._timeToStepIdx(this.currentTimeSec);
    const stepChanged = newStepIdx !== this.shownStepIdx;
    this.shownStepIdx = newStepIdx;
    this.shownImgIdx = this._timeToImgIdx(newStepIdx, this.currentTimeSec);
    if (stepChanged) {
      const num = this.data.steps[newStepIdx].num;
      try {
        history.replaceState(null, "", "#step_" + num);
      } catch (e) {
        // ignore
      }
    }
    this._reengageFollow();
  }

  seekToStepIdx(idx) {
    this.seekToTime(this._stepIdxToTime(idx));
  }

  navigateStep(delta) {
    const total = this.data.steps.length;
    if (delta > 0 && this.shownStepIdx >= total - 1) {
      this.seekToTime(this.derived.playEnd);
      return;
    }
    const next = Math.max(0, Math.min(this.shownStepIdx + delta, total - 1));
    this.seekToStepIdx(next);
  }

  goToEnd() {
    this.seekToTime(this.derived.playEnd);
  }

  startPlay() {
    if (this.isPlaying) return;
    if (this.currentTimeSec >= this.derived.playEnd) return;
    this.isPlaying = true;
    this._lastRafTime = null;
    this._reengageFollow();
    this._rafId = requestAnimationFrame((t) => this._playFrame(t));
  }

  stopPlay() {
    this.isPlaying = false;
    if (this._rafId) {
      cancelAnimationFrame(this._rafId);
      this._rafId = null;
    }
  }

  togglePlay() {
    if (this.isPlaying) this.stopPlay();
    else this.startPlay();
  }

  _playFrame(rafTime) {
    if (!this.isPlaying) return;
    const playEnd = this.derived.playEnd;
    if (this._lastRafTime !== null) {
      this.currentTimeSec += ((rafTime - this._lastRafTime) / 1000) * 1.0;
      if (this.currentTimeSec >= playEnd) {
        this.currentTimeSec = playEnd;
        const idx = this._timeToStepIdx(this.currentTimeSec);
        this.shownStepIdx = idx;
        this.shownImgIdx = this._timeToImgIdx(idx, this.currentTimeSec);
        this.stopPlay();
        return;
      }
    }
    this._lastRafTime = rafTime;
    const idx = this._timeToStepIdx(this.currentTimeSec);
    this.shownStepIdx = idx;
    this.shownImgIdx = this._timeToImgIdx(idx, this.currentTimeSec);
    this._rafId = requestAnimationFrame((t) => this._playFrame(t));
  }

  shiftScreenshot(delta) {
    const frameIdx = this.shownStepIdx;
    if (frameIdx < 0) return;
    const steps = this.data.steps;
    const step = steps[frameIdx];
    const n = step.screenshots.length;
    const cur = this.shownImgIdx >= 0 ? this.shownImgIdx : 0;
    const next = cur + delta;
    const { hasTiming } = this.derived;

    if (next >= 0 && next < n) {
      if (hasTiming && step.startOffset !== null && step.duration > 0 && n > 1) {
        this.seekToTime(step.startOffset + ((next + 0.5) / n) * step.duration);
      } else {
        this.shownImgIdx = next;
      }
      return;
    }

    if (delta > 0) {
      for (let i = frameIdx + 1; i < steps.length; i++) {
        if (steps[i].screenshots.length > 0) {
          this.seekToStepIdx(i);
          return;
        }
      }
    } else {
      for (let i = frameIdx - 1; i >= 0; i--) {
        const m = steps[i].screenshots.length;
        if (m > 0) {
          const s = steps[i];
          if (hasTiming && s.startOffset !== null && s.duration > 0 && m > 1) {
            this.seekToTime(s.startOffset + ((m - 0.5) / m) * s.duration);
          } else {
            this.seekToStepIdx(i);
          }
          return;
        }
      }
      this.seekToTime(0);
    }
  }

  _onKeydown(e) {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    switch (e.key) {
      case "ArrowLeft":  e.preventDefault(); this.shiftScreenshot(-1); break;
      case "ArrowRight": e.preventDefault(); this.shiftScreenshot(1);  break;
      case " ":          e.preventDefault(); this.togglePlay();        break;
      case "Home":       e.preventDefault(); this.seekToStepIdx(0);    break;
      case "End":        e.preventDefault(); this.goToEnd();           break;
    }
  }

  // ---------------------------------------------------------------------------
  // Panel collapse / resize
  // ---------------------------------------------------------------------------

  _togglePanel(id) {
    this.panelCollapsed[id] = !this.panelCollapsed[id];
    try {
      localStorage.setItem("vp-" + id + "-collapsed", this.panelCollapsed[id] ? "1" : "0");
    } catch (e) {
      // ignore
    }
    this._tick++;
  }

  _attachResize(handleEl, panelId, isStage) {
    handleEl.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      handleEl.setPointerCapture(e.pointerId);
      const targetSel = isStage ? "#vp-stage" : "#" + panelId + " .vp-log-content";
      const target = this.renderRoot.querySelector(targetSel);
      if (!target) return;
      const startY = e.clientY;
      const startH = target.offsetHeight;
      const minH = isStage ? 120 : parseInt(window.getComputedStyle(target).minHeight, 10) || 60;
      handleEl.classList.add("dragging");
      document.body.style.cursor = "ns-resize";
      document.body.style.userSelect = "none";
      const onMove = (ev) => {
        target.style.height = Math.max(minH, startH + (ev.clientY - startY)) + "px";
      };
      const onUp = () => {
        handleEl.classList.remove("dragging");
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
        try {
          if (isStage) localStorage.setItem("vp-stage-height", target.offsetHeight);
          else localStorage.setItem("vp-" + panelId + "-height", target.offsetHeight);
        } catch (e2) {
          // ignore
        }
        handleEl.removeEventListener("pointermove", onMove);
        handleEl.removeEventListener("pointerup", onUp);
        handleEl.removeEventListener("pointercancel", onUp);
      };
      handleEl.addEventListener("pointermove", onMove);
      handleEl.addEventListener("pointerup", onUp);
      handleEl.addEventListener("pointercancel", onUp);
    });
  }

  // ---------------------------------------------------------------------------
  // Timeline pointer drag (shared across all tracks)
  // ---------------------------------------------------------------------------

  _attachTimelineDrag(track) {
    const seek = (clientX) => {
      const rect = track.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
      this.seekToTime(ratio * this.derived.playEnd);
    };
    track.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      track.setPointerCapture(e.pointerId);
      seek(e.clientX);
      const onMove = (ev) => seek(ev.clientX);
      const onUp = () => {
        track.removeEventListener("pointermove", onMove);
        track.removeEventListener("pointerup", onUp);
        track.removeEventListener("pointercancel", onUp);
      };
      track.addEventListener("pointermove", onMove);
      track.addEventListener("pointerup", onUp);
      track.addEventListener("pointercancel", onUp);
    });
  }

  // ---------------------------------------------------------------------------
  // Step / browser highlight sync (imperative — operate on rendered server-like children)
  // ---------------------------------------------------------------------------

  _syncStepHighlights() {
    if (this.shownStepIdx < 0) return;
    const stepIdx = this.shownStepIdx;

    // Steps panel: highlight current + previous; scroll into view if following.
    const stepsContent = this.renderRoot.querySelector("#vp-steps-content");
    if (stepsContent) {
      stepsContent.querySelectorAll(".log-step-group").forEach((g) => {
        g.classList.remove("step-current", "step-previous");
      });
      let best = null;
      let prev = null;
      stepsContent.querySelectorAll(".log-step-group[data-step]").forEach((g) => {
        if (parseInt(g.dataset.step, 10) <= stepIdx) {
          prev = best;
          best = g;
        }
      });
      if (best) best.classList.add("step-current");
      if (prev) prev.classList.add("step-previous");
      if (best && this.stepPanelFollowing["vp-steps-content"] !== false) {
        const anchor = prev || best;
        const top = anchor.offsetTop - stepsContent.offsetTop;
        this._scrollBusy["vp-steps-content"] = true;
        stepsContent.scrollTop = Math.max(0, top - 4);
        requestAnimationFrame(() => {
          this._scrollBusy["vp-steps-content"] = false;
        });
      }
    }

    ["vp-cucu-content", "vp-stdout-content", "vp-stderr-content", "vp-errors-content"].forEach((id) => {
      const content = this.renderRoot.querySelector("#" + id);
      if (!content) return;
      content.querySelectorAll(".log-step-group").forEach((g) => g.classList.remove("step-current"));
      let best = null;
      content.querySelectorAll(".log-step-group[data-step]").forEach((g) => {
        if (parseInt(g.dataset.step, 10) <= stepIdx) best = g;
      });
      if (best) best.classList.add("step-current");
      if (best && this.stepPanelFollowing[id] !== false) {
        const top = best.offsetTop - content.offsetTop;
        this._scrollBusy[id] = true;
        content.scrollTop = Math.max(0, top - 4);
        requestAnimationFrame(() => {
          this._scrollBusy[id] = false;
        });
      }
    });
  }

  _syncBrowserHighlight() {
    const content = this.renderRoot.querySelector("#vp-browser-content");
    if (!content) return;
    const lines = this._browserTimedLines || [];
    if (lines.length === 0) return;
    let lo = 0, hi = lines.length - 1, best = 0;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      if (parseFloat(lines[mid].dataset.offset) <= this.currentTimeSec) {
        best = mid;
        lo = mid + 1;
      } else {
        hi = mid - 1;
      }
    }
    const target = lines[best];
    const prev = content.querySelector(".log-current");
    if (prev === target) return;
    if (prev) prev.classList.remove("log-current");
    target.classList.add("log-current");
    if (this.browserFollowing === false) return;
    this._scrollBusy["vp-browser-content"] = true;
    const cRect = content.getBoundingClientRect();
    const lRect = target.getBoundingClientRect();
    content.scrollTop += lRect.top - cRect.top - Math.floor(content.clientHeight * 0.33);
    requestAnimationFrame(() => {
      this._scrollBusy["vp-browser-content"] = false;
    });
  }

  // ---------------------------------------------------------------------------
  // Render — top-level template
  // ---------------------------------------------------------------------------

  createRenderRoot() {
    // Light DOM so cucu's fuzzy.find (jQuery against document.body) can reach our buttons/links.
    return this;
  }

  render() {
    if (!this.data) return html``;

    // Toggle host class for highlight visibility.
    this.classList.toggle("hide-highlights", !this.highlightVisible);

    return html`
      <style>${STYLES_TEXT}</style>
      ${this._renderNav()}
      ${this._renderHeader()}
      ${this._renderPicsPanel()}
      ${this._renderStepInfo()}
      ${this._renderStepsPanel()}
      ${this._renderLogPanels()}
    `;
  }

  // ---------------------------------------------------------------------------
  // Render — nav
  // ---------------------------------------------------------------------------

  _renderNav() {
    const data = this.data;
    const cur = this.currentTimeSec.toFixed(1);
    const tot = data.scenarioDuration.toFixed(1);
    let metaText;
    if (data.scenarioStartMs === null) {
      metaText = "▶ " + cur + " / " + tot + "s";
    } else {
      metaText = "▶ " + formatPlayheadTime(data.scenarioStartMs + this.currentTimeSec * 1000) + " · " + cur + " / " + tot + "s";
    }

    return html`
      <nav id="vp-nav">
        <a href=${data.links.flat} title="Flat view">Flat</a>
        <span class="vp-sep">|</span>
        <a href=${data.links.index} title="Index">Index</a>
        <span class="vp-sep">|</span>
        <a href=${data.links.feature} title="Feature">Feature</a>
        <span class="vp-sep">|</span>
        <a href=${data.links.classic} title="Classic checklist view">☑ Classic</a>
        ${data.logs.length > 0
          ? html`
            <span class="vp-sep">|</span>
            <div id="log-menu-wrap">
              <a href="#" id="log-menu-trigger" @click=${(e) => { e.preventDefault(); this.logsDropdownOpen = !this.logsDropdownOpen; }}>Logs ▾</a>
              <div id="log-dd" class=${this.logsDropdownOpen ? "open" : ""}>
                ${data.logs.map((lf) => html`<a href=${lf.url}>${lf.name}</a>`)}
              </div>
            </div>`
          : nothing}
        <div class="vp-nav-right">
          <button id="theme-toggle" type="button" title=${THEME_TITLES[this.theme] || THEME_TITLES.auto} @click=${() => this._cycleTheme()}>
            ${THEME_ICONS[this.theme] || THEME_ICONS.auto}
          </button>
          <span class="vp-meta" id="vp-meta-time">${metaText}</span>
        </div>
      </nav>
    `;
  }

  // ---------------------------------------------------------------------------
  // Render — header
  // ---------------------------------------------------------------------------

  _renderHeader() {
    const data = this.data;
    return html`
      <div id="vp-header">
        <div class="vp-feature-row">
          <div class="vp-feature-name">
            <span class="vp-feature-label">Feature</span>
            <a href=${data.links.feature} title="Go to feature report">${data.featureName}</a>
          </div>
          ${data.mhtFiles.length > 0 ? html`
            <div class="vp-mht-link">
              ${data.mhtFiles.map((mf, i) => html`<a href=${mf.url} title="Browser snapshot (MHT archive)">📄 ${mf.name}</a>${i < data.mhtFiles.length - 1 ? html`&nbsp;` : nothing}`)}
            </div>` : nothing}
        </div>
        <div class="vp-scenario-name"><span class="vp-feature-label">Scenario</span> ${data.scenarioName}</div>
        ${data.featureTagsHtml || data.scenarioTagsHtml ? html`
          <div class="vp-tags">${rawHtml(data.featureTagsHtml)} ${rawHtml(data.scenarioTagsHtml)}</div>` : nothing}
        ${data.subHeadersHtml ? html`<div class="vp-tags" style="margin-top:4px">${rawHtml(data.subHeadersHtml)}</div>` : nothing}
      </div>
    `;
  }

  // ---------------------------------------------------------------------------
  // Render — pics panel (stage)
  // ---------------------------------------------------------------------------

  _renderPicsPanel() {
    const steps = this.data.steps;
    const playEnd = this.derived.playEnd > 0 ? this.derived.playEnd : 1;
    const cursorPct = this.derived.playEnd > 0 ? (this.currentTimeSec / this.derived.playEnd) * 100 : 0;

    // Pics ticks
    const picsTicks = [];
    steps.forEach((step) => {
      if (step.startOffset === null) return;
      const n = Math.max(1, step.screenshots.length);
      const statusClass = "pics-tick-" + (step.status || "untested");
      for (let i = 0; i < n; i++) {
        const offset = step.startOffset + (i / n) * step.duration;
        picsTicks.push({ left: Math.max(0, Math.min(100, (offset / playEnd) * 100)), statusClass });
      }
    });

    const stageStyle = this.stageHeight ? `height: ${this.stageHeight}px` : "";

    return html`
      <div id="vp-pics-panel" class=${"vp-log-panel" + (this.panelCollapsed["vp-pics-panel"] ? " collapsed" : "")}>
        <div class="vp-log-header">
          <span class="log-toggle-area" @click=${() => this._togglePanel("vp-pics-panel")}>
            <span class="log-collapse-chevron">▾</span>
            <span class="log-title">Pics</span>
          </span>
          <div id="pics-timeline-track" class="panel-header-track" ${this._refTimelineTrack()}>
            ${picsTicks.map((t) => html`<div class=${"pics-tick " + t.statusClass} style=${"left: " + t.left + "%"}></div>`)}
            <div class="tl-cursor" style=${"left: " + cursorPct + "%"}></div>
          </div>
          <label class="log-follow-label" title="Toggle element highlights">
            <input type="checkbox" .checked=${this.highlightVisible} @change=${(e) => { this.highlightVisible = e.target.checked; }}>
            highlight
          </label>
        </div>
        <div class="vp-log-body">
          <div id="vp-stage" style=${stageStyle}>
            ${steps.map((step, si) => this._renderStepFrame(step, si))}
            <button class="stage-nav-btn" id="stage-btn-prev" type="button" title="Previous screenshot (← arrow)" @click=${() => this.shiftScreenshot(-1)}>&#8249;</button>
            <button class="stage-nav-btn" id="stage-btn-next" type="button" title="Next screenshot (→ arrow)" @click=${() => this.shiftScreenshot(1)}>&#8250;</button>
          </div>
          <div id="stage-resize-handle" ${this._refStageResize()}></div>
        </div>
      </div>
    `;
  }

  _renderStepFrame(step, si) {
    const show = si === this.shownStepIdx;
    const display = show ? "" : "none";
    if (step.screenshots.length > 0) {
      return html`
        <div class="step-frame" id=${"frame-" + si} style=${"display:" + (show ? "" : "none")}>
          <div class="stage-screenshots">
            ${step.screenshots.map((img, ii) => html`
              <div class=${"screenshot-wrapper" + (ii === this.shownImgIdx && show ? " active" : "")} data-frame=${si} data-imgidx=${ii}>
                <img loading="lazy" class="stage-img" src=${img.src} alt=${img.label} title=${img.label}>
                ${img.highlight ? html`<div class="highlight-overlay" style=${`top:${img.highlight.top}%;left:${img.highlight.left}%;width:${img.highlight.width}%;height:${img.highlight.height}%`}></div>` : nothing}
              </div>
            `)}
          </div>
        </div>
      `;
    }
    const status = step.status || "untested";
    return html`
      <div class="step-frame" id=${"frame-" + si} style=${"display:" + (show ? "" : "none")}>
        <div class="no-screenshot-display">
          ${status === "skipped" ? html`<div class=${"step-skipped-label status-" + status}>(${status.toUpperCase()})</div>` : nothing}
          <div class="step-line">
            ${step.isSubstep ? html`<span class="substep-prefix">↳</span> ` : nothing}
            <span class=${"step-keyword-large status-" + status}>${step.keyword}</span>
            <span class="step-name-large">${step.name}</span>
          </div>
          ${step.textHtml ? html`<pre class="step-detail-pre">${step.textHtml}</pre>` : nothing}
          ${step.tableHtml ? html`<pre class="step-detail-pre">${step.tableHtml}</pre>` : nothing}
        </div>
      </div>
    `;
  }

  // ---------------------------------------------------------------------------
  // Render — step info bar
  // ---------------------------------------------------------------------------

  _renderStepInfo() {
    const data = this.data;
    const stepIdx = Math.max(0, this.shownStepIdx);
    const step = data.steps[stepIdx];
    const atEnd = this.currentTimeSec >= this.derived.playEnd;
    const startDisabled = this.currentTimeSec <= 0;
    const playDisabled = atEnd && !this.isPlaying;
    const prevDisabled = stepIdx === 0 && this.currentTimeSec <= 0;
    const nextDisabled = atEnd;
    const stepShots = step?.screenshots || [];
    const stepPicNavClass = stepShots.length > 1 ? "" : "disabled";
    const picCount = stepShots.length > 1 ? (this.shownImgIdx + 1) + " / " + stepShots.length : "– / –";

    let overall = "– / –";
    let pillClass = "status-pill";
    if (this.derived.totalPics > 0 && step) {
      const clamped = stepShots.length > 1 ? Math.min(this.shownImgIdx, stepShots.length - 1) : 0;
      overall = (this.derived.picOffsets[stepIdx] || 0) + clamped + 1 + " / " + this.derived.totalPics;
    } else {
      pillClass += " disabled";
    }

    const caption = stepShots[this.shownImgIdx] ? stepShots[this.shownImgIdx].label || "" : "";

    return html`
      <div id="vp-step-info">
        <span id="pic-overall-pill" class=${pillClass} title="Overall pic index across the scenario (each step counts as at least one frame)">${overall}</span>
        <button class="ctrl-btn" id="btn-start" type="button" title="Start" ?disabled=${startDisabled} @click=${() => this.seekToTime(0)}>⏮</button>
        <button class="ctrl-btn" id="btn-play-pause" type="button" title="Play / Pause (Space)" ?disabled=${playDisabled} @click=${() => this.togglePlay()}>${this.isPlaying ? "⏸" : "▶"}</button>
        <button class="ctrl-btn" id="btn-end" type="button" title="End" ?disabled=${atEnd} @click=${() => this.goToEnd()}>⏭</button>
        <span id="step-num-badge">
          <span class="step-nav-label">Step</span>
          <button class="step-nav-btn" id="step-nav-prev" type="button" title="Previous step" ?disabled=${prevDisabled} @click=${() => this.navigateStep(-1)}>◀</button>
          <span id="step-count"><span id="step-cur">${step ? step.num : 1}</span> / ${data.steps.length}</span>
          <button class="step-nav-btn" id="step-nav-next" type="button" title="Next step" ?disabled=${nextDisabled} @click=${() => this.navigateStep(1)}>▶</button>
        </span>
        <span id="step-pic-nav" class=${stepPicNavClass}>
          <span class="step-pic-nav-label">Step Pic</span>
          <button class="step-pic-nav-btn" type="button" title="Previous screenshot" @click=${() => this.shiftScreenshot(-1)}>◀</button>
          <span id="pic-count">${picCount}</span>
          <button class="step-pic-nav-btn" type="button" title="Next screenshot" @click=${() => this.shiftScreenshot(1)}>▶</button>
        </span>
        <span id="pic-caption">${caption}</span>
        <span id="step-timing-text">${step ? step.timingLabel : ""}</span>
      </div>
    `;
  }

  // ---------------------------------------------------------------------------
  // Render — steps panel
  // ---------------------------------------------------------------------------

  _renderStepsPanel() {
    const data = this.data;
    const playEnd = this.derived.playEnd > 0 ? this.derived.playEnd : 1;
    const cursorPct = this.derived.playEnd > 0 ? (this.currentTimeSec / this.derived.playEnd) * 100 : 0;

    // Step bars
    const bars = data.steps.map((step, i) => {
      let leftPct, widthPct;
      if (this.derived.hasTiming) {
        leftPct = (step.startOffset / playEnd) * 100;
        widthPct = Math.max((step.duration / playEnd) * 100, 0.25);
      } else {
        leftPct = (i / Math.max(data.steps.length - 1, 1)) * 100;
        widthPct = 100 / data.steps.length;
      }
      const classes = "step-bar status-" + (step.status || "untested") + (step.isHeading ? " heading" : "") + (i === this.shownStepIdx ? " active" : "");
      return html`<div
        id=${"bar-" + i}
        class=${classes}
        title=${"Step " + step.num + ": " + step.keyword + " " + step.name.slice(0, 80)}
        style=${`left:${leftPct}%;width:${widthPct}%`}
        @click=${(e) => { e.stopPropagation(); this.seekToTime(this.derived.hasTiming ? step.startOffset : this._stepIdxToTime(i)); }}
      ></div>`;
    });

    // Breadcrumb
    let breadcrumbName = "Scenario: " + data.scenarioName;
    for (let i = 0; i <= this.shownStepIdx && i < data.steps.length; i++) {
      if (data.steps[i].headingLevel)
        breadcrumbName = ((data.steps[i].keyword || "") + " " + data.steps[i].name).trim();
    }

    const stepsHeight = this.panelHeight["vp-steps-panel"] ? `height:${this.panelHeight["vp-steps-panel"]}px` : "";

    return html`
      <div id="vp-steps-panel" class=${"vp-log-panel" + (this.panelCollapsed["vp-steps-panel"] ? " collapsed" : "")}>
        <div class="vp-log-header">
          <span class="log-toggle-area" @click=${() => this._togglePanel("vp-steps-panel")}>
            <span class="log-collapse-chevron">▾</span>
            <span class="log-title">Steps</span>
          </span>
          <div id="timeline-track" ${this._refTimelineTrack()}>
            ${bars}
            <div id="timeline-playhead" style=${"left:" + cursorPct + "%"}></div>
          </div>
          <label class="log-follow-label">
            <input type="checkbox" .checked=${this.stepPanelFollowing["vp-steps-content"] !== false} @change=${(e) => { this.stepPanelFollowing["vp-steps-content"] = e.target.checked; this._tick++; }}>
            follow
          </label>
        </div>
        <div class="vp-log-body">
          <div id="steps-breadcrumb">
            <div class="log-line"><span class="steps-name">${breadcrumbName}</span></div>
          </div>
          <div id="vp-steps-content" class="vp-log-content" style=${stepsHeight}
               @scroll=${() => this._onPanelScroll("vp-steps-content")}>
            <div class="log-step-group steps-row steps-heading" data-seek-time="0" title="Jump to scenario start" @click=${() => this.seekToTime(0)}>
              <div class="log-line"><span class="steps-name">Scenario: ${data.scenarioName}</span></div>
            </div>
            ${data.steps.map((step, i) => html`
              <div class=${"log-step-group steps-row" + (step.isSubstep ? " steps-substep" : "") + (step.headingLevel ? " steps-heading" : "")}
                   data-step=${i} data-seek-step=${i}
                   @click=${() => this.seekToStepIdx(i)}>
                <div class="log-line">
                  ${step.headingLevel
                    ? html`<span class="steps-name">${step.keyword} ${step.name}</span>`
                    : html`<span class=${"steps-kw steps-" + (step.status || "untested")}>${step.keyword}</span><span class="steps-name">${step.name}</span>`}
                </div>
              </div>
            `)}
          </div>
          <div class="vp-log-resize" ${this._refResize("vp-steps-panel")}></div>
        </div>
      </div>
    `;
  }

  // ---------------------------------------------------------------------------
  // Render — log panels (cucu, browser, stdout, stderr, errors)
  // ---------------------------------------------------------------------------

  _renderLogPanels() {
    const data = this.data;
    const hasCucu = data.steps.some((s) => s.debugOutputHtml);
    const hasBrowser = data.steps.some((s) => s.browserLogs.length > 0);
    const hasStdout = data.steps.some((s) => s.stdout.length > 0);
    const hasStderr = data.steps.some((s) => s.stderr.length > 0);
    const hasErrors = data.steps.some((s) => s.errorMessage.length > 0);

    return html`
      ${hasCucu ? this._renderCucuPanel() : nothing}
      ${hasBrowser ? this._renderBrowserPanel() : nothing}
      ${hasStdout ? this._renderStdoutPanel() : nothing}
      ${hasStderr ? this._renderStderrPanel() : nothing}
      ${hasErrors ? this._renderErrorsPanel() : nothing}
    `;
  }

  _renderLogPanelShell({ id, title, contentId, followKey, hasTimeline, timelineTrackId, children }) {
    const isBrowser = followKey === "browser";
    const followChecked = isBrowser
      ? this.browserFollowing
      : this.stepPanelFollowing[contentId] !== false;
    const onFollow = (e) => {
      if (isBrowser) this.browserFollowing = e.target.checked;
      else { this.stepPanelFollowing[contentId] = e.target.checked; this._tick++; }
    };
    const heightStyle = this.panelHeight[id] ? `height:${this.panelHeight[id]}px` : "";

    return html`
      <div id=${id} class=${"vp-log-panel" + (this.panelCollapsed[id] ? " collapsed" : "")}>
        <div class="vp-log-header">
          <span class="log-toggle-area" @click=${() => this._togglePanel(id)}>
            <span class="log-collapse-chevron">▾</span>
            <span class="log-title">${title}</span>
          </span>
          ${hasTimeline ? this._renderPanelTimelineTrack(timelineTrackId, followKey) : nothing}
          <label class="log-follow-label">
            <input type="checkbox" .checked=${followChecked} @change=${onFollow}>
            follow
          </label>
        </div>
        <div class="vp-log-body">
          <div id=${contentId} class="vp-log-content" style=${heightStyle}
               @scroll=${() => this._onPanelScroll(contentId)}>
            ${children}
          </div>
          <div class="vp-log-resize" ${this._refResize(id)}></div>
        </div>
      </div>
    `;
  }

  _renderPanelTimelineTrack(trackId, followKey) {
    const playEnd = this.derived.playEnd > 0 ? this.derived.playEnd : 1;
    const cursorPct = this.derived.playEnd > 0 ? (this.currentTimeSec / this.derived.playEnd) * 100 : 0;
    const data = this.data;

    let bars = [];
    let ticks = [];

    if (trackId === "cucu-timeline-track") {
      bars = this._presenceBars((s) => !!s.debugOutputHtml);
    } else if (trackId === "stdout-timeline-track") {
      bars = this._presenceBars((s) => s.stdout.length > 0);
    } else if (trackId === "errors-timeline-track") {
      bars = this._presenceBars((s) => s.errorMessage.length > 0);
    } else if (trackId === "browser-timeline-track") {
      data.steps.forEach((step) => {
        step.browserLogs.forEach((bl) => {
          if (bl.offset === undefined) return;
          const level = bl.level === "SEVERE" || bl.level === "ERROR" || bl.level === "CRITICAL"
            ? "error"
            : bl.level === "WARNING" ? "warning" : "info";
          ticks.push({ left: Math.max(0, Math.min(100, (bl.offset / playEnd) * 100)), level });
        });
      });
    }

    const hidden = trackId !== "browser-timeline-track" && bars.length === 0;
    return html`
      <div id=${trackId} class="panel-header-track" style=${hidden ? "display:none" : ""} ${this._refTimelineTrack()}>
        ${bars.map((b) => html`<div class="tl-step-bar" style=${`left:${b.left}%;width:${b.width}%`}></div>`)}
        ${ticks.map((t) => html`<div class=${"tl-tick tl-" + t.level} style=${"left:" + t.left + "%"}></div>`)}
        <div class="tl-cursor" style=${"left:" + cursorPct + "%"}></div>
      </div>
    `;
  }

  _presenceBars(predicate) {
    const playEnd = this.derived.playEnd > 0 ? this.derived.playEnd : 1;
    const out = [];
    this.data.steps.forEach((step, i) => {
      if (!predicate(step)) return;
      let leftPct, widthPct;
      if (this.derived.hasTiming && step.startOffset !== null) {
        leftPct = (step.startOffset / playEnd) * 100;
        widthPct = Math.max(0.5, (step.duration / playEnd) * 100);
      } else {
        leftPct = (i / Math.max(this.data.steps.length, 1)) * 100;
        widthPct = 100 / this.data.steps.length;
      }
      out.push({ left: leftPct, width: widthPct });
    });
    return out;
  }

  _renderCucuPanel() {
    const data = this.data;
    return this._renderLogPanelShell({
      id: "vp-cucu-panel",
      title: "Cucu",
      contentId: "vp-cucu-content",
      followKey: "step",
      hasTimeline: true,
      timelineTrackId: "cucu-timeline-track",
      children: data.steps.map((step, i) =>
        step.debugOutputHtml ? html`
          <div class="log-step-group" data-step=${i}>
            <div class="log-line">${rawHtml(step.debugOutputHtml)}</div>
          </div>` : nothing
      ),
    });
  }

  _renderBrowserPanel() {
    const data = this.data;
    const children = [];
    data.steps.forEach((step) => {
      step.browserLogs.forEach((bl) => {
        const level = bl.level === "SEVERE" || bl.level === "ERROR" || bl.level === "CRITICAL"
          ? "error"
          : bl.level === "WARNING" ? "warning" : "info";
        const classes = "log-line browser-log-line bl-" + level;
        children.push(bl.offset !== undefined
          ? html`<div class=${classes} data-offset=${bl.offset}>${bl.ts} ${bl.level} ${bl.message}</div>`
          : html`<div class=${classes}>${bl.ts} ${bl.level} ${bl.message}</div>`);
      });
    });
    return this._renderLogPanelShell({
      id: "vp-browser-panel",
      title: "Browser",
      contentId: "vp-browser-content",
      followKey: "browser",
      hasTimeline: true,
      timelineTrackId: "browser-timeline-track",
      children,
    });
  }

  _renderStdoutPanel() {
    const data = this.data;
    return this._renderLogPanelShell({
      id: "vp-stdout-panel",
      title: "Stdout",
      contentId: "vp-stdout-content",
      followKey: "step",
      hasTimeline: true,
      timelineTrackId: "stdout-timeline-track",
      children: data.steps.map((step, i) =>
        step.stdout.length > 0 ? html`
          <div class="log-step-group" data-step=${i}>
            ${step.stdout.map((line) => html`<div class="log-line">${line}</div>`)}
          </div>` : nothing
      ),
    });
  }

  _renderStderrPanel() {
    const data = this.data;
    return this._renderLogPanelShell({
      id: "vp-stderr-panel",
      title: "Stderr",
      contentId: "vp-stderr-content",
      followKey: "step",
      hasTimeline: false,
      children: data.steps.map((step, i) =>
        step.stderr.length > 0 ? html`
          <div class="log-step-group" data-step=${i}>
            <div class="log-step-label">Step ${i + 1}: ${step.keyword}${step.name}</div>
            ${step.stderr.map((line) => html`<div class="log-line stderr-line">${line}</div>`)}
          </div>` : nothing
      ),
    });
  }

  _renderErrorsPanel() {
    const data = this.data;
    return this._renderLogPanelShell({
      id: "vp-errors-panel",
      title: "Errors",
      contentId: "vp-errors-content",
      followKey: "step",
      hasTimeline: true,
      timelineTrackId: "errors-timeline-track",
      children: data.steps.map((step, i) =>
        step.errorMessage.length > 0 ? html`
          <div class="log-step-group" data-step=${i}>
            ${step.errorMessage.map((entry) => html`<div class="log-line error-line">${entry}</div>`)}
          </div>` : nothing
      ),
    });
  }

  // ---------------------------------------------------------------------------
  // Lit "directives" implemented as simple ref callbacks via element attribute hooks
  // ---------------------------------------------------------------------------

  // Hook a function on first connect — Lit doesn't have a built-in ref but we can use a
  // template element-attribute that fires on render. We piggy-back on a no-op event binding.
  _refTimelineTrack() {
    // Use a one-time pointerdown attach via a marker attribute; firstUpdated/updated wires it.
    return nothing;
  }

  _refResize(panelId) {
    return nothing;
  }

  _refStageResize() {
    return nothing;
  }

  // After every render, attach pointer handlers to newly-rendered tracks / handles, then sync
  // step/browser highlight classes against the freshly-rendered children.
  updated(changedProps) {
    super.updated?.(changedProps);
    this._attachOnceTracks();
    this._attachOnceResizes();
    if (!this._browserTimedLines) {
      this._browserTimedLines = Array.from(
        this.renderRoot.querySelectorAll("#vp-browser-content .log-line[data-offset]"),
      );
    }
    this._syncStepHighlights();
    this._syncBrowserHighlight();
  }

  _attachOnceTracks() {
    const trackIds = [
      "timeline-track", "pics-timeline-track", "stdout-timeline-track",
      "cucu-timeline-track", "browser-timeline-track", "errors-timeline-track",
    ];
    trackIds.forEach((id) => {
      const t = this.renderRoot.querySelector("#" + id);
      if (t && !t._dragAttached) {
        this._attachTimelineDrag(t);
        t._dragAttached = true;
      }
    });
  }

  _attachOnceResizes() {
    [
      ["vp-steps-panel", "#vp-steps-panel .vp-log-resize"],
      ["vp-cucu-panel", "#vp-cucu-panel .vp-log-resize"],
      ["vp-browser-panel", "#vp-browser-panel .vp-log-resize"],
      ["vp-stdout-panel", "#vp-stdout-panel .vp-log-resize"],
      ["vp-stderr-panel", "#vp-stderr-panel .vp-log-resize"],
      ["vp-errors-panel", "#vp-errors-panel .vp-log-resize"],
    ].forEach(([id, sel]) => {
      const h = this.renderRoot.querySelector(sel);
      if (h && !h._resizeAttached) {
        this._attachResize(h, id, false);
        h._resizeAttached = true;
      }
    });
    const stage = this.renderRoot.querySelector("#stage-resize-handle");
    if (stage && !stage._resizeAttached) {
      this._attachResize(stage, "stage", true);
      stage._resizeAttached = true;
    }
  }

  // Disable follow when the user scrolls a panel manually.
  _onPanelScroll(contentId) {
    if (this._scrollBusy[contentId]) return;
    if (contentId === "vp-browser-content") {
      this.browserFollowing = false;
    } else {
      this.stepPanelFollowing[contentId] = false;
      this._tick++;
    }
  }
}

customElements.define("cucu-replay-app", CucuReplayApp);
