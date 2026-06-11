// Cucu replay-view player. Companion CSS: replay.css. Per-scenario data — including all log
// content — comes from the inline JSON island at #replay-data; the player is wired up
// declaratively via Alpine.js (x-data="replayPlayer()").
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
  var BROWSER_LOGS      = DATA.browserLogs || [];
  var TOTAL_STEPS       = STEPS.length;

  function stepFrameCount(s) { return Math.max(1, s.screenshots.length); }

  var PIC_OFFSETS = STEPS.reduce(function (acc, s) {
    acc.push(acc.length ? acc[acc.length - 1] + stepFrameCount(STEPS[acc.length - 1]) : 0);
    return acc;
  }, []);
  var TOTAL_PICS = PIC_OFFSETS.length ? PIC_OFFSETS[PIC_OFFSETS.length - 1] + stepFrameCount(STEPS[STEPS.length - 1]) : 0;

  var HAS_TIMING = SCENARIO_DURATION > 0 &&
    STEPS.some(function (s) { return s.startOffset !== null && s.duration > 0; });

  // Synthesise startOffset/duration for untimed (skipped/untested) steps so they integrate with
  // timeToStepIdx, the timeline, and the pic player exactly like timed steps.
  (function () {
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

  var PLAY_END = HAS_TIMING
    ? STEPS.reduce(function (m, s) { return s.startOffset !== null ? Math.max(m, s.startOffset + (s.duration || 0)) : m; }, 0) || SCENARIO_DURATION
    : Math.max(TOTAL_STEPS - 1, 0);
  var TOTAL_DUR = PLAY_END > 0 ? PLAY_END : 1;

  // ----- Precomputed tick / bar arrays — bound via <template x-for> in markup. -----
  var STEP_BARS = STEPS.map(function (step, i) {
    var leftPct = HAS_TIMING ? step.startOffset / TOTAL_DUR * 100 : i / Math.max(TOTAL_STEPS - 1, 1) * 100;
    var widthPct = HAS_TIMING ? Math.max(step.duration / TOTAL_DUR * 100, 0.25) : 100 / TOTAL_STEPS;
    return {
      index:    i,
      leftPct:  leftPct,
      widthPct: widthPct,
      cls:      'status-' + (step.status || 'untested') + (step.isHeading ? ' heading' : ''),
      title:    'Step ' + step.num + ': ' + step.keyword + ' ' + step.name.slice(0, 80),
      seekTime: HAS_TIMING ? step.startOffset : i,
    };
  });

  var PIC_TICKS = STEPS.reduce(function (acc, step) {
    if (step.startOffset === null) return acc;
    var n = Math.max(1, step.screenshots.length);
    for (var i = 0; i < n; i++) {
      acc.push({
        cls: 'pics-tick pics-tick-' + (step.status || 'untested'),
        leftPct: Math.max(0, Math.min(100, (step.startOffset + (i / n) * step.duration) / TOTAL_DUR * 100)),
      });
    }
    return acc;
  }, []);

  function buildPresenceBars(predicate) {
    return STEPS.reduce(function (acc, step, i) {
      if (!predicate(step)) return acc;
      var leftPct  = HAS_TIMING ? step.startOffset / TOTAL_DUR * 100 : i / Math.max(TOTAL_STEPS, 1) * 100;
      var widthPct = HAS_TIMING ? Math.max(0.5, step.duration / TOTAL_DUR * 100) : 100 / TOTAL_STEPS;
      acc.push({ leftPct: leftPct, widthPct: widthPct });
      return acc;
    }, []);
  }
  var STDOUT_BARS = buildPresenceBars(function (s) { return s.stdout && s.stdout.length; });
  var CUCU_BARS   = buildPresenceBars(function (s) { return !!s.debugOutput; });
  var ERRORS_BARS = buildPresenceBars(function (s) { return s.errorMessage && s.errorMessage.length; });

  var BROWSER_TICKS = BROWSER_LOGS.map(function (log) {
    return { leftPct: Math.max(0, Math.min(100, log.offset / TOTAL_DUR * 100)), level: log.level };
  });

  var STEP_PANELS = [
    { contentId: 'vp-steps-content',  followId: 'steps-follow-chk',  field: null },
    { contentId: 'vp-cucu-content',   followId: 'cucu-follow-chk',   field: 'debugOutput' },
    { contentId: 'vp-stdout-content', followId: 'stdout-follow-chk', field: 'stdout' },
    { contentId: 'vp-stderr-content', followId: 'stderr-follow-chk', field: 'stderr' },
    { contentId: 'vp-errors-content', followId: 'errors-follow-chk', field: 'errorMessage' },
  ];
  var FOLLOW_IDS = ['browser-follow-chk'].concat(STEP_PANELS.map(function (p) { return p.followId; }));

  var PANEL_IDS = [
    'vp-pics-panel', 'vp-steps-panel', 'vp-cucu-panel', 'vp-browser-panel',
    'vp-stdout-panel', 'vp-stderr-panel', 'vp-errors-panel',
  ];

  var RESIZE_TARGETS = [
    ['vp-stage',           120, 'vp-stage-height'],
    ['vp-steps-content',    60, 'vp-vp-steps-panel-height'],
    ['vp-cucu-content',     60, 'vp-vp-cucu-panel-height'],
    ['vp-browser-content',  60, 'vp-vp-browser-panel-height'],
    ['vp-stdout-content',   60, 'vp-vp-stdout-panel-height'],
    ['vp-stderr-content',   60, 'vp-vp-stderr-panel-height'],
    ['vp-errors-content',   60, 'vp-vp-errors-panel-height'],
  ];

  var THEME_CYCLE  = ['auto', 'light', 'dark'];
  var THEME_ICONS  = { auto: '🖥', light: '☀', dark: '🌙' };
  var THEME_TITLES = { auto: 'Theme: auto (follows system)', light: 'Theme: light', dark: 'Theme: dark' };

  function padN(n, w) { var s = String(n); while (s.length < (w || 2)) s = '0' + s; return s; }
  function formatPlayheadTime(epochMs) {
    var d = new Date(epochMs);
    return d.getFullYear() + '-' + padN(d.getMonth() + 1) + '-' + padN(d.getDate()) + ' ' +
           padN(d.getHours()) + ':' + padN(d.getMinutes()) + ':' + padN(d.getSeconds()) + '.' +
           padN(d.getMilliseconds(), 3) + '000';
  }

  function stepIdxToTime(idx) {
    if (!HAS_TIMING) return idx;
    for (var i = idx; i >= 0; i--) {
      if (STEPS[i].startOffset !== null) return STEPS[i].startOffset;
    }
    return 0;
  }
  function timeToStepIdx(t) {
    if (!HAS_TIMING) return Math.min(Math.round(t), TOTAL_STEPS - 1);
    var best = 0;
    for (var i = 0; i < TOTAL_STEPS; i++) {
      if (STEPS[i].startOffset !== null && STEPS[i].startOffset <= t) best = i;
    }
    return best;
  }
  function timeToImgIdx(stepIdx, t) {
    var step = STEPS[stepIdx];
    var n = step.screenshots.length;
    if (n <= 1 || step.duration <= 0 || step.startOffset === null) return 0;
    return Math.min(Math.floor(Math.max(0, t - step.startOffset) / step.duration * n), n - 1);
  }

  function readTheme() {
    try { return localStorage.getItem('vp-theme') || 'auto'; } catch (e) { return 'auto'; }
  }
  function applyThemeClass(mode) {
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.classList.toggle('theme-dark', mode === 'dark' || (mode === 'auto' && prefersDark));
  }

  function panelByFollowId(followId) {
    for (var i = 0; i < STEP_PANELS.length; i++) if (STEP_PANELS[i].followId === followId) return STEP_PANELS[i];
    return null;
  }
  function panelByContentId(contentId) {
    for (var i = 0; i < STEP_PANELS.length; i++) if (STEP_PANELS[i].contentId === contentId) return STEP_PANELS[i];
    return null;
  }

  // ===== ALPINE COMPONENT =====
  window.replayPlayer = function () {
    return {
      // ----- bound state -----
      steps:           STEPS,
      totalSteps:      TOTAL_STEPS,
      totalPics:       TOTAL_PICS,
      stepBars:        STEP_BARS,
      picTicks:        PIC_TICKS,
      stdoutBars:      STDOUT_BARS,
      cucuBars:        CUCU_BARS,
      errorsBars:      ERRORS_BARS,
      browserTicks:    BROWSER_TICKS,
      browserLogs:     BROWSER_LOGS,
      cucuSteps:       STEPS.filter(function (s) { return !!s.debugOutput; }),
      stdoutSteps:     STEPS.filter(function (s) { return s.stdout && s.stdout.length; }),
      stderrSteps:     STEPS.filter(function (s) { return s.stderr && s.stderr.length; }),
      errorSteps:      STEPS.filter(function (s) { return s.errorMessage && s.errorMessage.length; }),
      currentTimeSec:  0,
      shownStepIdx:    -1,
      shownImgIdx:     -1,
      isPlaying:       false,
      playbackRate:    1.0,
      theme:           'auto',
      highlight:       true,
      logsOpen:        false,
      panelsCollapsed: {},
      followFlags:     {},
      themeIcons:      THEME_ICONS,
      themeTitles:     THEME_TITLES,

      // ----- unbound internals -----
      _rafId:             null,
      _lastRafTime:       null,
      _browserLineEls:    null,
      _stepScrollBusy:    {},
      _browserScrollBusy: { value: false },

      // ----- derived (getters) -----
      get headPct()       { return this.currentTimeSec / TOTAL_DUR * 100; },
      get atEnd()         { return this.currentTimeSec >= PLAY_END; },
      get curStep()       { return this.shownStepIdx >= 0 ? this.steps[this.shownStepIdx] : null; },
      get hasMultiplePics() { return !!(this.curStep && this.curStep.screenshots.length > 1); },
      get picCaption()    {
        var s = this.curStep;
        return s && s.screenshots[this.shownImgIdx] ? (s.screenshots[this.shownImgIdx].label || '') : '';
      },
      get picCountText()  {
        var s = this.curStep;
        return s && s.screenshots.length > 1 ? (this.shownImgIdx + 1) + ' / ' + s.screenshots.length : '– / –';
      },
      get picOverallText(){
        if (TOTAL_PICS === 0 || !this.curStep) return '– / –';
        var n = this.curStep.screenshots.length;
        var clamped = n > 1 ? Math.min(this.shownImgIdx, n - 1) : 0;
        return ((PIC_OFFSETS[this.shownStepIdx] || 0) + clamped + 1) + ' / ' + TOTAL_PICS;
      },
      get metaTimeText()  {
        var cur = this.currentTimeSec.toFixed(1), tot = SCENARIO_DURATION.toFixed(1);
        if (SCENARIO_START_MS === null) return '▶ ' + cur + ' / ' + tot + 's';
        return '▶ ' + formatPlayheadTime(SCENARIO_START_MS + this.currentTimeSec * 1000) + ' · ' + cur + ' / ' + tot + 's';
      },
      get breadcrumbText() {
        var name = 'Scenario: ' + SCENARIO_NAME;
        for (var i = 0; i <= Math.max(0, this.shownStepIdx) && i < this.steps.length; i++) {
          if (this.steps[i].headingLevel) name = ((this.steps[i].keyword || '') + ' ' + this.steps[i].name).trim();
        }
        return name;
      },
      get playPauseDisabled() { return this.atEnd && !this.isPlaying; },
      get stepPrevDisabled()  { return this.shownStepIdx === 0 && this.currentTimeSec <= 0; },
      get startDisabled()     { return this.currentTimeSec <= 0; },

      // Used by .log-step-group :class bindings — returns the highest step index <= shownStepIdx
      // whose given field is truthy. (e.g. 'debugOutput', 'stdout', 'stderr', 'errorMessage')
      currentStepFor(field) {
        for (var i = this.shownStepIdx; i >= 0; i--) {
          if (this.steps[i][field]) return i;
        }
        return -1;
      },

      // ===== INIT =====
      init() {
        var self = this;

        this.theme = readTheme();
        if (window.matchMedia) {
          window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
            if (self.theme === 'auto') applyThemeClass('auto');
          });
        }

        this.applyHighlightClass();

        PANEL_IDS.forEach(function (pid) {
          try { self.panelsCollapsed[pid] = localStorage.getItem('vp-' + pid + '-collapsed') === '1'; }
          catch (e) {}
        });
        FOLLOW_IDS.forEach(function (fid) { self.followFlags[fid] = true; });

        RESIZE_TARGETS.forEach(function (t) {
          var target = document.getElementById(t[0]);
          if (!target) return;
          try {
            var h = parseInt(localStorage.getItem(t[2]), 10);
            if (h >= t[1]) target.style.height = h + 'px';
          } catch (e) {}
        });

        if (navigator.userAgent.toLowerCase().indexOf('firefox') > -1) {
          document.querySelectorAll('img[loading="lazy"]').forEach(function (img) {
            img.setAttribute('loading', 'eager');
          });
        }

        var startTime = 0;
        var hash = window.location.hash;
        if (hash && hash.indexOf('#step_') === 0) {
          var n = parseInt(hash.replace('#step_', ''), 10);
          if (!isNaN(n) && n >= 1 && n <= TOTAL_STEPS) startTime = stepIdxToTime(n - 1);
        } else {
          var failIdx = STEPS.findIndex(function (s) { return s.status === 'failed' || s.status === 'errored'; });
          if (failIdx >= 0) startTime = stepIdxToTime(failIdx);
        }
        this.seekToTime(startTime);
      },

      // ===== ACTIONS =====
      cycleTheme() {
        var next = THEME_CYCLE[(THEME_CYCLE.indexOf(this.theme) + 1) % THEME_CYCLE.length];
        try { localStorage.setItem('vp-theme', next); } catch (e) {}
        this.theme = next;
        applyThemeClass(next);
      },

      applyHighlightClass() {
        document.body.classList.toggle('hide-highlights', !this.highlight);
      },

      togglePanel(panelId) {
        var next = !this.panelsCollapsed[panelId];
        this.panelsCollapsed[panelId] = next;
        try { localStorage.setItem('vp-' + panelId + '-collapsed', next ? '1' : '0'); } catch (e) {}
      },

      onFollowChange(followId) {
        if (!this.followFlags[followId]) return;
        if (followId === 'browser-follow-chk') { this._scrollBrowserToTime(); return; }
        var p = panelByFollowId(followId);
        if (p) this._scrollStepPanel(p.contentId, p.followId);
      },

      _reengageFollow() {
        var self = this;
        FOLLOW_IDS.forEach(function (fid) { self.followFlags[fid] = true; });
      },

      seekToTime(t) {
        this.currentTimeSec = Math.max(0, Math.min(t, PLAY_END));
        this._reengageFollow();
        this._updateDisplay(true);
      },
      seekToStepIdx(idx) { this.seekToTime(stepIdxToTime(idx)); },
      navigateStep(delta) {
        if (delta > 0 && this.shownStepIdx >= TOTAL_STEPS - 1) { this.seekToTime(PLAY_END); return; }
        this.seekToStepIdx(Math.max(0, Math.min(this.shownStepIdx + delta, TOTAL_STEPS - 1)));
      },
      goToEnd() { this.seekToTime(PLAY_END); },

      togglePlay() { if (this.isPlaying) this._stopPlay(); else this._startPlay(); },
      _startPlay() {
        if (this.isPlaying || this.currentTimeSec >= PLAY_END) return;
        this.isPlaying = true;
        this._lastRafTime = null;
        this._reengageFollow();
        var self = this;
        this._rafId = requestAnimationFrame(function (t) { self._playFrame(t); });
      },
      _stopPlay() {
        this.isPlaying = false;
        if (this._rafId) { cancelAnimationFrame(this._rafId); this._rafId = null; }
      },
      _playFrame(rafTime) {
        if (!this.isPlaying) return;
        if (this._lastRafTime !== null) {
          this.currentTimeSec += (rafTime - this._lastRafTime) / 1000 * this.playbackRate;
          if (this.currentTimeSec >= PLAY_END) {
            this.currentTimeSec = PLAY_END;
            this._updateDisplay(false);
            this._stopPlay();
            return;
          }
        }
        this._lastRafTime = rafTime;
        this._updateDisplay(false);
        var self = this;
        this._rafId = requestAnimationFrame(function (t) { self._playFrame(t); });
      },

      shiftScreenshot(delta) {
        var frameIdx = this.shownStepIdx;
        if (frameIdx < 0) return;
        var step = this.steps[frameIdx];
        var n = step.screenshots.length;
        var next = (this.shownImgIdx < 0 ? 0 : this.shownImgIdx) + delta;

        if (next >= 0 && next < n) {
          if (HAS_TIMING && step.startOffset !== null && step.duration > 0 && n > 1) {
            this.seekToTime(step.startOffset + ((next + 0.5) / n) * step.duration);
          } else {
            this.shownImgIdx = next;
            this._updateDisplay(false);
          }
          return;
        }

        var dir = delta > 0 ? 1 : -1;
        for (var i = frameIdx + dir; i >= 0 && i < TOTAL_STEPS; i += dir) {
          var m = this.steps[i].screenshots.length;
          var s = this.steps[i];
          if (m > 0 && HAS_TIMING && s.startOffset !== null && s.duration > 0) {
            if (dir < 0) {
              this.seekToTime(s.startOffset + ((m - 0.5) / m) * s.duration);
            } else {
              this.seekToTime(s.startOffset);
            }
          } else {
            this.seekToStepIdx(i);
          }
          return;
        }
        if (dir < 0) this.seekToTime(0);
      },

      // ===== DISPLAY UPDATE =====
      _updateDisplay(force) {
        var stepIdx = timeToStepIdx(this.currentTimeSec);
        var imgIdx  = timeToImgIdx(stepIdx, this.currentTimeSec);
        var stepChanged = stepIdx !== this.shownStepIdx;
        if (stepChanged || force) {
          this.shownStepIdx = stepIdx;
          history.replaceState(null, '', '#step_' + this.steps[stepIdx].num);
        }
        if (imgIdx !== this.shownImgIdx || stepChanged || force) {
          this.shownImgIdx = this.steps[stepIdx].screenshots.length > 1 ? imgIdx : 0;
        }
        this._scrollBrowserToTime();
        if (stepChanged || force) {
          var self = this;
          STEP_PANELS.forEach(function (p) { self._scrollStepPanel(p.contentId, p.followId); });
        }
      },

      // ===== STEP-PANEL SCROLL (class toggling is done declaratively via :class bindings) =====
      _scrollStepPanel(contentId, followId) {
        if (!this.followFlags[followId]) return;
        var content = document.getElementById(contentId);
        if (!content) return;
        var anchorIdx;
        if (contentId === 'vp-steps-content') {
          anchorIdx = this.shownStepIdx > 0 ? this.shownStepIdx - 1 : this.shownStepIdx;
        } else {
          var p = panelByContentId(contentId);
          anchorIdx = p && p.field ? this.currentStepFor(p.field) : this.shownStepIdx;
        }
        if (anchorIdx < 0) return;
        var anchor = content.querySelector('.log-step-group[data-step="' + anchorIdx + '"]');
        if (!anchor) return;
        this._stepScrollBusy[contentId] = true;
        content.scrollTop = Math.max(0, anchor.offsetTop - content.offsetTop - 4);
        var self = this;
        requestAnimationFrame(function () { self._stepScrollBusy[contentId] = false; });
      },

      // ===== BROWSER TRANSCRIPT SYNC (binary search over BROWSER_LOGS) =====
      _scrollBrowserToTime() {
        if (!this.followFlags['browser-follow-chk']) return;
        if (BROWSER_LOGS.length === 0) return;
        var lo = 0, hi = BROWSER_LOGS.length - 1, best = 0;
        while (lo <= hi) {
          var mid = (lo + hi) >> 1;
          if (BROWSER_LOGS[mid].offset <= this.currentTimeSec) { best = mid; lo = mid + 1; }
          else { hi = mid - 1; }
        }
        var container = document.getElementById('vp-browser-content');
        if (!container) return;
        if (!this._browserLineEls) {
          this._browserLineEls = container.querySelectorAll('.browser-log-line');
        }
        var target = this._browserLineEls[best];
        if (!target) return;
        var prev = container.querySelector('.log-current');
        if (prev === target) return;
        if (prev) prev.classList.remove('log-current');
        target.classList.add('log-current');
        this._browserScrollBusy.value = true;
        container.scrollTop += (target.getBoundingClientRect().top - container.getBoundingClientRect().top) -
                              Math.floor(container.clientHeight * 0.33);
        var self = this;
        requestAnimationFrame(function () { self._browserScrollBusy.value = false; });
      },

      // ===== EVENT HANDLERS (bound via Alpine @-directives in markup) =====
      onTimelineDrag(e) {
        var track = e.currentTarget, self = this;
        e.preventDefault();
        track.setPointerCapture(e.pointerId);
        function seek(x) {
          var r = track.getBoundingClientRect();
          self.seekToTime(Math.max(0, Math.min(1, (x - r.left) / r.width)) * PLAY_END);
        }
        seek(e.clientX);
        function onMove(ev) { seek(ev.clientX); }
        function onUp() {
          track.removeEventListener('pointermove', onMove);
          track.removeEventListener('pointerup',   onUp);
          track.removeEventListener('pointercancel', onUp);
        }
        track.addEventListener('pointermove', onMove);
        track.addEventListener('pointerup',   onUp);
        track.addEventListener('pointercancel', onUp);
      },

      onResizeDrag(e, targetId, minH, storageKey) {
        var target = document.getElementById(targetId);
        if (!target) return;
        var handle = e.currentTarget;
        e.preventDefault();
        handle.setPointerCapture(e.pointerId);
        var startY = e.clientY, startH = target.offsetHeight;
        handle.classList.add('dragging');
        document.body.style.cursor    = 'ns-resize';
        document.body.style.userSelect = 'none';
        function onMove(ev) {
          target.style.height = Math.max(minH, startH + (ev.clientY - startY)) + 'px';
        }
        function onUp() {
          handle.classList.remove('dragging');
          document.body.style.cursor    = '';
          document.body.style.userSelect = '';
          try { localStorage.setItem(storageKey, target.offsetHeight); } catch (e2) {}
          handle.removeEventListener('pointermove', onMove);
          handle.removeEventListener('pointerup',   onUp);
          handle.removeEventListener('pointercancel', onUp);
        }
        handle.addEventListener('pointermove', onMove);
        handle.addEventListener('pointerup',   onUp);
        handle.addEventListener('pointercancel', onUp);
      },

      onLogScroll(contentId, followId) {
        if (contentId === 'vp-browser-content') {
          if (this._browserScrollBusy.value) return;
        } else if (this._stepScrollBusy[contentId]) return;
        this.followFlags[followId] = false;
      },

      onKey(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        switch (e.key) {
          case 'ArrowLeft':  e.preventDefault(); this.shiftScreenshot(-1); break;
          case 'ArrowRight': e.preventDefault(); this.shiftScreenshot(1);  break;
          case ' ':          e.preventDefault(); this.togglePlay();        break;
          case 'Home':       e.preventDefault(); this.seekToStepIdx(0);    break;
          case 'End':        e.preventDefault(); this.goToEnd();           break;
        }
      },
    };
  };
})();
