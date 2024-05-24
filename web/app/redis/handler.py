from functools import wraps


class CeleryQueue:
    def __init__(self, lab=None):
        self.queue = []
        self.lab = lab

    def add(self, user_answer):
        self.queue.append(user_answer)

    def get(self):
        return self.queue.pop(0)


def redis_cache(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # some code here
        return func(*args, **kwargs)

    return wrapper


def redis_cache_delete(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # some code here
        return func(*args, **kwargs)

    return wrapper


def handle_lab_challenge(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        users = 1  # get users answer

        return func(*args, **kwargs)

    return wrapper


# Get user answer from celery queue
def consume():
    pass


# Add user answer to celery queue
def produce():
    pass
