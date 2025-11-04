from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import home,products,cart, login ,details,register,logout,search_view,checkout_view,order_confirmation,profile_view

app_name = 'app'

urlpatterns = [
    path('', home, name='home'),
    path('products/', products, name='products'),   
    path('cart/', cart, name='cart'),
    path('login/', login, name='login'),
    path('detail/<int:Shirtid>/', details, name='details'),
    path("register/", register, name="register"),
    path('logout/',logout, name='logout'),
    path('search/',search_view, name='search'),
    path('checkout/', checkout_view, name='checkout'),
    path('order_confirmation/', order_confirmation, name='order_confirmation'),
    path('profile/',profile_view, name='profile'),
    

]


# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)