from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

@csrf_exempt  # Sentry webhooks won't have a CSRF token
def sentry_error_webhook(request):
    if request.method == 'POST':
        try:
            # Parse the JSON payload from Sentry
            payload = json.loads(request.body)

            # Log the error details to the console
            logger.error(f"Sentry Frontend Error: {json.dumps(payload, indent=2)}")

            return JsonResponse({"message": "Error logged successfully"}, status=200)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Sentry webhook payload: {str(e)}")
            return JsonResponse({"error": "Invalid payload"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)