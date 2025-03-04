from django.shortcuts import render
from django.utils.timezone import now

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order
import json
from .serializers import OrderSerializer
from .tasks import update_delivery_location


@api_view(['GET'])
def get_orders(request, order_id):
    """
    Retrieve the order details
    """
    order = get_object_or_404(Order, id=order_id)
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def start_delivery(request, order_id):
    """
    Start the delivery process, triggering the Celery task.
    """
    order = get_object_or_404(Order, id=order_id)

    if order.status == Order.Status.EN_ROUTE:
        return Response({"message": "Delivery already in progress.", "order": OrderSerializer(order).data})

    if order.status != Order.Status.PREPARING:
        return Response({"error": "Order is not in a deliverable state."}, status=status.HTTP_400_BAD_REQUEST)

    # Change status and trigger Celery task
    order.status = Order.Status.EN_ROUTE
    order.save()
    
    task = update_delivery_location.delay(order.id)  # Start movement task

    return Response(
        {
            "message": "Delivery started.",
            "order": OrderSerializer(order).data,  # Return order details
            "task_id": task.id,  # Show task ID in response
        },
        status=status.HTTP_200_OK,
    )
    
@api_view(['POST'])
def reset_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.status = Order.Status.PREPARING
        order.current_position_index = 1
        order.eta = None
        order.save()
        return Response({"message": "Order reset successfully."}, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)