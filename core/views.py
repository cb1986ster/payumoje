from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from .models import Cart, Product, Order, OrderItem, CartItem

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

    return redirect(payment_request.redirectUri)


def payuNotification(request):
    try:
        raise Exception('NOT_IMPLEMENTED')
        return HttpResponse('Success!')
    except Exception as e:
        resp = HttpResponse('Error: {}'.format(e))
        resp.status_code = 500
        return resp
