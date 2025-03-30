import random
import string
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth import authenticate, login as auth_login
from .models import User, RegistrationKey


# Helper function to generate a random key
def generate_random_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

# Generate customer key - accessible by superadmins
def generate_customer_key(request):
    if request.method == 'POST':
        if request.user.role != 'superadmin':
            return JsonResponse({'error': 'Unauthorized access'}, status=403)
        
        key = generate_random_key()
        RegistrationKey.objects.create(key=key, for_role='customer') #dont forget to delete them after they are expired
        return JsonResponse({'customer_registration_key': key})

# Generate admin key - accessible by superadmins only
def generate_admin_key(request):
    if request.method == 'GET':
        # if request.user.role != 'superadmin':
        #     return JsonResponse({'error': 'Unauthorized access'}, status=403)

        key = generate_random_key()
        RegistrationKey.objects.create(key=key, for_role='admin')
        return JsonResponse({'admin_registration_key': key})


# User registration
def register_user(request):
    if request.method == 'POST':
        key = request.POST.get('registration_key')
        name = request.POST.get('name')
        password = request.POST.get('password')

        try:
            registration_key = RegistrationKey.objects.get(key=key)
            if not registration_key.is_valid():
                return JsonResponse({'error': 'Key has expired'}, status=400)

            # Create user
            user = User.objects.create(name=name, password=password, role=registration_key.for_role)
            registration_key.delete()  # Invalidate the key after use
            return JsonResponse({'message': 'User registered successfully', 'role': user.role})
        #make sure the responses are appropriate after the frontend is done
        except RegistrationKey.DoesNotExist:
            return JsonResponse({'error': 'Invalid registration key'}, status=400)

# User login
def login_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        user = authenticate(username=name, password=password)
        if user:
            auth_login(request, user)
            return JsonResponse({'message': 'Login successful', 'role': user.role})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
