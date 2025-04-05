import random
import string

# Helper function to generate a random key
def generate_random_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))