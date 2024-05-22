import time
from threading import Thread

class CPU:
    def __init__(self, frequency, name):
        self.frequency = frequency
        self.name = name
        self.running = False
        self.functions = []
        self.thread = None

    def add_function(self, func):
        self.functions.append(func)

    def play(self):
        self.running = True
        self.thread = Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def run(self):
        while self.running:
            for func in self.functions:
                func()
            time.sleep(1 / self.frequency)

    @staticmethod
    def stop_all_cpus():
        # Implement stopping logic for all CPUs if needed
        pass
