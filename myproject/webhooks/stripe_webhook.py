import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from cart.models import Order

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook secret from your Stripe settings
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata']['order_id']  # Get the order ID from metadata
        print(f"Payment for {payment_intent['amount']} succeeded!") # in views payment_intent added metadata

        try:
            # Update  the db to mark the order as paid
            order = Order.objects.get(id=order_id)
            order.status = 'Paid'
            order.save()


            print(f"Payment for order {order_id} succeeded!")
        except Order.DoesNotExist:
            print(f"Order {order_id} not found.")

        # Update your database to mark the order as paid
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"Payment for {payment_intent['amount']} failed!")
        # Handle the failure in your system
    else:
        # Unexpected event type
        print(f"Unhandled event type {event['type']}")

    return HttpResponse(status=200)