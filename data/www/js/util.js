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
})();
