import os

import cv2
from skimage.metrics import structural_similarity

from cucu import StopRetryException, helpers, logger, retry, step
from cucu.config import CONFIG


def find_image(ctx, name, index=0):
    """
    find an input on screen by fuzzy matching on the name provided and the
    target element:

        * <img>

    parameters:
      ctx(object): behave context object used to share data between steps
      name(str):   name that identifies the desired image on screen
      index(str):  the index of the image if there are duplicates

    returns:
        the WebElement that matches the provided arguments.
    """
    ctx.check_browser_initialized()

    name = name.replace('"', '\\"')
    images = ctx.browser.css_find_elements(f'img[alt="{name}"')

    if index >= len(images):
        return None

    return images[index]


helpers.define_should_see_thing_with_name_steps(
    "image with the alt text", find_image
)


def get_image_screenshot(ctx, display_image_name):
    image_element = find_image(ctx, display_image_name, index=0)
    image_screenshot_location = (
        CONFIG["CUCU_RESULTS_DIR"] + "/Images/cucu_image_screenshot.png"
    )
    image_element.screenshot(f"{image_screenshot_location}")
    return image_screenshot_location


def compare_two_images(
    ctx, image1_filepath, image2_filepath, min_similarity_percent
):
    # load the input images
    # The cv2.imread() function return a NumPy array if the image is loaded successfully.
    image1 = cv2.imread(os.path.abspath(image1_filepath))
    image2 = cv2.imread(os.path.abspath(image2_filepath))

    # convert the images to grayscale
    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # make the shapes of two images same to compare.
    # cv2.resize() - tuple passed for determining the size of the new image follows the order (width, height) unlike as expected (height, width).
    if image1.shape != image2.shape:
        h, w = image1.shape
        image2 = cv2.resize(image2, (w, h))

    # Calculate structural similarity of images.
    similarity_score, diff = structural_similarity(image1, image2, full=True)
    logger.debug("Similarity Score: {:.2f}%".format(similarity_score * 100))

    if similarity_score * 100 < float(min_similarity_percent):
        raise StopRetryException(
            f"Images are not {min_similarity_percent} percent similar"
        )


@step(
    'I wait to see the source image "{image_filepath}" and the displayed image "{display_name}" are at least "{percentage}" percent similar'
)
def wait_to_compare_source_displayed_images(
    ctx, image_filepath, display_name, percentage
):
    display_image_filepath = retry(get_image_screenshot)(ctx, display_name)
    compare_two_images(ctx, image_filepath, display_image_filepath, percentage)


@step(
    'I wait to see the image "{image1_filepath}" and the image "{image2_filepath}" are at least "{percentage}" percent similar'
)
def wait_to_compare_two_images(
    ctx, image1_filepath, image2_filepath, percentage
):
    retry(compare_two_images)(ctx, image1_filepath, image2_filepath, percentage)
