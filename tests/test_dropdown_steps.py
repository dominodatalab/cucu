from unittest.mock import MagicMock, patch

from cucu.steps import dropdown_steps


def _dropdown_element(expanded="true"):
    element = MagicMock()
    element.get_attribute.return_value = expanded
    return element


def test_dynamic_dropdown_selects_visible_option_without_typing():
    ctx = MagicMock()
    option_element = MagicMock()
    mock_find_option = MagicMock()
    mock_find_option.__wrapped__ = MagicMock(return_value=option_element)

    with (
        patch.object(
            dropdown_steps, "find_dropdown", return_value=_dropdown_element()
        ),
        patch.object(
            dropdown_steps.base_steps, "is_disabled", return_value=False
        ),
        patch.object(dropdown_steps, "find_dropdown_option", mock_find_option),
        patch.object(dropdown_steps, "find_input") as find_input,
        patch.object(
            dropdown_steps, "click_dynamic_dropdown_option"
        ) as click_option,
    ):
        dropdown_steps.find_n_select_dynamic_dropdown_option(
            ctx, "Listed Dropdown", "already-listed"
        )

    mock_find_option.__wrapped__.assert_called_once_with(ctx, "already-listed")
    mock_find_option.assert_not_called()
    find_input.assert_not_called()
    click_option.assert_called_once_with(ctx, option_element)
    ctx.browser.wait_for_page_to_load.assert_called_once()


def test_dynamic_dropdown_types_full_option_once_when_not_listed():
    ctx = MagicMock()
    option_element = MagicMock()
    dropdown_input = MagicMock()
    dropdown_input.get_attribute.return_value = ""
    mock_find_option = MagicMock(return_value=option_element)
    mock_find_option.__wrapped__ = MagicMock(return_value=None)

    with (
        patch.object(
            dropdown_steps, "find_dropdown", return_value=_dropdown_element()
        ),
        patch.object(
            dropdown_steps.base_steps, "is_disabled", return_value=False
        ),
        patch.object(dropdown_steps, "find_dropdown_option", mock_find_option),
        patch.object(
            dropdown_steps, "find_input", return_value=dropdown_input
        ) as find_input,
        patch.object(
            dropdown_steps, "click_dynamic_dropdown_option"
        ) as click_option,
    ):
        dropdown_steps.find_n_select_dynamic_dropdown_option(
            ctx, "Code", "gbp-sync-15df69dc4dbb"
        )

    mock_find_option.__wrapped__.assert_called_once_with(
        ctx, "gbp-sync-15df69dc4dbb"
    )
    find_input.assert_called_once_with(ctx, "Code", 0)
    dropdown_input.send_keys.assert_called_once_with("gbp-sync-15df69dc4dbb")
    mock_find_option.assert_called_once_with(ctx, "gbp-sync-15df69dc4dbb")
    click_option.assert_called_once_with(ctx, option_element)
    assert ctx.browser.wait_for_page_to_load.call_count == 2


def test_dynamic_dropdown_refinds_input_after_clearing_existing_value():
    ctx = MagicMock()
    option_element = MagicMock()
    existing_input = MagicMock()
    existing_input.get_attribute.return_value = "old"
    typed_input = MagicMock()
    mock_find_option = MagicMock(return_value=option_element)
    mock_find_option.__wrapped__ = MagicMock(return_value=None)

    with (
        patch.object(
            dropdown_steps, "find_dropdown", return_value=_dropdown_element()
        ),
        patch.object(
            dropdown_steps.base_steps, "is_disabled", return_value=False
        ),
        patch.object(dropdown_steps, "find_dropdown_option", mock_find_option),
        patch.object(
            dropdown_steps,
            "find_input",
            side_effect=[existing_input, typed_input],
        ),
        patch.object(dropdown_steps, "click_dynamic_dropdown_option"),
    ):
        dropdown_steps.find_n_select_dynamic_dropdown_option(
            ctx, "Code", "gbp-sync-15df69dc4dbb"
        )

    typed_input.send_keys.assert_called_once_with("gbp-sync-15df69dc4dbb")
    existing_input.send_keys.assert_called()


def test_dynamic_dropdown_waits_after_opening_before_probe():
    ctx = MagicMock()
    option_element = MagicMock()
    mock_find_option = MagicMock()
    mock_find_option.__wrapped__ = MagicMock(return_value=option_element)

    with (
        patch.object(
            dropdown_steps,
            "find_dropdown",
            return_value=_dropdown_element(expanded="false"),
        ),
        patch.object(
            dropdown_steps.base_steps, "is_disabled", return_value=False
        ),
        patch.object(dropdown_steps, "find_dropdown_option", mock_find_option),
        patch.object(dropdown_steps, "click_dropdown") as click_dropdown,
        patch.object(dropdown_steps, "find_input") as find_input,
        patch.object(dropdown_steps, "click_dynamic_dropdown_option"),
    ):
        dropdown_steps.find_n_select_dynamic_dropdown_option(
            ctx, "Code", "already-listed"
        )

    click_dropdown.assert_called_once()
    find_input.assert_not_called()
    assert ctx.browser.wait_for_page_to_load.call_count == 2
    mock_find_option.__wrapped__.assert_called_once_with(ctx, "already-listed")
