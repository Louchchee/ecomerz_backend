from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response


from base.models import Product
from base.serializers import ProductSerializer, OrderSerializer
from datetime import datetime

from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data

    orderItems = data['orderItems']

    if orderItems and len(orderItems) == 0:
        return Response({'detail': 'No order items yet'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        #(1) Create Order
        order = Order.objects.create(
            user = user,
            paymentMethod = data['paymentMethod'],
            taxPrice = data['taxPrice'],
            shippingPrice = data['shippingPrice'],
            totalPrice = data['totalPrice']
        )

        #(2) Create shipping address
        shipping = ShippingAddress.objects.create(
            order = order,
            address = data['ShippingAddress']['address'],
            city = data['ShippingAddress']['city'],
           postalCode = data['ShippingAddress']['postalCode'],
            country = data['ShippingAddress']['country'],

        )


        #(3) Create order items and set order to orderItem relationship

        for itm in orderItems:
            product = Product.objects.get(_id=itm['product'])

            item = OrderItem.objects.create(
                 product = product,
                 order = order,
                 name = product.name,
                 qty = itm['qty'],
                 price = itm['price'],
                 image = product.image.url,
            )

            #(4) Update stock
            product.countInStock -= item.qty
            product.save()

    serializer = OrderSerializer(order, many=False)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
   
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):

    user = request.user

    try:
        order = Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)

            return Response(serializer.data)

        else:
            Response({'detail': 'You are not authorise to view this order'}, status=status.HTTP_400_BAD_REQUEST)
        
    except:
        return Response({'detail':'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(_id=pk)

    order.isPaid = True
    order.paidAt = datetime.now()
    order.save()


    return Response('Order was paid successfully')


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    order = Order.objects.get(_id=pk)

    order.isDelivered = True
    order.deliveredAt = datetime.now()
    order.save()


    return Response('Order was delivered successfully')

