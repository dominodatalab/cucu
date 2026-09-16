/*
 * utility javascript library that allows us to delay page loads for testing
 */
(function() {
var delay = new URLSearchParams(window.location.search).get('delay_page_load_ms');
if (delay) {
    var html = document.body.innerHTML;
    document.body.innerHTML = '';
    setTimeout(function() {
        document.body.innerHTML = html;
    }, parseInt(delay))
}

var clear_after = new URLSearchParams(window.location.search).get('clear_page_after_ms');
if (clear_after) {
    setTimeout(function() {
        document.body.innerHTML = '';
    }, parseInt(clear_after))
}

/*
 * toggle visibility of #toggled without adding or removing it from the DOM, so
 * tests can cover the case where fuzzy find must re-evaluate visibility for an
 * element it has already seen
 */
var reveal_after = new URLSearchParams(window.location.search).get('reveal_hidden_after_ms');
if (reveal_after) {
    setTimeout(function() {
        document.querySelector('#toggled').style.display = 'inline';
    }, parseInt(reveal_after))
}

var hide_after = new URLSearchParams(window.location.search).get('hide_shown_after_ms');
if (hide_after) {
    document.querySelector('#toggled').style.display = 'inline';
    setTimeout(function() {
        document.querySelector('#toggled').style.display = 'none';
    }, parseInt(hide_after))
}
})();
