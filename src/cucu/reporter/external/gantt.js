document.addEventListener("DOMContentLoaded", function () {
    var gantt = document.querySelector(".gantt");
    if (!gantt) return;

    var MIN_ZOOM = 1;
    var MAX_ZOOM = 64;
    var TICK_MIN_PX = 90;
    var TICK_STEPS = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600, 7200, 14400];

    var scroller = document.querySelector(".gantt-scroll");
    var axisTrack = gantt.querySelector(".gantt-axis-track");
    var spacer = gantt.querySelector(".gantt-label-spacer");
    var workerHeader = gantt.querySelector(".gantt-worker-header");
    var resizer = gantt.querySelector(".gantt-resizer");
    var LABEL_W_DEFAULT = 320;
    var LABEL_W_MIN = 120;
    var LABEL_W_KEY = "cucu-gantt-label-width";
    var rows = Array.prototype.slice.call(gantt.querySelectorAll(".gantt-row"));
    var bars = rows.map(function (row) { return row.querySelector(".gantt-bar"); });
    var statusChips = Array.prototype.slice.call(document.querySelectorAll(".gantt-status-chip"));
    var workerChips = Array.prototype.slice.call(document.querySelectorAll(".gantt-worker-chip"));
    var alignButton = document.querySelector(".gantt-align");
    var cleanupChip = document.querySelector(".gantt-cleanup-chip");
    var inners = bars.map(function (bar) { return bar.querySelector(".gantt-bar-inner"); });
    var showCleanup = true;
    var search = document.querySelector(".gantt-search");
    var shown = document.querySelector(".gantt-shown");
    var zoomLevel = document.querySelector(".gantt-zoom-level");

    var clockSpanS = parseFloat(gantt.getAttribute("data-span-s"));
    var alignedSpanS = parseFloat(gantt.getAttribute("data-aligned-span-s"));
    var clockStartS = parseFloat(gantt.getAttribute("data-run-start-clock-s"));
    var aligned = false;
    var spanS = clockSpanS;
    var zoom = 1;

    function barLeft(i) { return parseFloat(bars[i].getAttribute(aligned ? "data-aligned-left" : "data-left")); }
    function cleanupRatio(i) { return parseFloat(inners[i].getAttribute("data-cleanup-ratio")) || 1; }
    function barWidth(i) {
        var width = parseFloat(bars[i].getAttribute(aligned ? "data-aligned-width" : "data-width"));
        return showCleanup ? width : width / cleanupRatio(i);
    }

    function positionBars() {
        spanS = aligned ? alignedSpanS : clockSpanS;
        bars.forEach(function (bar, i) {
            bar.style.left = barLeft(i) + "%";
            bar.style.width = barWidth(i) + "%";
            inners[i].style.width = (showCleanup ? 100 : cleanupRatio(i) * 100) + "%";
        });
        cleanupChip.classList.toggle("active", showCleanup);
        if (alignButton) alignButton.classList.toggle("active", aligned);
    }
    positionBars();

    function setAligned(value) {
        if (aligned === value) return;
        aligned = value;
        positionBars();
        applyZoom(zoom, 0);
        writeHash();
    }

    function labelWidth() { return spacer.offsetWidth + workerHeader.offsetWidth; }

    function setLabelWidth(px) {
        var max = Math.max(LABEL_W_MIN, scroller.clientWidth - workerHeader.offsetWidth - 200);
        px = Math.round(Math.min(max, Math.max(LABEL_W_MIN, px)));
        gantt.style.setProperty("--label-w", px + "px");
        return px;
    }
    function viewTrackWidth() { return Math.max(1, scroller.clientWidth - labelWidth()); }
    function trackWidth() { return viewTrackWidth() * zoom; }

    function pad(n) { return (n < 10 ? "0" : "") + n; }

    function formatTick(offsetS, step) {
        var total = aligned ? offsetS : (clockStartS + offsetS) % 86400;
        var whole = Math.floor(total + 1e-9);
        var hours = Math.floor(whole / 3600);
        var text = aligned
            ? "+" + (hours ? hours + ":" + pad(Math.floor(whole / 60) % 60) : Math.floor(whole / 60)) + ":" + pad(whole % 60)
            : pad(hours) + ":" + pad(Math.floor(whole / 60) % 60) + ":" + pad(whole % 60);
        if (step < 1) {
            var digits = step >= 0.1 ? 1 : step >= 0.01 ? 2 : 3;
            text += "." + (total - whole).toFixed(digits).slice(2);
        }
        return text;
    }

    function renderTicks() {
        var width = trackWidth();
        var pxPerS = width / spanS;
        var step = TICK_STEPS[TICK_STEPS.length - 1];
        for (var i = 0; i < TICK_STEPS.length; i++) {
            if (TICK_STEPS[i] * pxPerS >= TICK_MIN_PX) { step = TICK_STEPS[i]; break; }
        }
        var html = "";
        for (var n = 0; n * step <= spanS + 1e-9; n++) {
            var t = n * step;
            var left = t * pxPerS;
            if (left < 30 || left > width - 30) continue;
            html += '<span class="gantt-tick" style="left:' + left + 'px">' + formatTick(t, step) + "</span>";
        }
        axisTrack.innerHTML = html;
        gantt.style.setProperty("--grid-px", step * pxPerS + "px");
    }

    function markNarrowBars() {
        bars.forEach(function (bar, i) {
            if (rows[i].classList.contains("hidden")) return;
            var label = bar.firstElementChild;
            bar.classList.toggle("narrow", bar.clientWidth < label.scrollWidth + 8);
            bar.classList.toggle("tiny", bar.offsetWidth < 12);
        });
    }

    function applyZoom(newZoom, anchorPx) {
        stopGlide();
        newZoom = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, newZoom));
        if (anchorPx === undefined) anchorPx = viewTrackWidth() / 2;
        var anchorFrac = (scroller.scrollLeft + anchorPx) / trackWidth();
        zoom = newZoom;
        gantt.style.width = labelWidth() + trackWidth() + "px";
        scroller.scrollLeft = anchorFrac * trackWidth() - anchorPx;
        zoomLevel.textContent = (Math.round(zoom * 10) / 10) + "×";
        renderTicks();
        markNarrowBars();
        if (bottomSpacer) sizeBottomSpacer();
        syncPanOffset();
        writeHash();
    }

    function scrollToSeconds(seconds) {
        scroller.scrollLeft = seconds / spanS * trackWidth();
    }

    function leftEdgeSeconds() {
        return scroller.scrollLeft / trackWidth() * spanS;
    }

    function activeValues(chips, attr) {
        return chips.filter(function (c) { return c.classList.contains("active") && !c.disabled; })
            .map(function (c) { return c.getAttribute(attr); });
    }

    function allActive(chips) {
        return chips.every(function (c) { return c.disabled || c.classList.contains("active"); });
    }

    function applyFilters() {
        var statuses = activeValues(statusChips, "data-status");
        var chipStatuses = statusChips.map(function (c) { return c.getAttribute("data-status"); });
        var workers = activeValues(workerChips, "data-worker");
        var query = search.value.trim().toLowerCase();
        var count = 0;
        rows.forEach(function (row) {
            var status = row.getAttribute("data-status");
            var visible = (statuses.indexOf(status) !== -1 || chipStatuses.indexOf(status) === -1) &&
                workers.indexOf(row.getAttribute("data-worker")) !== -1 &&
                (!query || row.getAttribute("data-search").indexOf(query) !== -1);
            row.classList.toggle("hidden", !visible);
            if (visible) count++;
        });
        shown.textContent = "Showing " + count + " of " + rows.length;
        if (bottomSpacer) sizeBottomSpacer();
        var firstShown = rows.filter(function (row) { return !row.classList.contains("hidden"); })[0];
        rows.forEach(function (row) { row.classList.toggle("first-shown", row === firstShown); });
        markNarrowBars();
        writeHash();
    }

    function fitToShown() {
        var lo = 100, hi = 0;
        rows.forEach(function (row, i) {
            if (row.classList.contains("hidden")) return;
            lo = Math.min(lo, barLeft(i));
            hi = Math.max(hi, barLeft(i) + barWidth(i));
        });
        if (hi <= lo) return;
        applyZoom(100 / (hi - lo) * 0.96, 0);
        scroller.scrollLeft = Math.max(0, (lo - (hi - lo) * 0.02) / 100 * trackWidth());
        writeHash();
    }

    var restoring = true;
    function writeHash() {
        if (restoring) return;
        var parts = [];
        if (zoom !== 1) {
            parts.push("zoom=" + Math.round(zoom * 100) / 100);
            parts.push("t=" + parseFloat(leftEdgeSeconds().toPrecision(6)));
        }
        if (scroller.scrollTop > 0) parts.push("y=" + Math.round(scroller.scrollTop));
        if (!allActive(statusChips)) parts.push("status=" + activeValues(statusChips, "data-status").join(","));
        if (aligned) parts.push("align=1");
        if (!showCleanup) parts.push("cleanup=0");
        if (!allActive(workerChips)) parts.push("worker=" + activeValues(workerChips, "data-worker").join(","));
        if (focusedRow) parts.push("scenario=" + encodeURIComponent(focusedRow.getAttribute("data-id")));
        if (search.value.trim()) parts.push("q=" + encodeURIComponent(search.value.trim()));
        var hash = parts.length ? "#" + parts.join("&") : "";
        history.replaceState(null, "", location.pathname + location.search + hash);
    }

    function readHash() {
        var params = {};
        location.hash.replace(/^#/, "").split("&").forEach(function (pair) {
            var idx = pair.indexOf("=");
            if (idx > 0) params[pair.slice(0, idx)] = decodeURIComponent(pair.slice(idx + 1));
        });
        var statuses = params.status === undefined ? null : params.status.split(",");
        statusChips.forEach(function (c) { c.classList.toggle("active", !statuses || statuses.indexOf(c.getAttribute("data-status")) !== -1); });
        var workers = params.worker === undefined ? null : params.worker.split(",");
        workerChips.forEach(function (c) { c.classList.toggle("active", !workers || workers.indexOf(c.getAttribute("data-worker")) !== -1); });
        search.value = params.q || "";
        aligned = !!alignButton && params.align === "1";
        showCleanup = params.cleanup !== "0";
        positionBars();
        applyFilters();
        var z = parseFloat(params.zoom);
        applyZoom(isFinite(z) ? z : 1, 0);
        var y = parseFloat(params.y);
        if (isFinite(y) && y > 0) scroller.scrollTop = y;
        lastScrollTop = scroller.scrollTop;
        var t = parseFloat(params.t);
        if (isFinite(t) && t >= 0 && t <= spanS) scrollToSeconds(t);
        setFocus(params.scenario ? gantt.querySelector('.gantt-row[data-id="' + CSS.escape(params.scenario) + '"]') : null);
        if (focusedRow && !isFinite(z) && !isFinite(y)) showFocused();
    }

    var FOCUS_BAR_VIEW_PCT = 25;
    var focusedRow = null;

    function setFocus(row) {
        if (focusedRow) focusedRow.classList.remove("focused");
        focusedRow = row;
        if (focusedRow) focusedRow.classList.add("focused");
    }

    function showFocused() {
        var i = rows.indexOf(focusedRow);
        if (focusedRow.classList.contains("hidden")) return;
        applyZoom(FOCUS_BAR_VIEW_PCT / Math.max(barWidth(i), 1e-6), 0);
        scroller.scrollTop = focusedRow.classList.contains("first-shown") ? 0 : focusedRow.offsetTop - axis.offsetHeight;
        lastScrollTop = scroller.scrollTop;
        stopGlide();
        scroller.scrollLeft = barLeft(i) / 100 * trackWidth() - FOLLOW_MARGIN_PX;
    }

    function wireChips(chips) {
        chips.forEach(function (chip) {
            chip.addEventListener("click", function (event) {
                if (event.altKey) {
                    chips.forEach(function (c) { c.classList.toggle("active", c === chip); });
                } else {
                    chip.classList.toggle("active");
                }
                applyFilters();
            });
        });
    }
    wireChips(statusChips);
    wireChips(workerChips);
    cleanupChip.addEventListener("click", function () {
        showCleanup = !showCleanup;
        positionBars();
        markNarrowBars();
        writeHash();
    });
    if (alignButton) alignButton.addEventListener("click", function () { setAligned(!aligned); });
    search.addEventListener("input", applyFilters);
    document.querySelector(".gantt-reset-filters").addEventListener("click", function () {
        statusChips.concat(workerChips).forEach(function (c) { c.classList.add("active"); });
        search.value = "";
        showCleanup = true;
        positionBars();
        setFocus(null);
        applyFilters();
        applyZoom(1, 0);
        scroller.scrollTop = 0;
        lastScrollTop = 0;
        scroller.scrollLeft = 0;
        history.replaceState(null, "", location.pathname + location.search);
    });

    document.querySelectorAll(".gantt-btn[data-zoom]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var action = btn.getAttribute("data-zoom");
                if (action === "in") applyZoom(zoom * 2);
            else if (action === "out") applyZoom(zoom / 2);
            else if (action === "fit") fitToShown();
        });
    });

    scroller.addEventListener("wheel", function (event) {
        if (!event.ctrlKey && !event.metaKey) return;
        event.preventDefault();
        var anchor = event.clientX - scroller.getBoundingClientRect().left - labelWidth();
        applyZoom(zoom * Math.exp(-event.deltaY * 0.002), Math.max(0, anchor));
    }, { passive: false });

    var FOLLOW_MARGIN_PX = 24;
    var lastScrollTop = scroller.scrollTop;
    var axis = gantt.querySelector(".gantt-axis");
    var panOffset = 0;
    var lastSetLeft = null;

    function stopGlide() {}

    function followLeft(top) {
        var axisHeight = axis.offsetHeight;
        var prev = null;
        for (var i = 0; i < rows.length; i++) {
            if (rows[i].classList.contains("hidden")) continue;
            var point = { y: rows[i].offsetTop - axisHeight, x: barLeft(i) / 100 * trackWidth() - FOLLOW_MARGIN_PX };
            if (top <= point.y) {
                if (!prev) return point.x;
                var t = (top - prev.y) / Math.max(1, point.y - prev.y);
                return prev.x + (point.x - prev.x) * t;
            }
            prev = point;
        }
        return prev ? prev.x : 0;
    }

    function clampLeft(left) {
        return Math.max(0, Math.min(left, scroller.scrollWidth - scroller.clientWidth));
    }

    function syncPanOffset() {
        panOffset = scroller.scrollLeft - clampLeft(followLeft(scroller.scrollTop));
        lastSetLeft = null;
    }

    function followTopRow() {
        var left = clampLeft(clampLeft(followLeft(scroller.scrollTop)) + panOffset);
        lastSetLeft = Math.round(left);
        scroller.scrollLeft = left;
    }

    var scrollTimer = null;
    scroller.addEventListener("scroll", function () {
        if (scroller.scrollTop !== lastScrollTop) {
            lastScrollTop = scroller.scrollTop;
            if (!pan) followTopRow();
        } else if (!pan && (lastSetLeft === null || Math.abs(scroller.scrollLeft - lastSetLeft) > 1)) {
            syncPanOffset();
        }
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(writeHash, 150);
    });

    var pan = null;
    gantt.addEventListener("mousedown", function (event) {
        if (event.button !== 0 || !event.target.classList.contains("gantt-track")) return;
        pan = { x: event.clientX, y: event.clientY, left: scroller.scrollLeft, top: scroller.scrollTop };
        scroller.classList.add("panning");
        event.preventDefault();
    });
    window.addEventListener("mousemove", function (event) {
        if (!pan) return;
        scroller.scrollLeft = pan.left - (event.clientX - pan.x);
        scroller.scrollTop = pan.top - (event.clientY - pan.y);
    });
    window.addEventListener("mouseup", function () {
        if (pan) syncPanOffset();
        pan = null;
        scroller.classList.remove("panning");
    });

    var stored = parseFloat(localStorage.getItem(LABEL_W_KEY));
    if (isFinite(stored)) setLabelWidth(stored);

    var resize = null;
    resizer.addEventListener("mousedown", function (event) {
        if (event.button !== 0) return;
        resize = { x: event.clientX, width: spacer.offsetWidth };
        gantt.classList.add("resizing");
        event.preventDefault();
        event.stopPropagation();
    });
    window.addEventListener("mousemove", function (event) {
        if (!resize) return;
        setLabelWidth(resize.width + event.clientX - resize.x);
        applyZoom(zoom, 0);
    });
    window.addEventListener("mouseup", function () {
        if (!resize) return;
        resize = null;
        gantt.classList.remove("resizing");
        localStorage.setItem(LABEL_W_KEY, spacer.offsetWidth);
    });
    resizer.addEventListener("dblclick", function () {
        setLabelWidth(LABEL_W_DEFAULT);
        localStorage.removeItem(LABEL_W_KEY);
        applyZoom(zoom, 0);
    });

    window.addEventListener("resize", function () { applyZoom(zoom, 0); });

    var rowsBox = gantt.querySelector(".gantt-rows");
    var BOUNCE_MAX_PX = 48;
    var bounce = 0;
    var bounceTimer = null;

    function setBounce(px) {
        bounce = px;
        rowsBox.style.transform = px ? "translateY(" + px + "px)" : "";
    }

    scroller.addEventListener("wheel", function (event) {
        if (event.ctrlKey || event.metaKey || event.shiftKey || !event.deltaY) return;
        var atTop = scroller.scrollTop <= 0 && event.deltaY < 0;
        var atBottom = scroller.scrollTop + scroller.clientHeight >= scroller.scrollHeight - 1 && event.deltaY > 0;
        if (!atTop && !atBottom && !bounce) return;
        rowsBox.classList.remove("bouncing");
        var next = bounce - event.deltaY * 0.35 * (1 - Math.abs(bounce) / BOUNCE_MAX_PX);
        if (atTop) next = Math.max(0, Math.min(BOUNCE_MAX_PX, next));
        else if (atBottom) next = Math.min(0, Math.max(-BOUNCE_MAX_PX, next));
        else next = 0;
        setBounce(next);
        clearTimeout(bounceTimer);
        bounceTimer = setTimeout(function () {
            rowsBox.classList.add("bouncing");
            setBounce(0);
        }, 90);
    }, { passive: true });

    var bottomSpacer = gantt.querySelector(".gantt-spacer-bottom");

    function sizeBottomSpacer() {
        var shownRows = rows.filter(function (row) { return !row.classList.contains("hidden"); });
        var last = shownRows[shownRows.length - 1] || rows[rows.length - 1];
        var rowH = last.offsetHeight || 17;
        var current = bottomSpacer.offsetHeight;
        var excess = (scroller.scrollHeight - scroller.clientHeight) - (last.offsetTop - axis.offsetHeight);
        bottomSpacer.style.height = Math.max(rowH, current - excess) + "px";
    }
    sizeBottomSpacer();
    window.addEventListener("resize", sizeBottomSpacer);

    var tip = document.createElement("div");
    tip.className = "gantt-tip";
    document.body.appendChild(tip);
    gantt.querySelectorAll(".gantt-track [title], .gantt-worker[title]").forEach(function (el) {
        el.setAttribute("data-tip", el.getAttribute("title"));
        el.removeAttribute("title");
    });
    gantt.addEventListener("mousemove", function (event) {
        var el = event.target.closest("[data-tip]");
        if (!el || pan) { tip.style.display = "none"; return; }
        tip.textContent = el.getAttribute("data-tip");
        tip.style.display = "block";
        var x = event.clientX + 12, y = event.clientY + 14;
        if (x + tip.offsetWidth > window.innerWidth - 4) x = event.clientX - tip.offsetWidth - 12;
        if (y + tip.offsetHeight > window.innerHeight - 4) y = event.clientY - tip.offsetHeight - 10;
        tip.style.left = x + "px";
        tip.style.top = y + "px";
    });
    gantt.addEventListener("mouseleave", function () { tip.style.display = "none"; });

    readHash();
    restoring = false;

    window.addEventListener("hashchange", function () {
        clearTimeout(scrollTimer);
        restoring = true;
        readHash();
        restoring = false;
    });
    writeHash();
});
