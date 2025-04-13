import random
import string
import json
from django.http import JsonResponse

# Helper function to generate a random key
def generate_random_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

def parse_json_request(request):
    """
    Utility function to parse JSON data from the request body.
    Returns a tuple: (data, error)
    """
    try:
        data = json.loads(request.body)
        return data, None
    except json.JSONDecodeError:
        return None, JsonResponse({'error': 'Invalid JSON data'}, status=400)