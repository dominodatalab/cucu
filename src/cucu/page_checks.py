from cucu import config, retry, register_page_check_hook, logger


def init_page_checks():
    """
    initialize cucu built in page checks
    """

    if config.CONFIG["CUCU_READY_STATE_PAGE_CHECK"] == "enabled":

        def wait_for_document_to_be_ready(browser):
            state = browser.execute("return document.readyState;")

            if state != "complete":
                raise RuntimeError(f'document.readyState is in "{state}"')

        register_page_check_hook(
            "wait for document.readyState", retry(wait_for_document_to_be_ready)
        )

    if config.CONFIG["CUCU_BROKEN_IMAGES_PAGE_CHECK"] == "enabled":

        def wait_for_all_images_to_be_loaded(browser):
            broken_images = browser.execute(
                """
            return (function() {
                var images = Array.prototype.slice.call(document.querySelectorAll('img'));

                return images.filter(function(image){
                    return !image.complete &&
                           image.naturalHeight !== 0 &&
                           image.getAttribute('aria-hidden') !== 'true';
                });
            })();
            """
            )

            if len(broken_images) != 0:
                # lets print the image outerHTML so its easier to identify
                for broken_image in broken_images:
                    html = broken_image.get_attribute("outerHTML")
                    logger.warn(f"broken image found: {html}")

                raise RuntimeError("broken images were found on the page")

        register_page_check_hook(
            "broken image checker", retry(wait_for_all_images_to_be_loaded)
        )
