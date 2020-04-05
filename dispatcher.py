import abc
import threading
import time
from collections import deque


class Dispatcher:
    def __init__(self):
        self._lock = threading.Lock()
        self._queue = deque()
        self._sched_cv = threading.Condition(self._lock)
        self._shutdown_cv = threading.Condition(self._lock)
        self._stop_cnt = 0
        self._active_cnt = 0
        self._threads = set()

    def dispatch(self, task):
        with self._lock:
            self._queue.append(task)
            self._sched_cv.notify()
            idle = len(self._threads) - self._stop_cnt - self._active_cnt
            if len(self._queue) > idle:
                print("Task queue depth is %d" % (len(self._queue) - idle))

    def create_thread(self, target, args):
        t = threading.Thread(target=target, name="petty", args=args)
        t.daemon = True
        t.start()

    def schedule_threads(self, count):
        with self._lock:
            threads_ = self._threads
            thread_no_ = 0
            running_ = len(threads_) - self._stop_cnt
            while running_ < count:
                while thread_no_ in threads_:
                    thread_no_ += 1
                threads_.add(thread_no_)
                running_ += 1
                self.create_thread(self._thread_handler, (thread_no_,))
                self._active_cnt += 1
                thread_no_ += 1

            if running_ > count:
                self._stop_cnt += running_ - count
                self._sched_cv.notifyAll()

    def _thread_handler(self, thread_no):
        while True:
            with self._lock:

                while not len(self._queue):
                    self._active_cnt -= 1
                    self._sched_cv.wait()
                    self._active_cnt += 1

                if self._stop_cnt > 0:
                    self._stop_cnt -= 1
                    self._active_cnt -= 1
                    self._threads.discard(thread_no)
                    self._shutdown_cv.notify()
                    break

                task_ = self._queue.popleft()
                try:
                    task_.execute()
                except BaseException as e:
                    print(str(e))

    def shutdown(self, cancel_pending=True, timeout=5):
        self.schedule_threads(0)
        expiration = time.time() + timeout
        with self._lock:
            while self._threads:
                if time.time() > expiration:
                    print("%u threads still running" % len(self._threads))
                    break
                self._shutdown_cv.wait(0.1)
            if cancel_pending:
                if len(self._queue) > 0:
                    print("Cancel %d pending task(s)", len(self._queue))
                while self._queue:
                    task = self._queue.popleft()
                    task.cancel()
                self._sched_cv.notifyAll()
                return True
        return False
