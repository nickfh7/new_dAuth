import random
import string

# File for random utility functions

def random_string(stringLength=10):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))