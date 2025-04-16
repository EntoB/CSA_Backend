from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .models import Feedback
from accounts.helpers.utils import parse_json_request
from feedback.helpers.utils import analyze_sentiment


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


@user_passes_test(lambda u: u.role == 'superadmin')
def view_feedback(request):
    if request.method == 'GET':
        feedbacks = Feedback.objects.all()
        feedback_data = list(feedbacks.values('id', 'customer__username', 'message', 'sentiment', 'created_at'))
        return JsonResponse({'feedbacks': feedback_data}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)