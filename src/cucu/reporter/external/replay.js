// Cucu replay-view player. Companion CSS: replay.css. Per-scenario data is supplied via the
// inline JSON island at #replay-data; everything else is wired up from the static DOM.
(function () {
  "use strict";

  // ===== DATA =====
  var DATA_NODE = document.getElementById('replay-data');
  if (!DATA_NODE) return;
  var DATA = JSON.parse(DATA_NODE.textContent);

  var SCENARIO_DURATION = DATA.scenarioDuration;
  var SCENARIO_START_MS = DATA.scenarioStartMs;
  var SCENARIO_NAME     = DATA.scenarioName;
  var STEPS             = DATA.steps;
  var TOTAL_STEPS       = STEPS.length;

  // ===== THEME =====
  // Theme-init is inline in <head> so it runs before paint. Here we just handle the toggle button.
  var THEME_CYCLE  = ['auto', 'light', 'dark'];
  var THEME_ICONS  = { auto: '🖥', light: '☀', dark: '🌙' };
  var THEME_TITLES = { auto: 'Theme: auto (follows system)', light: 'Theme: light', dark: 'Theme: dark' };

  function applyTheme(mode) {
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    var dark = mode === 'dark' || (mode === 'auto' && prefersDark);
    document.documentElement.classList.toggle('theme-dark', dark);
    var btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.textContent = THEME_ICONS[mode] || THEME_ICONS.auto;
      btn.title       = THEME_TITLES[mode] || THEME_TITLES.auto;
    }
  }

  function readTheme() {
    try { return localStorage.getItem('vp-theme') || 'auto'; } catch (e) { return 'auto'; }
  }

  function cycleTheme() {
    var cur  = readTheme();
    var next = THEME_CYCLE[(THEME_CYCLE.indexOf(cur) + 1) % THEME_CYCLE.length];
    try { localStorage.setItem('vp-theme', next); } catch (e) {}
    applyTheme(next);
  }

  applyTheme(readTheme());
  if (window.matchMedia) {
    // Track OS dark-mode flips while the user is on auto.
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
      if (readTheme() === 'auto') applyTheme('auto');
    });
  }

  // ===== LOG PANEL: COLLAPSE & RESIZE =====
  function toggleLogPanel(panelId) {
    var panel = document.getElementById(panelId);
    if (!panel) return;
    var collapsed = panel.classList.toggle('collapsed');
    try { localStorage.setItem('vp-' + panelId + '-collapsed', collapsed ? '1' : '0'); } catch (e) {}
  }

  function initLogPanel(panelId, contentId, resizeId) {
    var panel   = document.getElementById(panelId);
    var content = document.getElementById(contentId);
    var handle  = resizeId ? document.getElementById(resizeId) : null;
    if (!panel) return;

    try {
      if (localStorage.getItem('vp-' + panelId + '-collapsed') === '1') panel.classList.add('collapsed');
    } catch (e) {}

    if (!handle || !content) return;

    try {
      var h = parseInt(localStorage.getItem('vp-' + panelId + '-height'), 10);
      if (h >= 60) content.style.height = h + 'px';
    } catch (e) {}

    handle.addEventListener('pointerdown', function (e) {
      e.preventDefault();
      handle.setPointerCapture(e.pointerId);
      var startY = e.clientY;
      var startH = content.offsetHeight;
      var minH   = parseInt(window.getComputedStyle(content).minHeight, 10) || 60;
      handle.classList.add('dragging');
      document.body.style.cursor    = 'ns-resize';
      document.body.style.userSelect = 'none';

      function onMove(ev) {
        content.style.height = Math.max(minH, startH + (ev.clientY - startY)) + 'px';
      }
      function onUp() {
        handle.classList.remove('dragging');
        document.body.style.cursor    = '';
        document.body.style.userSelect = '';
        try { localStorage.setItem('vp-' + panelId + '-height', content.offsetHeight); } catch (e2) {}
        handle.removeEventListener('pointermove', onMove);
        handle.removeEventListener('pointerup',   onUp);
        handle.removeEventListener('pointercancel', onUp);
      }
      handle.addEventListener('pointermove', onMove);
      handle.addEventListener('pointerup',   onUp);
      handle.addEventListener('pointercancel', onUp);
    });
  }

  initLogPanel('vp-pics-panel');  // collapse only — stage has its own resize handle
  initLogPanel('vp-steps-panel',   'vp-steps-content',   'steps-resize-handle');
  initLogPanel('vp-cucu-panel',    'vp-cucu-content',    'cucu-resize-handle');
  initLogPanel('vp-browser-panel', 'vp-browser-content', 'browser-resize-handle');
  initLogPanel('vp-stdout-panel',  'vp-stdout-content',  'stdout-resize-handle');
  initLogPanel('vp-stderr-panel',  'vp-stderr-content',  'stderr-resize-handle');
  initLogPanel('vp-errors-panel',  'vp-errors-content',  'errors-resize-handle');

  // Stage resize
  (function () {
    var stage  = document.getElementById('vp-stage');
    var handle = document.getElementById('stage-resize-handle');
    if (!stage || !handle) return;
    try {
      var h = parseInt(localStorage.getItem('vp-stage-height'), 10);
      if (h >= 120) stage.style.height = h + 'px';
    } catch (e) {}
    handle.addEventListener('pointerdown', function (e) {
      e.preventDefault();
      handle.setPointerCapture(e.pointerId);
      var startY = e.clientY;
      var startH = stage.offsetHeight;
      handle.classList.add('dragging');
      document.body.style.cursor    = 'ns-resize';
      document.body.style.userSelect = 'none';
      function onMove(ev) {
        stage.style.height = Math.max(120, startH + (ev.clientY - startY)) + 'px';
      }
      function onUp() {
        handle.classList.remove('dragging');
        document.body.style.cursor    = '';
        document.body.style.userSelect = '';
        try { localStorage.setItem('vp-stage-height', stage.offsetHeight); } catch (e2) {}
        handle.removeEventListener('pointermove', onMove);
        handle.removeEventListener('pointerup',   onUp);
        handle.removeEventListener('pointercancel', onUp);
      }
      handle.addEventListener('pointermove', onMove);
      handle.addEventListener('pointerup',   onUp);
      handle.addEventListener('pointercancel', onUp);
    });
  })();

  // ===== STEP-BASED PANEL SCROLL (stdout / stderr / errors) =====
  var stepPanelFollowing = {};
  var stepScrollBusy     = {};   // true while a programmatic scroll is in flight

  function setStepPanelFollowing(contentId, enabled) {
    stepPanelFollowing[contentId] = enabled;
    if (enabled) scrollStepPanelToStep(contentId, shownStepIdx >= 0 ? shownStepIdx : 0);
  }

  function scrollStepPanelToStep(contentId, stepIdx) {
    if (stepPanelFollowing[contentId] === false) return;
    var content = document.getElementById(contentId);
    if (!content) return;
    content.querySelectorAll('.log-step-group').forEach(function (g) {
      g.classList.remove('step-current', 'step-previous');
    });
    // find the closest group at-or-before stepIdx (current) and the one just before it (previous)
    var best = null;
    var prev = null;
    content.querySelectorAll('.log-step-group[data-step]').forEach(function (g) {
      if (parseInt(g.dataset.step, 10) <= stepIdx) {
        prev = best;
        best = g;
      }
    });
    if (best) {
      best.classList.add('step-current');
      // Steps panel only: also mark the previous step and scroll so both stay in view
      if (contentId === 'vp-steps-content' && prev) prev.classList.add('step-previous');
      stepScrollBusy[contentId] = true;
      var anchor = (contentId === 'vp-steps-content' && prev) ? prev : best;
      var top = anchor.offsetTop - content.offsetTop;
      content.scrollTop = Math.max(0, top - 4);
      requestAnimationFrame(function () { stepScrollBusy[contentId] = false; });
    }
  }

  function scrollAllStepPanels(stepIdx) {
    ['vp-steps-content', 'vp-cucu-content', 'vp-stdout-content', 'vp-stderr-content', 'vp-errors-content'].forEach(function (id) {
      scrollStepPanelToStep(id, stepIdx);
    });
    updateStepsBreadcrumb(stepIdx);
  }

  // Show the current group header — the most recent heading at-or-before stepIdx (with its
  // raw `#` prefixes preserved). If no heading has been encountered yet, fall back to the scenario
  // name prefixed with "Scenario: ".
  function updateStepsBreadcrumb(stepIdx) {
    var bc = document.getElementById('steps-breadcrumb');
    if (!bc) return;
    var name = 'Scenario: ' + SCENARIO_NAME;
    for (var i = 0; i <= stepIdx && i < STEPS.length; i++) {
      if (STEPS[i].headingLevel) name = ((STEPS[i].keyword || '') + ' ' + STEPS[i].name).trim();
    }
    bc.innerHTML = '<div class="log-line"><span class="steps-name">' + escHtml(name) + '</span></div>';
  }

  function escHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  ['vp-steps-content', 'vp-cucu-content', 'vp-stdout-content', 'vp-stderr-content', 'vp-errors-content'].forEach(function (id) {
    stepPanelFollowing[id] = true;
  });

  // ===== STEP TIMING / PIC INDEX =====
  function padN(n, w) { var s = String(n); while (s.length < (w || 2)) s = '0' + s; return s; }
  function formatPlayheadTime(epochMs) {
    // Local time — matches the rest of the report (step timestamps, scenario start_at).
    var d = new Date(epochMs);
    return d.getFullYear() + '-' + padN(d.getMonth() + 1) + '-' + padN(d.getDate()) + ' ' +
           padN(d.getHours()) + ':' + padN(d.getMinutes()) + ':' + padN(d.getSeconds()) + '.' +
           padN(d.getMilliseconds(), 3) + '000';
  }
  function updateMetaTime() {
    var el = document.getElementById('vp-meta-time');
    if (!el) return;
    var cur = currentTimeSec.toFixed(1);
    var tot = SCENARIO_DURATION.toFixed(1);
    if (SCENARIO_START_MS === null) {
      el.textContent = '▶ ' + cur + ' / ' + tot + 's';
    } else {
      el.textContent = '▶ ' + formatPlayheadTime(SCENARIO_START_MS + currentTimeSec * 1000) + ' · ' + cur + ' / ' + tot + 's';
    }
  }

  // Each step contributes max(1, screenshots.length) — steps without screenshots (and skipped
  // steps) count as a single "frame" so they're navigable in the pic player.
  function stepFrameCount(s) { return Math.max(1, s.screenshots.length); }
  var PIC_OFFSETS = (function () {
    var offsets = []; var sum = 0;
    STEPS.forEach(function (s) { offsets.push(sum); sum += stepFrameCount(s); });
    return offsets;
  })();
  var TOTAL_PICS = PIC_OFFSETS.length ? PIC_OFFSETS[PIC_OFFSETS.length - 1] + stepFrameCount(STEPS[STEPS.length - 1]) : 0;

  // Whether we have enough real timing data to drive time-based playback
  var HAS_TIMING = SCENARIO_DURATION > 0 &&
    STEPS.some(function (s) { return s.startOffset !== null && s.duration > 0; });

  // Synthesise startOffset/duration for untimed (skipped/untested) steps so they integrate with
  // timeToStepIdx, the timeline, and the pic player exactly like timed steps. Each untimed step
  // gets a small inline slot right after the previous step ended.
  (function assignVirtualOffsets() {
    if (!HAS_TIMING) return;
    var untimedMarkerSec = SCENARIO_DURATION * 0.005;
    var lastEnd = 0;
    STEPS.forEach(function (s) {
      if (s.startOffset !== null) {
        lastEnd = s.startOffset + (s.duration || 0);
      } else {
        s.startOffset = lastEnd;
        s.duration    = untimedMarkerSec;
        lastEnd      += untimedMarkerSec;
      }
    });
  })();

  // Total playback range — actual end of the last step (no trailing slack against SCENARIO_DURATION).
  var PLAY_END = (function () {
    if (!HAS_TIMING) return Math.max(TOTAL_STEPS - 1, 0);
    var last = 0;
    STEPS.forEach(function (s) {
      if (s.startOffset !== null) last = Math.max(last, s.startOffset + (s.duration || 0));
    });
    return last > 0 ? last : SCENARIO_DURATION;
  })();

  // ===== STATE =====
  var currentTimeSec = 0;
  var shownStepIdx   = -1;
  var shownImgIdx    = -1;
  var isPlaying      = false;
  var playbackRate   = 1.0;
  var lastRafTime    = null;
  var rafId          = null;

  var browserFollowing   = true;
  var browserScrollBusy  = { value: false };
  var browserTimedLines  = null;

  function getBrowserTimedLines() {
    if (!browserTimedLines)
      browserTimedLines = Array.from(document.querySelectorAll('#vp-browser-content .log-line[data-offset]'));
    return browserTimedLines;
  }

  // ===== TIMELINE BUILDERS =====
  function buildStepPresenceTrack(trackId, stepHasContent) {
    var track = document.getElementById(trackId);
    if (!track) return;
    var totalDur = PLAY_END > 0 ? PLAY_END : 1;
    var cursor = track.firstElementChild;
    var hasAny = false;
    STEPS.forEach(function (step, i) {
      if (!stepHasContent(step)) return;
      hasAny = true;
      var bar = document.createElement('div');
      bar.className = 'tl-step-bar';
      if (HAS_TIMING && step.startOffset !== null && totalDur > 0) {
        bar.style.left  = (step.startOffset / totalDur * 100) + '%';
        bar.style.width = Math.max(0.5, step.duration / totalDur * 100) + '%';
      } else {
        bar.style.left  = (i / Math.max(TOTAL_STEPS, 1) * 100) + '%';
        bar.style.width = (100 / TOTAL_STEPS) + '%';
      }
      if (cursor) track.insertBefore(bar, cursor); else track.appendChild(bar);
    });
    if (hasAny) track.style.display = '';
  }

  function buildPicsTimeline() {
    // One tick per screenshot at its capture offset, plus a single tick for steps without screenshots
    // (skipped/untested/no-pic). Each tick is coloured by its step's status.
    var track = document.getElementById('pics-timeline-track');
    if (!track) return;
    var totalDur = PLAY_END > 0 ? PLAY_END : 1;
    STEPS.forEach(function (step) {
      if (step.startOffset === null) return;
      var n = Math.max(1, step.screenshots.length);
      var statusClass = 'pics-tick-' + (step.status || 'untested');
      for (var i = 0; i < n; i++) {
        var offset = step.startOffset + (i / n) * step.duration;
        var tick = document.createElement('div');
        tick.className = 'pics-tick ' + statusClass;
        tick.style.left = Math.max(0, Math.min(100, offset / totalDur * 100)) + '%';
        track.appendChild(tick);
      }
    });
    track.style.display = '';
  }

  function buildBrowserTimeline() {
    // One tick per browser log entry, coloured by severity (info / warning / error).
    var track = document.getElementById('browser-timeline-track');
    if (!track) return;
    var totalDur = PLAY_END > 0 ? PLAY_END : 1;
    var cursor = document.getElementById('browser-tl-cursor');
    var lines = getBrowserTimedLines();
    if (lines.length === 0) { track.style.display = 'none'; return; }
    lines.forEach(function (line) {
      var offset = parseFloat(line.dataset.offset);
      if (isNaN(offset)) return;
      var level = 'info';
      if (line.classList.contains('bl-error'))   level = 'error';
      else if (line.classList.contains('bl-warning')) level = 'warning';
      var tick = document.createElement('div');
      tick.className = 'tl-tick tl-' + level;
      tick.style.left = Math.max(0, Math.min(100, offset / totalDur * 100)) + '%';
      if (cursor) track.insertBefore(tick, cursor); else track.appendChild(tick);
    });
  }

  function buildTimeline() {
    var track = document.getElementById('timeline-track');
    var totalDur = HAS_TIMING ? PLAY_END : Math.max(TOTAL_STEPS - 1, 1);

    STEPS.forEach(function (step, i) {
      var bar = document.createElement('div');
      bar.id = 'bar-' + i;
      bar.className = 'step-bar status-' + (step.status || 'untested') + (step.isHeading ? ' heading' : '');
      bar.setAttribute('title', 'Step ' + step.num + ': ' + step.keyword + ' ' + step.name.slice(0, 80));
      bar.dataset.step = i;

      var leftPct, widthPct;
      if (HAS_TIMING) {
        // Every step has a (real or synthesised) startOffset+duration after assignVirtualOffsets
        leftPct  = step.startOffset / totalDur * 100;
        widthPct = Math.max(step.duration / totalDur * 100, 0.25);
      } else {
        leftPct  = (i / Math.max(TOTAL_STEPS - 1, 1)) * 100;
        widthPct = 100 / TOTAL_STEPS;
      }

      bar.style.left  = leftPct  + '%';
      bar.style.width = widthPct + '%';

      bar.addEventListener('click', function (e) {
        e.stopPropagation();
        seekToTime(HAS_TIMING ? step.startOffset : stepIdxToTime(i));
      });
      track.appendChild(bar);
    });
  }

  // Convert a step index to a player-time value. If this step has no startOffset, walk backwards
  // to the nearest step that does.
  function stepIdxToTime(idx) {
    if (!HAS_TIMING) return idx;
    for (var i = idx; i >= 0; i--) {
      if (STEPS[i].startOffset !== null) return STEPS[i].startOffset;
    }
    return 0;
  }

  // ===== TIME ↔ STEP RESOLUTION =====
  function timeToStepIdx(t) {
    if (!HAS_TIMING) return Math.min(Math.round(t), TOTAL_STEPS - 1);
    var best = 0;
    for (var i = 0; i < TOTAL_STEPS; i++) {
      var s = STEPS[i];
      if (s.startOffset !== null && s.startOffset <= t) best = i;
    }
    return best;
  }

  function timeToImgIdx(stepIdx, t) {
    var step = STEPS[stepIdx];
    var n = step.screenshots.length;
    if (n <= 1 || step.duration <= 0 || step.startOffset === null) return 0;
    var within = Math.max(0, t - step.startOffset);
    return Math.min(Math.floor(within / step.duration * n), n - 1);
  }

  // ===== SEEK & DISPLAY =====
  function seekToTime(t) {
    currentTimeSec = Math.max(0, Math.min(t, PLAY_END));
    reengageFollow();
    updateDisplay(true);
  }

  function reengageFollow() {
    browserFollowing = true;
    var bc = document.getElementById('browser-follow-chk'); if (bc) bc.checked = true;
    ['vp-steps-content', 'vp-cucu-content', 'vp-stdout-content', 'vp-stderr-content', 'vp-errors-content'].forEach(function (id) {
      stepPanelFollowing[id] = true;
    });
    var cc = document.getElementById('cucu-follow-chk'); if (cc) cc.checked = true;
  }

  function seekToStepIdx(idx) {
    seekToTime(stepIdxToTime(idx));
  }

  function updateDisplay(force) {
    var headPct = PLAY_END > 0 ? (currentTimeSec / PLAY_END) * 100 : 0;
    document.getElementById('timeline-playhead').style.left = headPct + '%';
    ['pics-tl-cursor', 'stdout-tl-cursor', 'cucu-tl-cursor', 'browser-tl-cursor'].forEach(function (id) {
      var el = document.getElementById(id); if (el) el.style.left = headPct + '%';
    });

    var stepIdx = timeToStepIdx(currentTimeSec);
    var imgIdx  = timeToImgIdx(stepIdx, currentTimeSec);

    var stepChanged = stepIdx !== shownStepIdx;
    var imgChanged  = imgIdx  !== shownImgIdx;

    if (stepChanged || force) {
      if (shownStepIdx >= 0) {
        document.getElementById('frame-' + shownStepIdx).style.display = 'none';
        var oldBar = document.getElementById('bar-' + shownStepIdx);
        if (oldBar) oldBar.classList.remove('active');
      }
      shownStepIdx = stepIdx;
      document.getElementById('frame-' + stepIdx).style.display = '';
      var newBar = document.getElementById('bar-' + stepIdx);
      if (newBar) newBar.classList.add('active');

      var step = STEPS[stepIdx];
      document.getElementById('step-cur').textContent = step.num;
      document.getElementById('step-timing-text').textContent = step.timingLabel;
      // Deliberate: replace (not push) so refresh / back-button lands on the right step.
      history.replaceState(null, '', '#step_' + step.num);
    }

    var atEnd = currentTimeSec >= PLAY_END;
    document.getElementById('btn-start').disabled       = (currentTimeSec <= 0);
    document.getElementById('btn-end').disabled         = atEnd;
    document.getElementById('step-nav-prev').disabled   = (stepIdx === 0 && currentTimeSec <= 0);
    document.getElementById('step-nav-next').disabled   = atEnd;
    // Play/Pause is only meaningful while the playhead can still advance — disable at PLAY_END
    document.getElementById('btn-play-pause').disabled = atEnd && !isPlaying;

    if (imgChanged || stepChanged) {
      if (STEPS[stepIdx].screenshots.length > 1) {
        setActiveScreenshot(stepIdx, imgIdx);
      } else {
        var picNav   = document.getElementById('step-pic-nav');
        var picCount = document.getElementById('pic-count');
        if (picNav)   picNav.classList.add('disabled');
        if (picCount) picCount.textContent = '– / –';
        setPicCaption(stepIdx, 0);
      }
      shownImgIdx = imgIdx;
    }

    scrollBrowserToTime(currentTimeSec);
    if (stepChanged) scrollAllStepPanels(stepIdx);

    updateMetaTime();
  }

  function setActiveScreenshot(frameIdx, imgIdx) {
    var wrappers = document.querySelectorAll('.screenshot-wrapper[data-frame="' + frameIdx + '"]');
    wrappers.forEach(function (w) { w.classList.remove('active'); });
    if (wrappers[imgIdx]) wrappers[imgIdx].classList.add('active');
    var picNav   = document.getElementById('step-pic-nav');
    var picCount = document.getElementById('pic-count');
    if (picNav && picCount) {
      if (wrappers.length > 1) {
        picCount.textContent = (imgIdx + 1) + ' / ' + wrappers.length;
        picNav.classList.remove('disabled');
      } else {
        picCount.textContent = '– / –';
        picNav.classList.add('disabled');
      }
    }
    setPicCaption(frameIdx, imgIdx);
  }

  function setPicCaption(frameIdx, imgIdx) {
    var caption = document.getElementById('pic-caption');
    if (caption) {
      var shots = (STEPS[frameIdx] && STEPS[frameIdx].screenshots) || [];
      var shot = shots[imgIdx];
      caption.textContent = shot ? (shot.label || '') : '';
    }
    var pill = document.getElementById('pic-overall-pill');
    if (pill) {
      if (TOTAL_PICS === 0) {
        pill.textContent = '– / –';
        pill.classList.add('disabled');
      } else {
        var shotsLen = (STEPS[frameIdx] && STEPS[frameIdx].screenshots.length) || 0;
        var clampedImgIdx = shotsLen > 1 ? Math.min(imgIdx, shotsLen - 1) : 0;
        var overall = (PIC_OFFSETS[frameIdx] || 0) + clampedImgIdx + 1;
        pill.textContent = overall + ' / ' + TOTAL_PICS;
        pill.classList.remove('disabled');
      }
    }
  }

  // ===== STEP NAVIGATION =====
  function navigateStep(delta) {
    // Stepping forward off the last step parks the playhead at the very end of the scenario
    if (delta > 0 && shownStepIdx >= TOTAL_STEPS - 1) { seekToTime(PLAY_END); return; }
    var next = Math.max(0, Math.min(shownStepIdx + delta, TOTAL_STEPS - 1));
    seekToStepIdx(next);
  }
  function goToEnd() { seekToTime(PLAY_END); }

  // ===== PLAYBACK ENGINE (requestAnimationFrame for smooth time-based play) =====
  function startPlay() {
    if (isPlaying) return;
    if (currentTimeSec >= PLAY_END) return;  // at end — user must manually rewind with ⏮
    isPlaying = true;
    lastRafTime = null;
    reengageFollow();
    document.getElementById('btn-play-pause').textContent = '⏸';
    rafId = requestAnimationFrame(playFrame);
  }

  function stopPlay() {
    isPlaying = false;
    if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    document.getElementById('btn-play-pause').textContent = '▶';
  }

  function togglePlay() { if (isPlaying) stopPlay(); else startPlay(); }

  function playFrame(rafTime) {
    if (!isPlaying) return;
    if (lastRafTime !== null) {
      currentTimeSec += (rafTime - lastRafTime) / 1000 * playbackRate;
      if (currentTimeSec >= PLAY_END) {
        currentTimeSec = PLAY_END;
        updateDisplay(false);
        stopPlay();
        return;
      }
    }
    lastRafTime = rafTime;
    updateDisplay(false);
    rafId = requestAnimationFrame(playFrame);
  }

  // ===== TIMELINE CLICK / DRAG =====
  // The same handler is wired to every track (steps + pics + stdout + cucu + browser + errors),
  // so resolve the rect against the track that actually received the event.
  function seekFromPointer(track, clientX) {
    var rect  = track.getBoundingClientRect();
    var ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    seekToTime(ratio * PLAY_END);
  }

  function attachTimelineDrag(track) {
    track.addEventListener('pointerdown', function (e) {
      e.preventDefault();
      track.setPointerCapture(e.pointerId);
      seekFromPointer(track, e.clientX);
      function onMove(ev) { seekFromPointer(track, ev.clientX); }
      function onUp() {
        track.removeEventListener('pointermove', onMove);
        track.removeEventListener('pointerup',   onUp);
        track.removeEventListener('pointercancel', onUp);
      }
      track.addEventListener('pointermove', onMove);
      track.addEventListener('pointerup',   onUp);
      track.addEventListener('pointercancel', onUp);
    });
  }

  // ===== TRANSCRIPT SYNC =====
  function scrollTranscriptToTime(containerId, timedLines, busyFlag, following) {
    if (!following) return;
    if (timedLines.length === 0) return;
    var lo = 0, hi = timedLines.length - 1, best = 0;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      if (parseFloat(timedLines[mid].dataset.offset) <= currentTimeSec) { best = mid; lo = mid + 1; }
      else { hi = mid - 1; }
    }
    var target = timedLines[best];
    var container = document.getElementById(containerId);
    if (!container) return;
    var prev = container.querySelector('.log-current');
    if (prev === target) return;
    if (prev) prev.classList.remove('log-current');
    target.classList.add('log-current');
    busyFlag.value = true;
    var containerRect = container.getBoundingClientRect();
    var lineRect      = target.getBoundingClientRect();
    container.scrollTop += (lineRect.top - containerRect.top) - Math.floor(container.clientHeight * 0.33);
    requestAnimationFrame(function () { busyFlag.value = false; });
  }

  function setBrowserFollowing(enabled) {
    browserFollowing = enabled;
    if (enabled) scrollBrowserToTime(currentTimeSec);
  }
  function scrollBrowserToTime() {
    scrollTranscriptToTime('vp-browser-content', getBrowserTimedLines(), browserScrollBusy, browserFollowing);
  }

  // ===== MANUAL SCREENSHOT CAROUSEL =====
  function shiftScreenshot(delta) {
    var frameIdx = shownStepIdx;
    var wrappers = Array.from(document.querySelectorAll('.screenshot-wrapper[data-frame="' + frameIdx + '"]'));
    var n   = wrappers.length;
    var cur = n > 0 ? wrappers.findIndex(function (w) { return w.classList.contains('active'); }) : -1;
    if (cur < 0) cur = 0;

    var next = cur + delta;

    if (next >= 0 && next < n) {
      // ── within the same step ──
      var step = STEPS[frameIdx];
      if (HAS_TIMING && step.startOffset !== null && step.duration > 0 && n > 1) {
        // Use midpoint of the screenshot's time slot to avoid floating-point edge cases where
        // (next/n)*n rounds down to next-1 inside timeToImgIdx.
        seekToTime(step.startOffset + ((next + 0.5) / n) * step.duration);
      } else {
        setActiveScreenshot(frameIdx, next);
        shownImgIdx = next;
      }
      return;
    }

    if (delta > 0) {
      // ── forward: first screenshot of the next step that has any ──
      for (var siF = frameIdx + 1; siF < TOTAL_STEPS; siF++) {
        if (STEPS[siF].screenshots.length > 0) { seekToStepIdx(siF); return; }
      }
    } else {
      // ── backward: last screenshot of the previous step that has any ──
      for (var siB = frameIdx - 1; siB >= 0; siB--) {
        var m = STEPS[siB].screenshots.length;
        if (m > 0) {
          var s = STEPS[siB];
          if (HAS_TIMING && s.startOffset !== null && s.duration > 0 && m > 1) {
            seekToTime(s.startOffset + ((m - 0.5) / m) * s.duration);
          } else {
            seekToStepIdx(siB);
          }
          return;
        }
      }
      seekToTime(0);  // before the first step with screenshots
    }
  }

  // ===== HIGHLIGHT TOGGLE =====
  function toggleHighlight() {
    var chk = document.getElementById('btn-highlight');
    document.body.classList.toggle('hide-highlights', !!(chk && !chk.checked));
  }

  // ===== EVENT WIRING =====
  function on(id, event, fn) {
    var el = document.getElementById(id);
    if (el) el.addEventListener(event, fn);
  }

  on('theme-toggle', 'click', cycleTheme);

  on('btn-start',      'click', function () { seekToTime(0); });
  on('btn-play-pause', 'click', togglePlay);
  on('btn-end',        'click', goToEnd);
  on('step-nav-prev',  'click', function () { navigateStep(-1); });
  on('step-nav-next',  'click', function () { navigateStep(1); });
  on('stage-btn-prev', 'click', function () { shiftScreenshot(-1); });
  on('stage-btn-next', 'click', function () { shiftScreenshot(1); });

  document.querySelectorAll('.step-pic-nav-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      shiftScreenshot(parseInt(btn.dataset.delta, 10) || 0);
    });
  });

  on('btn-highlight', 'change', toggleHighlight);
  on('browser-follow-chk', 'change', function (e) { setBrowserFollowing(e.target.checked); });
  [
    ['steps-follow-chk',  'vp-steps-content'],
    ['cucu-follow-chk',   'vp-cucu-content'],
    ['stdout-follow-chk', 'vp-stdout-content'],
    ['stderr-follow-chk', 'vp-stderr-content'],
    ['errors-follow-chk', 'vp-errors-content'],
  ].forEach(function (pair) {
    on(pair[0], 'change', function (e) { setStepPanelFollowing(pair[1], e.target.checked); });
  });

  // Log panel collapse toggles
  document.querySelectorAll('[data-log-toggle]').forEach(function (el) {
    el.addEventListener('click', function () { toggleLogPanel(el.dataset.logToggle); });
  });

  // Steps list click-to-seek (scenario row, plus each step row)
  document.querySelectorAll('[data-seek-step]').forEach(function (row) {
    row.addEventListener('click', function () { seekToStepIdx(parseInt(row.dataset.seekStep, 10)); });
  });
  var scenarioRow = document.querySelector('[data-seek-time]');
  if (scenarioRow) scenarioRow.addEventListener('click', function () { seekToTime(parseFloat(scenarioRow.dataset.seekTime) || 0); });

  // Timeline tracks
  ['timeline-track', 'pics-timeline-track', 'stdout-timeline-track', 'cucu-timeline-track', 'browser-timeline-track', 'errors-timeline-track'].forEach(function (id) {
    var t = document.getElementById(id); if (t) attachTimelineDrag(t);
  });

  // Logs dropdown — clicking the trigger toggles, clicking outside closes
  on('log-menu-trigger', 'click', function (e) {
    e.preventDefault();
    var dd = document.getElementById('log-dd');
    if (dd) dd.classList.toggle('open');
  });
  document.addEventListener('click', function (e) {
    var wrap = document.getElementById('log-menu-wrap');
    var dd   = document.getElementById('log-dd');
    if (dd && wrap && !wrap.contains(e.target)) dd.classList.remove('open');
  });

  // Transcript scroll → disable follow-mode on user scroll
  (function attachTranscriptScrollListeners() {
    var bc = document.getElementById('vp-browser-content');
    if (bc) {
      bc.addEventListener('scroll', function () {
        if (browserScrollBusy.value) return;
        setBrowserFollowing(false);
        var chk = document.getElementById('browser-follow-chk');
        if (chk) chk.checked = false;
      }, { passive: true });
    }

    function makeStepListener(contentId, chkId) {
      return function () {
        if (stepScrollBusy[contentId]) return;
        setStepPanelFollowing(contentId, false);
        var chk = document.getElementById(chkId);
        if (chk) chk.checked = false;
      };
    }

    [
      ['vp-steps-content',  'steps-follow-chk'],
      ['vp-cucu-content',   'cucu-follow-chk'],
      ['vp-stdout-content', 'stdout-follow-chk'],
      ['vp-stderr-content', 'stderr-follow-chk'],
      ['vp-errors-content', 'errors-follow-chk'],
    ].forEach(function (pair) {
      var el = document.getElementById(pair[0]);
      if (el) el.addEventListener('scroll', makeStepListener(pair[0], pair[1]), { passive: true });
    });
  })();

  // ===== KEYBOARD SHORTCUTS =====
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    switch (e.key) {
      case 'ArrowLeft':  e.preventDefault(); shiftScreenshot(-1);   break;
      case 'ArrowRight': e.preventDefault(); shiftScreenshot(1);    break;
      case ' ':          e.preventDefault(); togglePlay();          break;
      case 'Home':       e.preventDefault(); seekToStepIdx(0);      break;
      case 'End':        e.preventDefault(); goToEnd();             break;
    }
  });

  // Firefox defers `loading="lazy"` images until they near the viewport, but in this report the
  // hidden step frames never trigger that intersection check until shown — by then the user has
  // already advanced past them. Force eager loading on Firefox so screenshots are ready when seeked.
  if (navigator.userAgent.toLowerCase().indexOf('firefox') > -1) {
    document.querySelectorAll('img[loading="lazy"]').forEach(function (img) { img.setAttribute('loading', 'eager'); });
  }

  // ===== INIT =====
  buildTimeline();
  buildPicsTimeline();
  buildStepPresenceTrack('stdout-timeline-track', function (s) { return s.hasStdout; });
  buildStepPresenceTrack('cucu-timeline-track',   function (s) { return s.hasCucu; });
  buildStepPresenceTrack('errors-timeline-track', function (s) { return s.hasErrors; });
  buildBrowserTimeline();

  var startTime = 0;
  var hash = window.location.hash;
  if (hash && hash.indexOf('#step_') === 0) {
    var n = parseInt(hash.replace('#step_', ''), 10);
    if (!isNaN(n) && n >= 1 && n <= TOTAL_STEPS) {
      startTime = stepIdxToTime(n - 1);
    }
  } else {
    var failIdx = STEPS.findIndex(function (s) { return s.status === 'failed' || s.status === 'errored'; });
    if (failIdx >= 0) startTime = stepIdxToTime(failIdx);
  }
  seekToTime(startTime);
})();
