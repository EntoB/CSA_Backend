from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .models import Feedback, Service
from accounts.helpers.utils import parse_json_request
from feedback.helpers.utils import analyze_sentiment
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


def submit_feedback(request):
    if request.method == 'POST':
        data, error = parse_json_request(request)
        if error:
            return error  # Return error response if JSON parsing fails

        customer = request.user
        message = data.get('message')

        # Analyze sentiment
        sentiment = analyze_sentiment(message)

        # Save feedback
        feedback = Feedback.objects.create(customer=customer, message=message, sentiment=sentiment)
        return JsonResponse({'message': 'Feedback submitted successfully', 'sentiment': sentiment}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# @user_passes_test(lambda u: u.role == 'superadmin')
def view_feedback(request):
    if request.method == 'GET':
        feedbacks = Feedback.objects.all()
        feedback_data = list(feedbacks.values('id', 'customer__username', 'message', 'sentiment', 'created_at'))
        return JsonResponse({'feedbacks': feedback_data}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# @user_passes_test(lambda u: u.is_superuser == 1,login_url='/')  # Restrict access to superadmins

# @csrf_exempt  # For local development; for production, use CSRF tokens properly
@login_required  # Ensures user is logged in via session
def add_service(request):
    user = request.user
    # Ensure the user is authorized (e.g., superadmin)
    if user.is_superuser != 1:
        return JsonResponse({'error': 'Unauthorized access'}, status=403)

    if request.method == 'POST':
        data, error = parse_json_request(request)
        if error:
            return error  # Return error response if JSON parsing fails
        print(f"Received data: {data}")
        # Extract service details
        name = data.get('name')
        description = data.get('description', '')
        category = data.get('category', '')

        if not name:
            return JsonResponse({'error': 'Service name is required'}, status=400)

        # Create and save the service
        service = Service.objects.create(name=name, description=description, category=category)
        print(f"Service created: {service}")
        return JsonResponse({'message': 'Service added successfully', 'service_id': service.id}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
