import hashlib
import random
import string

# File for random utility functions


def _sha512(data):
    return hashlib.sha512(data).hexdigest()


def random_string(stringLength=10):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))