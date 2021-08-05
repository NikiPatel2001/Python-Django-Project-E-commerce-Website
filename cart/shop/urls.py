from django.urls import path
from . import views
from .views import Login, Signup

urlpatterns = [
    path("login/", Login.as_view(), name="Login"),
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>", views.productview, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path("signup/", Signup.as_view(), name="SignUp"),
    path("logout/", views.logout, name="Logout"),
    path("gallary/", views.gallary, name="Gallary"),

]