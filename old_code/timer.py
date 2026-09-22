import time

class Timer:
    def __init__(self):
        self.start_time = None
        self.elapsed = 0.0
        self.running = False

    def start(self):
        if self.running:
            return
        self.start_time = time.time()
        self.running = True

    def stop(self):
        if not self.running:
            return self.elapsed
        self.elapsed += time.time() - self.start_time
        self.start_time = None
        self.running = False
        return self.elapsed

    def reset(self):
        self.start_time = None
        self.elapsed = 0.0
        self.running = False

    def get_elapsed(self):
        if self.running:
            return self.elapsed + (time.time() - self.start_time)
        return self.elapsed
