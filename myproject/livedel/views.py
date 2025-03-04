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
    
# @api_view(['GET'])
# def get_order(request, order_id):
#     """
#     Retrieve order details including status, ETA, and route data.
#     """
#     order = get_object_or_404(Order, id=order_id)
    
#     return Response({
#         'id': order.id,
#         'status': order.status,
#         'eta': order.eta,
#         'route_data': json.loads(order.route_data) if order.route_data else None,
#         'current_position_index': order.current_position_index,
#     }, status=status.HTTP_200_OK)
    
    
    
    
    
# @api_view(['POST'])
# def move_delivery(request, order_id):
#     """
#     Simulate real-time movement along the delivery route.
#     """
#     order = get_object_or_404(Order, id=order_id)

#     if order.status != Order.Status.EN_ROUTE or not order.route_data:
#         return Response({"error": "Order is not en route or has no route data."}, status=status.HTTP_400_BAD_REQUEST)

#     route = json.loads(order.route_data)

#     if order.current_position_index < len(route) - 1:
#         order.current_position_index += 1
#         order.save()

#         current_location = route[order.current_position_index]
#         return Response({
#             "latitude": current_location[1],  # Reverse lat/lon for consistency
#             "longitude": current_location[0],
#             "current_position_index": order.current_position_index
#         }, status=status.HTTP_200_OK)
#     else:
#         # If last point reached, mark as delivered
#         order.status = Order.Status.DELIVERED
#         order.save()
#         return Response({"message": "Order delivered."}, status=status.HTTP_200_OK)
    
    
# @api_view(['POST'])
# def move_delivery(request, order_id):
#     """
#     Simulate real-time movement along the delivery route.
#     """
#     order = get_object_or_404(Order, id=order_id)
    
#     if order.status != Order.Status.EN_ROUTE or not order.route_data:
#         return Response({"error": "Order is not en route or has no route data."}, status=status.HTTP_400_BAD_REQUEST)

#     route = json.loads(order.route_data)
    
#     if order.current_position_index < len(route) - 1:
#         order.current_position_index += 1
#         order.save()
        
#         current_location = route[order.current_position_index]
#         return Response({
#             "latitude": current_location[1],  # Reverse lat/lon for consistency
#             "longitude": current_location[0],
#             "current_position_index": order.current_position_index
#         }, status=status.HTTP_200_OK)
#     else:
#         # If last point reached, mark as delivered
#         order.status = Order.Status.DELIVERED
#         order.eta = now()
#         order.save()
#         return Response({"message": "Order delivered."}, status=status.HTTP_200_OK)
