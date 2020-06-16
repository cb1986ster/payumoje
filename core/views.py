from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .models import Cart, Product, Order, OrderItem, CartItem

import json

def home(request):
    return render(request,'core/home.html', {
        'products':Product.objects.all()
    })

def addToCart(request):
    user = request.user
    if not(user):
        return render(request,'core/error.html', { 'error': 'Przedstaw się najpierw!(zaloguj)' })
    try:
        cart = Cart.objects.get(user=request.user)
    except Exception as e:
        cart = Cart.objects.create(user=user)

    try:
        cart.add(
            int(request.POST['pid']),
            int(request.POST['quantity'])
        )
        return redirect('/')
    except Exception as e:
        return render(request,'core/error.html', { 'error': 'Coś nie tak z produktem: {}'.format(e) })

def removeFromCart(request):
    user = request.user
    if not(user):
        return render(request,'core/error.html', { 'error': 'Przedstaw się najpierw!(zaloguj)' })
    try:
        cart = Cart.objects.get(user=request.user)
    except Exception as e:
        cart = Cart.objects.create(user=user)

    try:
        cart.remove(
            int(request.POST['pid'])
        )
        return redirect('/')
    except Exception as e:
        return render(request,'core/error.html', { 'error': 'Coś nie tak z produktem: {}'.format(e) })

def chceckout(request):
    return render(request,'core/chceckout.html')

def chceckoutConfirm(request):
    user = request.user
    if not(user):
        return render(request,'core/error.html', { 'error': 'Przedstaw się najpierw!(zaloguj)' })
    try:
        cart = Cart.objects.get(user=request.user)
    except Exception as e:
        return render(request,'core/error.html', { 'error': 'Kółki się urwały temu koszyku... ({})'.format(e) })

    try:
        order = cart.convert_to_order()
    except Exception as e:
        return render(request,'core/error.html', { 'error': 'Pakowanie do zamówinia nie udane: {}'.format(e) })

    try:
        payment_request = order.request_paymaent()
    except Exception as e:

        return render(request,'core/error.html', { 'error': 'Nie udało się wyciągnąć ręki po płatność({}): {}'.format(type(e),e) })

    return redirect(payment_request['redirectUri'])

def orderStatus(request,order_id):
    order = Order.objects.get(pk=order_id)
    return render(request,'core/order-view.html',{'order':order})

from .helpers import PayUHelper
def orderStatusData(request,order_id):
    order = Order.objects.get(pk=order_id)
    if order.payment_status != 'SUCCESS' and order.payment_status != 'ERR':
        try:
            payUHelper = PayUHelper()
            details = payUHelper.orderData(order.payu_id).json()
            if details['orders'][0]['status'] == 'COMPLETED':
                order.switch_to_success()
        except Exception as e:
            pass

    return JsonResponse({
        'id':order.id,
        'payment_status':order.payment_status,
    })

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def payuNotification(request):
    try:
        data = json.loads(request.body)
        if data['order']['status'] == 'COMPLETED':
            # TODO: dodać weryfikację płatności !!!
            order = Order.objects.get(id=data['order']['extOrderId'])
            order.switch_to_success()
        return HttpResponse('Success!')
    except Exception as e:
        resp = HttpResponse('Error: {}'.format(e))
        resp.status_code = 500
        return resp

'''
PENDING 	Płatność jest w trakcie rozliczenia.
WAITING_FOR_CONFIRMATION 	system PayU oczekuje na akcje ze strony sprzedawcy w celu wykonania płatności. Ten status występuje w przypadku gdy auto-odbiór na POSie sprzedawcy jest wyłączony.
COMPLETED 	Płatność została zaakceptowana w całości. Środki są dostępne do wypłaty.
CANCELED 	Płatność została anulowana. Płacący nie został obciążony (nie nastąpił przepływ środków między płacącym a Payu).
'''
