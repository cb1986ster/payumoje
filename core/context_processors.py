from datetime import datetime

def current_time(request):
    return { 'time_now' : datetime.now() }

def server_load(request):
    try:
        with open('/proc/loadavg','rt') as file:
            server_load = float( file.readline().split()[0] )
    except Exception as e:
        server_load = '?'
    return { 'server_load' : server_load }

def user_cart(request):
    cart = None
    try:
        cart = request.user.cart_set.all()[0] 
    except Exception as e: pass
    return { 'cart' : cart }
