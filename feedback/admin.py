from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('customer', 'sentiment', 'created_at')
    list_filter = ('sentiment', 'created_at')
    search_fields = ('customer__username', 'message')