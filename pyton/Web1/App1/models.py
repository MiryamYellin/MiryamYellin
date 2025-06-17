import datetime
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.timezone import now

class Mediator(models.Model):
    userId = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    totalFees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.userId}"

class Buyer(models.Model):
    userId = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"{self.userId}"

class Seller(models.Model):
     userId = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

     def __str__(self):
         return f"{self.userId}"
class Apartment(models.Model):
    city = models.CharField(max_length=30)
    neighborhood = models.CharField(max_length=40)
    street = models.CharField(max_length=40)
    houseNumber = models.IntegerField(validators=[MinValueValidator(1)])
    ZIP_code = models.CharField(max_length=7)
    floor = models.IntegerField()
    rooms = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    isImmediateEvacuation = models.BooleanField(default=False)
    isSoled = models.BooleanField(default=False)
    isThroughMediation = models.BooleanField(default=False)
    mediatorId = models.ForeignKey(Mediator, on_delete=models.CASCADE, null=True, blank=True)
    sellerId = models.ForeignKey(Seller, on_delete=models.CASCADE)


class ApartmentImage(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='apartments/')

    def __str__(self):
        return f"Image for {self.apartment}"

class Inquiry(models.Model):
    inquiriedId = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    apartmentId = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
    message = models.CharField(max_length=200)

class Purchase(models.Model):
    buyerId = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    apartmentId = models.OneToOneField(Apartment, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.date.today())