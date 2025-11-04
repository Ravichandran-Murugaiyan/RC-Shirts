from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class Category(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)

    def __str__(self):
        return self.name

class Shirt(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False) 
    brand = models.CharField(max_length=100, null=False, unique=True) 
    model_name= models.CharField(max_length=100, null=False, unique=True) 
    description = models.TextField(null=False) 
    image = models.ImageField(upload_to='shirts/',blank=True,null=True)
    stock = models.PositiveIntegerField(default=10) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # ✅ New field to track inventory

    def is_avaiable(self):
        return self.stock > 0
    
    def __str__(self):
        return self.brand
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
        ('XXXL', 'Triple Extra Large'),
        ('4XL', '4X Large'),
        ('5XL', '5X Large'),
        ('FREE', 'Free Size'),
    ]
    
    size = models.CharField(
        max_length=5,
        choices=SIZE_CHOICES,
        blank=True,
        null=True,
        help_text="Select your clothing size"
    )

    def __str__(self):
        return self.username
    
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # If you have login system
    session_key = models.CharField(max_length=40, null=True, blank=True)  # For guest users
    product = models.ForeignKey('Shirt', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.product.price * self.quantity

User = get_user_model()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    customer_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ordered = models.BooleanField(default=False)
    stock_reduced = models.BooleanField(default=False)
    stock_reduction_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    def get_total_items(self):
        return sum(item.quantity for item in self.order_items.all())
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='order_items'  # Changed from 'items' to avoid conflict
    )
    product = models.ForeignKey(
        'Shirt',
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total(self):
        return self.price * self.quantity
    
class ShirtSizeStock(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
        ('3XL', 'Triple Extra Large'),

    ]

    shirt = models.ForeignKey(Shirt, on_delete=models.CASCADE, related_name='size_stocks')
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('shirt', 'size')

    def __str__(self):
        return f"{self.shirt.model_name} - {self.size} ({self.quantity})"


class Review(models.Model):
    shirt = models.ForeignKey(Shirt, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)