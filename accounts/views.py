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


# Set user status (activate/deactivate) - accessible by superadmins only
def set_status(request):
    if request.method == 'POST':
        if request.user.role != 'superadmin':  # Ensure only super admins can perform this action
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        user_id = request.POST.get('user_id')  # ID of the user to activate/deactivate
        action = request.POST.get('action')  # 'activate' or 'deactivate'

        try:
            user = User.objects.get(id=user_id)
            if user.id == request.user.id:
                return JsonResponse({'error': 'You cannot deactivate your own account.'}, status=400)

            if action == 'activate':
                user.is_active = True
                user.save()
                return JsonResponse({'message': f'User {user.username} has been activated.'})
            elif action == 'deactivate':
                user.is_active = False
                user.save()
                return JsonResponse({'message': f'User {user.username} has been deactivated.'})
            else:
                return JsonResponse({'error': 'Invalid action. Use "activate" or "deactivate".'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
   
        
# delete user - accessible by superadmins only
def delete_user(request):
    if request.method == 'POST':
        if request.user.role != 'superadmin':  # Ensure only super admins can perform this action
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        user_id = request.POST.get('user_id')  # ID of the user to delete

        try:
            user = User.objects.get(id=user_id)

            # Prevent super admins from deleting themselves
            if user.id == request.user.id:
                return JsonResponse({'error': 'You cannot delete your own account.'}, status=400)

            user.delete()
            return JsonResponse({'message': f'User {user.username} has been deleted.'})

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)