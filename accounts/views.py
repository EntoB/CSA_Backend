from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth import authenticate, login as auth_login
from .models import User, RegistrationKey
from django.contrib.auth.hashers import make_password

from accounts.helpers.utils import generate_random_key


# Generate customer key - accessible by superadmins
def generate_customer_key(request):
    if request.method == 'POST':
        if request.user.role != 'superadmin': #adminum mechal alebet
            return JsonResponse({'error': 'Unauthorized access'}, status=403)
        
        key = generate_random_key()
        RegistrationKey.objects.create(key=key, for_role='customer') #dont forget to delete them after they are expired
        return JsonResponse({'customer_registration_key': key})

# Generate admin key - accessible by superadmins only
def generate_admin_key(request):
    if request.method == 'POST':
        if request.user.is_superuser == 0:
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        key = generate_random_key()
        RegistrationKey.objects.create(key=key, for_role='admin')
        return JsonResponse({'admin_registration_key': key})


# User registration
def register_user(request):
    if request.method == 'POST':
        key = request.POST.get('registration_key')
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        try:
            registration_key = RegistrationKey.objects.get(key=key)
            if not registration_key.is_valid():
                return JsonResponse({'error': 'Key has expired'}, status=400)

            # Create user
            user = User.objects.create(username=username,phone_number = phone_number, password=make_password(password), role=registration_key.for_role)
            registration_key.delete()  # Invalidate the key after use
            return JsonResponse({'message': 'User registered successfully', 'role': user.role})
        #make sure the responses are appropriate after the frontend is done
        except RegistrationKey.DoesNotExist:
            return JsonResponse({'error': 'Invalid registration key'}, status=400)

# User login
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            return JsonResponse({'message': 'Login successful', 'role': user.role})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
