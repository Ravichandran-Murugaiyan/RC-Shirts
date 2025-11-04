from django.contrib import admin

from .models import Category,Shirt,Order
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import Shirt, ShirtSizeStock

admin.site.register(Category)
admin.site.register(Shirt)
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Order)


class ShirtSizeStockAdmin(admin.ModelAdmin):
    list_display = ('shirt', 'size', 'quantity')
    list_filter = ('shirt', 'size')

admin.site.register(ShirtSizeStock, ShirtSizeStockAdmin)