import time

class Timer:
    def __init__(self, message: str):
        self.message = message

    def __enter__(self):
        self.start = time.time()

    # TODO: What are the types of these...?
    def __exit__(self, exc_type, exc_value, traceback):
        self.log_message()

    def log_message(self):
        self.finish = time.time()
        duration = self.finish - self.start
        print(f"-> {self.message}: Ran for {duration:.2f}s")
