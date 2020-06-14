from django.db import models

# Create your models here.

from django.contrib.auth.models import User

from .helpers import PayUHelper

class Product(models.Model):
    name = models.CharField(max_length=32)
    price= models.FloatField()
    def __str__(self): return self.name

class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self): return "Cart of {}, #{}".format(User,self.id)
    def add(self,product_id,quantity):
        for item in self.cartitem_set.all():
            if product_id == item.product.id:
                item.quantity += quantity
                item.save()
                return True
        CartItem.objects.create(
            cart = self,
            quantity = quantity,
            product = Product.objects.get(id=product_id)
        )
        return True
    def remove(self,product_id):
        for item in self.cartitem_set.all():
            if product_id == item.product.id:
                item.delete()
        return False

    def convert_to_order(self):
        order = Order.objects.create(
            user = self.user,
            payment_status = 'PREPARE'
        )
        for item in self.cartitem_set.all():
            OrderItem.objects.create(
                order = order,
                product = item.product,
                quantity = item.quantity
            )
        self.delete()
        return order


class CartItem(models.Model):
    cart     =  models.ForeignKey(Cart,on_delete=models.CASCADE)
    product  = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    def __str__(self): return "{} (x{})".format(self.product,self.quantity)


class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=16)
    payu_id = models.CharField(max_length=64,null = True)
    def __str__(self): return "Order of {}, #{}, status {}".format(User,self.id,self.payment_status)
    def request_paymaent(self):
        payuHelper = PayUHelper()
        result = payuHelper.newOrder(self.id, self.user, self.orderitem_set.all(),"Order {}".format(self.id))
        result_json = result.json()
        if result_json['status']['statusCode'] == 'SUCCESS':
            self.payu_id = result_json['orderId']
            self.payment_status = 'WAITING'
            self.save()
            return result_json
        else:
            raise Exception('Nie udało się utworzyć zamównia: {}'.format(result))
    def switch_to_success(self):
        self.payment_status = 'SUCCESS'
        self.save()

class OrderItem(models.Model):
    order    = models.ForeignKey(Order,on_delete=models.CASCADE)
    product  = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    def __str__(self): return "{} (x{})".format(self.product,self.quantity)
