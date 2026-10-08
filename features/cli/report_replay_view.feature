@report
Feature: Report replay view
  As a developer I want the user to be able to view individual scenario reports
  in a replay timeline format for a more visual step-by-step experience

  Scenario: Replay view shows step text and navigation for a non-browser scenario
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/replay-echo-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-echo-results --output {CUCU_RESULTS_DIR}/replay-echo-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-echo-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Echo"
      And I click the link "Echo an environment variable"
      And I click the link "🔁 Replay"
     Then I wait to see the link "Echo"

        * # Scenario name shown in the header
      And I should see the text "Echo an environment variable"

        * # Stage shows step text for non-browser tests
      And I should see the text "1 / 6"
      And I should see the text "Given"

        * # dragging the timeline playhead must not leave it stranded far from the cursor: a
        * # bar's own duration is almost always a tiny fraction of the scenario's real elapsed
        * # time (clicking/asserting is near-instant), so most of the track used to be an
        * # unaccounted-for "dead zone" where any drag snapped the head to the far right edge
      And I execute in the current browser the following javascript
      """
      const track = document.getElementById("timeline-track");
      track.setPointerCapture = () => undefined;
      const r = track.getBoundingClientRect();
      const targetX = r.left + r.width * 0.5;
      window.__dragTargetPct = (targetX - r.left) / r.width * 100;
      const init = Object.fromEntries([["bubbles", true], ["cancelable", true], ["pointerId", 1], ["clientX", targetX], ["clientY", r.top + r.height / 2]]);
      track.dispatchEvent(new PointerEvent("pointerdown", init));
      """
      And I execute in the current browser the following javascript and save the result to the variable "DRAG_TRACKS_CURSOR_CHECK"
      """
      const track = document.getElementById("timeline-track");
      const head = document.getElementById("timeline-playhead");
      const r = track.getBoundingClientRect();
      const h = head.getBoundingClientRect();
      const headPct = (h.left - r.left) / r.width * 100;
      const diff = Math.abs(headPct - window.__dragTargetPct);
      return diff <= 5
        ? "tracks-cursor"
        : "diverges target=" + window.__dragTargetPct.toFixed(2) + " head=" + headPct.toFixed(2);
      """
      And I should see "{DRAG_TRACKS_CURSOR_CHECK}" is equal to "tracks-cursor"

  Scenario: Replay view auto-focuses the first failing step in a failed scenario
    Given I run the command "cucu run data/features/feature_with_failing_scenario.feature --results {CUCU_RESULTS_DIR}/replay-fail-results" and expect exit code "1"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-fail-results --output {CUCU_RESULTS_DIR}/replay-fail-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-fail-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Feature with failing scenario"
      And I click the link "Just a scenario that fails"
      And I click the link "🔁 Replay"
     Then I wait to see the text "1 / 1"
      And I should see the text "failed"

  Scenario: Replay view renders correctly for a scenario with substeps
    Given I run the command "cucu run data/features/scenario_with_substeps.feature --results {CUCU_RESULTS_DIR}/replay-substeps-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-substeps-results --output {CUCU_RESULTS_DIR}/replay-substeps-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-substeps-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Feature with substeps"
      And I click the link "Scenario that uses a step with substeps"
      And I click the link "🔁 Replay"
     Then I wait to see the text "1 /"
      And I should see the text "passed"

        * # parent steps with substeps must not double-count timing and overflow the timeline
      And I execute in the current browser the following javascript and save the result to the variable "TIMELINE_OVERFLOW_CHECK"
      """
      const data = JSON.parse(document.getElementById("replay-data").textContent);
      const maxEnd = Math.max(
        ...data.steps
          .filter((step) => step.startOffset !== null)
          .map((step) => step.startOffset + (step.duration || 0))
      );
      return maxEnd <= data.scenarioDuration ? "no-overflow" : "overflow";
      """
      And I should see "{TIMELINE_OVERFLOW_CHECK}" is equal to "no-overflow"

  Scenario: Replay view timeline bars do not overflow the track when substep durations double-count real time
    Given I run the command "cucu run data/features/scenario_with_substeps_that_sleep.feature --results {CUCU_RESULTS_DIR}/replay-substeps-sleep-results" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-substeps-sleep-results --output {CUCU_RESULTS_DIR}/replay-substeps-sleep-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-substeps-sleep-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Feature with substeps that sleep"
      And I click the link "Scenario that uses a step with substeps that sleep"
      And I click the link "🔁 Replay"
     Then I wait to see the text "1 /"
      And I should see the text "passed"

        * # a step wrapping substeps that each sleep for real seconds has its own duration
        * # legitimately span the same wall-clock window as its substeps, so summed bar
        * # durations exceed the scenario's real elapsed time (PLAY_END) -- the width math
        * # must not let that push step or cleanup bars past the right edge of the track
      And I execute in the current browser the following javascript and save the result to the variable "BAR_OVERFLOW_CHECK"
      """
      const track = document.getElementById("timeline-track").getBoundingClientRect();
      const bars = Array.from(document.querySelectorAll("#timeline-track .step-bar"));
      const maxRight = bars.reduce((acc, bar) => Math.max(acc, bar.getBoundingClientRect().right), 0);
      return maxRight <= track.right + 1
        ? "no-overflow"
        : "overflow maxRight=" + maxRight + " trackRight=" + track.right;
      """
      And I should see "{BAR_OVERFLOW_CHECK}" is equal to "no-overflow"

  Scenario: Replay view renders screenshots for a browser scenario
    Given I run the command "cucu run data/features/feature_with_passing_scenario_with_web.feature --results {CUCU_RESULTS_DIR}/replay-browser-results --env CUCU_BROKEN_IMAGES_PAGE_CHECK=disabled" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-browser-results --output {CUCU_RESULTS_DIR}/replay-browser-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-browser-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I wait to click the link "Feature with passing scenario with web"
      And I wait to click the link "Just a scenario that opens a web page"
      And I wait to click the link "🔁 Replay"
     Then I wait to see the text "1 /"
      And I should see the link "Index"
      And I should see the link "Feature with passing scenario with web"

        * # after-scenario cleanup hooks (keep-alive, MHT download, browser quit) get their own
        * # trailing entries on the timeline instead of being silently dropped
      And I should see the text "Cleanup"
      And I execute in the current browser the following javascript and save the result to the variable "CLEANUP_STEPS_CHECK"
      """
      const data = JSON.parse(document.getElementById("replay-data").textContent);
      const lastStepEnd = Math.max(
        ...data.steps
          .filter((step) => step.startOffset !== null)
          .map((step) => step.startOffset + (step.duration || 0))
      );
      const allAfterSteps = data.cleanupSteps.every(
        (cleanup) => cleanup.startOffset !== null && cleanup.startOffset >= lastStepEnd
      );
      return data.cleanupSteps.length > 0 && allAfterSteps ? "has-cleanup" : "no-cleanup";
      """
      And I should see "{CLEANUP_STEPS_CHECK}" is equal to "has-cleanup"

        * # clicking a cleanup entry shows its own duration instead of leaving the step-timing
        * # display frozen on the last real step's duration (which never changes shownStepIdx)
      And I execute in the current browser the following javascript
      """
      document.querySelector(".steps-cleanup:last-of-type").click();
      """
      And I execute in the current browser the following javascript and save the result to the variable "CLEANUP_TIMING_CHECK"
      """
      const data = JSON.parse(document.getElementById("replay-data").textContent);
      const lastCleanup = data.cleanupSteps[data.cleanupSteps.length - 1];
      const displayed = document.getElementById("step-timing-text").textContent;
      return displayed === lastCleanup.timingLabel
        ? "matches"
        : "mismatch displayed=" + displayed + " expected=" + lastCleanup.timingLabel;
      """
      And I should see "{CLEANUP_TIMING_CHECK}" is equal to "matches"

  Scenario: Replay view surfaces errors raised by a failing cleanup hook
    Given I run the command "cucu run data/features/feature_with_mixed_results.feature:16 --results {CUCU_RESULTS_DIR}/replay-hook-error-results" and expect exit code "1"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-hook-error-results --output {CUCU_RESULTS_DIR}/replay-hook-error-report" and expect exit code "0"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-hook-error-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Feature with mixed results"
      And I click the link "Scenario with after-hook error"
      And I click the link "🔁 Replay"
     Then I wait to see the text "1 /"

        * # every real Gherkin step passes here -- only the after-scenario hook fails -- so the
        * # Errors panel must still render from the cleanup entry alone, not just real steps.
        * # Checked via direct DOM query (not "I should see the text"/fuzzy.find) since the
        * # cleanup bar's own tooltip text ("Cleanup: <name>") would otherwise false-positive
        * # this same assertion even when the Errors panel itself renders nothing
      And I execute in the current browser the following javascript and save the result to the variable "CLEANUP_ERROR_PANEL_CHECK"
      """
      const panel = document.getElementById("vp-errors-panel");
      const hasLabel = !!panel && Array.from(panel.querySelectorAll(".log-step-label"))
        .some((el) => el.textContent === "Cleanup: after_hook_fail");
      const hasError = !!panel && Array.from(panel.querySelectorAll(".error-line"))
        .some((el) => el.textContent.includes("after-hook errors on purpose"));
      return hasLabel && hasError ? "found" : "not-found";
      """
      And I should see "{CLEANUP_ERROR_PANEL_CHECK}" is equal to "found"

  Scenario: Replay view renders with CUCU_SCREENSHOT_VIDEO enabled
    Given I run the command "cucu run data/features/echo.feature --results {CUCU_RESULTS_DIR}/replay-video-echo-results --env CUCU_SCREENSHOT_VIDEO=true" and expect exit code "0"
      And I run the command "cucu report {CUCU_RESULTS_DIR}/replay-video-echo-results --env CUCU_SCREENSHOT_VIDEO=true --output {CUCU_RESULTS_DIR}/replay-video-echo-report" and expect exit code "0"
      And I should see a file at "{CUCU_RESULTS_DIR}/replay-video-echo-results/Echo/Echo an environment variable/screenshots.mp4"
      And I start a webserver at directory "{CUCU_RESULTS_DIR}/replay-video-echo-report/" and save the port to the variable "PORT"
      And I open a browser at the url "http://{HOST_ADDRESS}:{PORT}/index.html"
     When I click the link "Echo"
      And I click the link "Echo an environment variable"
      And I click the link "🔁 Replay"
     Then I wait to see the text "1 / 6"
      And I should see the text "Given"
      And I should see the link "Echo"
