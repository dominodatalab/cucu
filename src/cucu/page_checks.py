from tenacity import retry, stop_after_delay, wait_fixed

from cucu import config, logger, register_page_check_hook


def init_page_checks():
    """
    initialize cucu built in page checks
    """

    @retry(
        stop=stop_after_delay(
            float(config.CONFIG["CUCU_STEP_WAIT_TIMEOUT_S"])
        ),
        wait=wait_fixed(float(config.CONFIG["CUCU_STEP_RETRY_AFTER_S"])),
    )
    def wait_for_document_to_be_ready(browser):
        if config.CONFIG["CUCU_SKIP_PAGE_READY_CHECK"] != "false":
            state = browser.execute("return document.readyState;")

            if state != "complete":
                raise RuntimeError(f'document.readyState is in "{state}"')
        else:
            logger.debug("skipped document.readyState check")

    register_page_check_hook(
        "wait for document.readyState", wait_for_document_to_be_ready
    )

    @retry(
        stop=stop_after_delay(
            float(config.CONFIG["CUCU_STEP_WAIT_TIMEOUT_S"])
        ),
        wait=wait_fixed(float(config.CONFIG["CUCU_STEP_RETRY_AFTER_S"])),
    )
    def wait_for_all_images_to_be_loaded(browser):
        if config.CONFIG["CUCU_SKIP_BROKEN_IMAGES_CHECK"] == "false":
            broken_images = browser.execute(
                """
            return (function() {
                var images = Array.prototype.slice.call(document.querySelectorAll('img:not([aria-hidden=true])'));

                return images.filter(function(image){
                    return !image.complete
                           || image.naturalHeight === 0;
                });
            })();
            """
            )

            if len(broken_images) != 0:
                # lets print the image outerHTML so its easier to identify
                for broken_image in broken_images:
                    html = broken_image.get_attribute("outerHTML")
                    logger.warning(f"broken image found: {html}")

                raise RuntimeError("broken images were found on the page")
        else:
            logger.debug("skipped broken image check")

    register_page_check_hook(
        "broken image checker", wait_for_all_images_to_be_loaded
    )
