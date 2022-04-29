import sys
import threading
import traceback


class ThreadDumper(threading.Thread):
    """
    thread dumping class that can be easily stopped by calling the `.stop()`
    method.
    """

    def __init__(self, interval_min, stdout, *args, **kwargs):
        super(ThreadDumper, self).__init__(*args, **kwargs)
        self.interval_min = interval_min
        self.stdout = stdout
        self.running = False
        self.event = threading.Event()

    def stop(self):
        self.running = False
        self.event.set()

    def start(self):
        self.running = True
        super().start()

    def run(self):
        while self.running:
            self.stdout.write(f"\n{'*' * 80}\n")
            for thread in threading.enumerate():
                self.stdout.write(f"{thread}\n")
                traceback.print_stack(
                    sys._current_frames()[thread.ident], file=self.stdout
                )
                self.stdout.write("\n")
            self.stdout.write(f"{'*' * 80}\n")
            self.event.wait(self.interval_min * 60)


def start(interval_min):
    """
    start the thread dumper and return it so one can call the `.stop()` method
    on it to get it to quit

    parameters:
        interval_min(float): number of minutes between each thread stacktrace
                             dump to print

    returns:
        a ThreadDumper object that is a child of the threading.Thread class with
        the method `.stop()` to get the thread to quit
    """
    thread = ThreadDumper(interval_min, sys.stdout)
    thread.start()
    return thread
