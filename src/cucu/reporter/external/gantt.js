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
    var search = document.querySelector(".gantt-search");
    var shown = document.querySelector(".gantt-shown");
    var zoomLevel = document.querySelector(".gantt-zoom-level");

    var spanS = parseFloat(gantt.getAttribute("data-span-s"));
    var clockStartS = parseFloat(gantt.getAttribute("data-run-start-clock-s"));
    var zoom = 1;

    bars.forEach(function (bar) {
        bar.style.left = bar.getAttribute("data-left") + "%";
        bar.style.width = bar.getAttribute("data-width") + "%";
    });

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

    function formatClock(offsetS, step) {
        var total = (clockStartS + offsetS) % 86400;
        var whole = Math.floor(total);
        var text = pad(Math.floor(whole / 3600)) + ":" + pad(Math.floor(whole / 60) % 60) + ":" + pad(whole % 60);
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
            html += '<span class="gantt-tick" style="left:' + left + 'px">' + formatClock(t, step) + "</span>";
        }
        axisTrack.innerHTML = html;
        gantt.style.setProperty("--grid-px", step * pxPerS + "px");
    }

    function markNarrowBars() {
        bars.forEach(function (bar, i) {
            if (rows[i].classList.contains("hidden")) return;
            var label = bar.firstElementChild;
            bar.classList.toggle("narrow", bar.clientWidth < label.scrollWidth + 8);
        });
    }

    function applyZoom(newZoom, anchorPx) {
        newZoom = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, newZoom));
        if (anchorPx === undefined) anchorPx = viewTrackWidth() / 2;
        var anchorFrac = (scroller.scrollLeft + anchorPx) / trackWidth();
        zoom = newZoom;
        gantt.style.width = labelWidth() + trackWidth() + "px";
        scroller.scrollLeft = anchorFrac * trackWidth() - anchorPx;
        zoomLevel.textContent = (Math.round(zoom * 10) / 10) + "×";
        renderTicks();
        markNarrowBars();
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
        var workers = activeValues(workerChips, "data-worker");
        var query = search.value.trim().toLowerCase();
        var count = 0;
        rows.forEach(function (row) {
            var visible = statuses.indexOf(row.getAttribute("data-status")) !== -1 &&
                (!workerChips.length || workers.indexOf(row.getAttribute("data-worker")) !== -1) &&
                (!query || row.getAttribute("data-search").indexOf(query) !== -1);
            row.classList.toggle("hidden", !visible);
            if (visible) count++;
        });
        shown.textContent = "Showing " + count + " of " + rows.length;
        markNarrowBars();
        writeHash();
    }

    function fitToShown() {
        var lo = 100, hi = 0;
        rows.forEach(function (row, i) {
            if (row.classList.contains("hidden")) return;
            var left = parseFloat(bars[i].getAttribute("data-left"));
            lo = Math.min(lo, left);
            hi = Math.max(hi, left + parseFloat(bars[i].getAttribute("data-width")));
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
            parts.push("t=" + Math.round(leftEdgeSeconds() * 10) / 10);
        }
        if (!allActive(statusChips)) parts.push("status=" + activeValues(statusChips, "data-status").join(","));
        if (!allActive(workerChips)) parts.push("worker=" + activeValues(workerChips, "data-worker").join(","));
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
        if (params.status !== undefined) {
            var statuses = params.status.split(",");
            statusChips.forEach(function (c) { c.classList.toggle("active", statuses.indexOf(c.getAttribute("data-status")) !== -1); });
        }
        if (params.worker !== undefined) {
            var workers = params.worker.split(",");
            workerChips.forEach(function (c) { c.classList.toggle("active", workers.indexOf(c.getAttribute("data-worker")) !== -1); });
        }
        if (params.q) search.value = params.q;
        applyFilters();
        var z = parseFloat(params.zoom);
        applyZoom(isFinite(z) ? z : 1, 0);
        var t = parseFloat(params.t);
        if (isFinite(t) && t >= 0 && t <= spanS) scrollToSeconds(t);
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
    search.addEventListener("input", applyFilters);

    document.querySelectorAll(".gantt-btn[data-zoom]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var action = btn.getAttribute("data-zoom");
            if (action === "in") applyZoom(zoom * 2);
            else if (action === "out") applyZoom(zoom / 2);
            else if (action === "fit") fitToShown();
            else { applyZoom(1, 0); scroller.scrollLeft = 0; writeHash(); }
        });
    });

    scroller.addEventListener("wheel", function (event) {
        if (!event.ctrlKey && !event.metaKey) return;
        event.preventDefault();
        var anchor = event.clientX - scroller.getBoundingClientRect().left - labelWidth();
        applyZoom(zoom * Math.exp(-event.deltaY * 0.002), Math.max(0, anchor));
    }, { passive: false });

    var scrollTimer = null;
    scroller.addEventListener("scroll", function () {
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

    readHash();
    restoring = false;
    writeHash();
});
