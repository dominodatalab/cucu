document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".gantt-tick[data-left]").forEach(function (el) {
        el.style.left = el.getAttribute("data-left") + "%";
    });
    document.querySelectorAll(".gantt-bar[data-left]").forEach(function (el) {
        el.style.left = el.getAttribute("data-left") + "%";
        el.style.width = el.getAttribute("data-width") + "%";
    });
});
