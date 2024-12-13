from django.contrib import admin
from .models import Review, Restaurant
# Register your models here.

admin.site.register(Restaurant)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'rating', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'restaurant__name')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, 'Selected reviews have been approved.')
    approve_reviews.short_description = 'Approve selected reviews'
