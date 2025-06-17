from django.urls import path
from . import views



urlpatterns = [
    path("", views.HomePage, name="homepage"),
    path("register", views.Register, name="register"),
    path("login", views.Login, name="login"),
    path("logout", views.Logout, name="logout"),
    path("apartments", views.Apartments, name="apartments"),
    path('add_apartment/', views.add_apartment, name='add_apartment'),
    path('add-inquiry/', views.add_inquiry, name='add_inquiry'),
    path('inquiries/<int:id>/', views.apartment_inquiries, name='inquiries'),
    path('fees', views.Fees, name='fees'),
    path('buy/<int:id>/<int:appartId>/', views.buy, name='buy')
]