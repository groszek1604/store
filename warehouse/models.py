from unicodedata import decimal
from django.db import models
from phone_field import PhoneField
from django.core.validators import MinValueValidator
from uuid import uuid4

class Promotion(models.Model):
    description = models.CharField(max_length=252)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=252, null=True)
    featured_product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']

class Product(models.Model):
    title = models.CharField(max_length=252, null=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=4, 
                                decimal_places=2,
                                validators=[MinValueValidator(1, message='Price could not be negative')])
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotion = models.ManyToManyField(Promotion, blank=True)
    slug = models.SlugField(default='-')

    def __str__(self) -> str:
        return self.title


class Customer(models.Model):

    MEMBERSHIP_BRONEZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONEZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold')
    ]

    first_name = models.CharField(max_length=252, null=False)
    last_name = models.CharField(max_length=252, null=False)
    email = models.EmailField(max_length=252, unique=False, null=False)
    phone_number = PhoneField(blank=True, help_text = 'Contact phone number')
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, 
                                    default=MEMBERSHIP_BRONEZE)

    def __str__(self) -> str:
        return f'{self.first_name}, {self.last_name}'

class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Completed'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES,
                                    default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(
                                    validators=[MinValueValidator(1, message='Price could not be negative')])
    unit_price = models.DecimalField(max_digits=6, 
                                    decimal_places=2)


class Adress(models.Model):
    street = models.CharField(max_length=252)
    city = models.CharField(max_length=252)
    city_code = models.CharField(max_length=252, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart =models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [['cart', 'product']]


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=252)
    description = models.TextField()
    date = models.DateField(auto_now=True)