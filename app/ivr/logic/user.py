""" App logic functions (controller code) for managing users
"""
import random
import string


# TODO - look into generating a secure salt (for our application? per user?)

def create_6digit_id():
    return ''.join(random.choices(string.digits, k=6))

# TODO - write create user function