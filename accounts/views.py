from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from .models import User, RegistrationKey
from django.contrib.auth.hashers import make_password

from accounts.helpers.utils import generate_random_key
from accounts.helpers.utils import parse_json_request


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
    if request.method == 'GET':
        # if request.user.is_superuser == 0:
        #     return JsonResponse({'error': 'Unauthorized access'}, status=403)

        key = generate_random_key()
        RegistrationKey.objects.create(key=key, for_role='admin')
        return JsonResponse({'admin_registration_key': key})


# User registration
def register_user(request):
    if request.method == 'POST':
        data, error = parse_json_request(request)
        if error:
            return error  # Return error response if JSON parsing fails

        key = data.get('registration_key')
        username = data.get('username')
        password = data.get('password')
        phone_number = data.get('phone_number')

        try:
            registration_key = RegistrationKey.objects.get(key=key)
            if not registration_key.is_valid():
                return JsonResponse({'error': 'Key has expired'}, status=400)

            # Create user
            user = User.objects.create(
                username=username,
                phone_number=phone_number,
                password=make_password(password),
                role=registration_key.for_role
            )
            registration_key.delete()  # Invalidate the key after use
            return JsonResponse({'message': 'User registered successfully', 'role': user.role}, status=201)
        except RegistrationKey.DoesNotExist:
            return JsonResponse({'error': 'Invalid registration key'}, status=400)

# User login
from django.http import JsonResponse

def login_user(request):
    if request.method == 'POST':
        data, error = parse_json_request(request)
        if error:
            return error

        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                return JsonResponse({'message': 'Login successful', 'role': user.role}, status=200)
            else:
                return JsonResponse({'error': 'Account is deactivated. Please contact support.'}, status=403)
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Set user status (activate/deactivate) - accessible by superadmins only
def set_status(request):
    if request.method == 'POST':
        data, error = parse_json_request(request)
        if error:
            return error  # Return error response if JSON parsing fails

        if request.user.role != 'superadmin':  # Ensure only superadmins can perform this action
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        user_id = data.get('user_id')  # ID of the user to activate/deactivate
        action = data.get('action')  # 'activate' or 'deactivate'

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
        data, error = parse_json_request(request)
        if error:
            return error  # Return error response if JSON parsing fails

        if request.user.role != 'superadmin':  # Ensure only superadmins can perform this action
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        user_id = data.get('user_id')  # ID of the user to delete

        try:
            user = User.objects.get(id=user_id)

            # Prevent superadmins from deleting themselves
            if user.id == request.user.id:
                return JsonResponse({'error': 'You cannot delete your own account.'}, status=400)

            user.delete()
            return JsonResponse({'message': f'User {user.username} has been deleted.'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
        
# View all customers - accessible by superadmins only
def view_customers(request):
    if request.method == 'GET':
        # Check if the requesting user is a superadmin
        if request.user.role != 'superadmin':
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        # Fetch all users with the role 'customer'
        customers = User.objects.filter(role='customer')
        customer_data = list(customers.values('id', 'username', 'phone_number', 'email', 'is_active'))
        return JsonResponse({'customers': customer_data}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# View all admins - accessible by superadmins only
def view_admins(request):
    if request.method == 'GET':
        # Check if the requesting user is a superadmin
        if request.user.role != 'superadmin':
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        # Fetch all users with the role 'admin'
        admins = User.objects.filter(role='admin')
        admin_data = list(admins.values('id', 'username', 'phone_number', 'email', 'is_active'))
        return JsonResponse({'admins': admin_data}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)