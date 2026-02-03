import json
import queue
import threading
import trio


class BidiCollectorManager:

    def __init__(self):
        self.collector = None

    def initialize(self, driver):
        if self.collector is None:
            self.collector = BidiCollector(driver)
        self.collector.start_background()

    def stop_and_save(self, path, timeout=60):
        self.collector.end_and_wait(timeout=timeout)
        self.collector.save(path)


class BidiCollector:
    """
    Runs Selenium BiDi (Trio) in a background thread, collects
    Tracing.dataCollected events, and exposes a synchronous API
    suitable for Behave / classic WebDriver code.
    """

    def __init__(self, driver):
        self._driver = driver

        self._thread = None
        self._cmd_q = queue.Queue()

        self._ready = threading.Event()
        self._trace_done = threading.Event()
        self._shutdown_done = threading.Event()

        self._lock = threading.Lock()
        self._trace_events = []
        self._last_error = None

    # ---------- public API (sync) ----------

    def start_background(self):
        """Start the Trio/BiDi loop in a daemon thread (idempotent)."""
        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(
            target=self._thread_main,
            name="bidi-tracing",
            daemon=True,
        )
        self._thread.start()

        if not self._ready.wait(timeout=10):
            raise RuntimeError("BiDi background thread did not become ready")

        if self._last_error:
            raise RuntimeError("BiDi background thread failed") from self._last_error

    def begin(self):
        """Start tracing."""
        self.start_background()
        self._trace_done.clear()

        with self._lock:
            self._trace_events.clear()

        class TraceConfig:

            def to_json(self):
                return {
                    "recordMode": "recordAsMuchAsPossible",
                    "includedCategories": [
                        "devtools.timeline",
                        "disabled-by-default-devtools.timeline.frame",
                        "disabled-by-default-devtools.timeline.stack",
                        "devtools.net",
                    ],
                }

        self._cmd_q.put({
            "op": "start",
            "trace_config": TraceConfig(),
        })

    def end_and_wait(self, timeout=30):
        """Stop tracing and wait for Tracing.tracingComplete."""
        self.start_background()
        self._cmd_q.put({"op": "end"})

        if not self._trace_done.wait(timeout=timeout):
            raise TimeoutError("Timed out waiting for tracingComplete")

        if self._last_error:
            raise RuntimeError("Tracing failed") from self._last_error

    def save(self, path):
        """Write collected trace data to a JSON file."""
        with self._lock:
            payload = {"traceEvents": list(self._trace_events)}

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    def shutdown(self, timeout=5):
        """Shut down the background thread cleanly."""
        if not self._thread:
            return

        self._cmd_q.put({"op": "quit"})
        self._shutdown_done.wait(timeout=timeout)

    # ---------- background thread ----------

    def _thread_main(self):
        try:
            trio.run(self._trio_main)
        except Exception as e:
            self._last_error = e
            self._ready.set()
            self._trace_done.set()
            self._shutdown_done.set()

    async def _trio_main(self):
        async with self._driver.bidi_connection() as connection:
            session = connection.session
            devtools = connection.devtools

            data_listener = session.listen(devtools.tracing.DataCollected)
            done_listener = session.listen(devtools.tracing.TracingComplete)

            self._ready.set()

            async with data_listener, done_listener:
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(self._consume_data, data_listener)
                    nursery.start_soon(self._consume_done, done_listener)
                    nursery.start_soon(self._command_loop, session, devtools)

    async def _consume_data(self, data_listener):
        try:
            async for evt in data_listener:
                with self._lock:
                    print("ex...")
                    self._trace_events.extend(evt.value)
        except Exception as e:
            self._last_error = e
            self._trace_done.set()

    async def _consume_done(self, done_listener):
        try:
            async for _ in done_listener:
                self._trace_done.set()
        except Exception as e:
            self._last_error = e
            self._trace_done.set()

    async def _command_loop(self, session, devtools):
        while True:
            cmd = await trio.to_thread.run_sync(self._cmd_q.get)
            op = cmd.get("op")

            try:
                if op == "start":
                    self._last_error = None
                    await session.execute(
                        devtools.tracing.start(
                            transfer_mode="ReportEvents",
                            trace_config=cmd["trace_config"],
                        )
                    )

                elif op == "end":
                    print("devtools.tracing.end")
                    await session.execute(devtools.tracing.end())

                elif op == "quit":
                    self._shutdown_done.set()
                    return

            except Exception as e:
                self._last_error = e
                self._trace_done.set()

                if op == "quit":
                    self._shutdown_done.set()
                    return

