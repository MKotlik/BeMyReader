""" App logic functions (controller code) for managing users
"""
import random
import string
from django.db import IntegrityError
from ivr.models import IVRUser

# TODO - look into generating a secure salt (for our application? per user?)

def create_6digit_id():
    return ''.join(random.choices(string.digits, k=6))

# TODO - come up with better way to create user with short, unique ID
# TODO - finish setting up user with initial info
def create_IVRUser(num_tries = 10):
    created = False
    attempt = 0
    user = None

    while not created and attempt < num_tries:
        try:
            id = create_6digit_id()
            user = IVRUser.objects.create(id=id)
            created = True
        except IntegrityError:
            # TODO - remove after testing
            attempt += 1
            print(f"Caught {attempt} IntegrityError trying to create user. Trying again")

    if not created:
        print("Error: Couldn't create user with unique ID")

    return user