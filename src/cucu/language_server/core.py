import logging
import re
from importlib import metadata

import jellyfish
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionList,
    CompletionOptions,
    CompletionParams,
)
from pygls.server import LanguageServer

from cucu import init_global_hook_variables
from cucu.cli.steps import load_cucu_steps

init_global_hook_variables()


def find_completions(step_fragment, steps_cache=None):
    """
    given a step name fragment return all of the possible step name completions
    for that fragment.

    Params:
        step_fragment(string): prefix of the step name to look for such as
                             "I click"

    Returns:
        an Array tuples of step name and locations.
    """
    items = []

    if steps_cache is None:
        steps_cache, _ = load_cucu_steps()

    # first pass try to find steps that start with fragment provided
    for step in steps_cache.keys():
        if step.startswith(step_fragment):
            step_details = steps_cache[step]
            location = step_details["location"]
            location = f"{location['filepath']}:{location['line']}"
            items.append((step, location))

    # if there were 0 steps found then lets at least find some that are close
    # based on some string distance heuristic
    if len(items) == 0:
        for step in steps_cache.keys():
            if jellyfish.jaro_similarity(step_fragment, step) > 0.6:
                step_details = steps_cache[step]
                location = step_details["location"]
                location = f"{location['filepath']}:{location['line']}"
                items.append((step, location))

        def compare_completion_item(completion_item):
            return jellyfish.jaro_similarity(completion_item[0], step_fragment)

        items.sort(key=compare_completion_item, reverse=True)

    return items


def start(port=None):
    version = metadata.version(__package__.split(".")[0])
    server = LanguageServer(name="cucu", version=version)
    steps_cache, _ = load_cucu_steps()
    logging.basicConfig(
        filename="pygls.log", filemode="w", level=logging.DEBUG
    )

    @server.feature(
        TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=[","])
    )
    def completions(ls: LanguageServer, params: CompletionParams):
        logging.warn(f"{TEXT_DOCUMENT_COMPLETION}: {params}")

        document_uri = params.text_document.uri
        document = document_lines = ls.workspace.get_document(document_uri)
        document_lines = document.source.split("\n")

        completion_line = document_lines[params.position.line]
        logging.debug(f'completions for "{completion_line}"')

        completion_line = completion_line.lstrip()
        step_line = re.match(
            "(Given|When|Then|And) (.*)", completion_line
        ).groups()[1]

        items = []
        step_completions = find_completions(
            completion_line, steps_cache=steps_cache
        )

        for step_name, step_location in step_completions:
            insert_text = step_name.replace(step_line, "")
            items.append(
                CompletionItem(
                    label=step_name,
                    detail=f"defined in {step_location}",
                    insert_text=insert_text,
                )
            )

        return CompletionList(
            is_incomplete=False,
            items=items,
        )

    if port:
        server.start_tcp("0.0.0.0", int(port))

    else:
        server.start_io()
