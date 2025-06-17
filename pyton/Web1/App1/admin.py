from django.contrib import admin
from . import models
# Register your models here.

class ApartmentImageInline(admin.TabularInline):
    model = models.ApartmentImage
    extra = 1


# admin.site.register(models.Apartment),
@admin.register(models.Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    inlines = [ApartmentImageInline]

admin.site.register(models.Inquiry),
admin.site.register(models.Purchase),
admin.site.register(models.Mediator),
admin.site.register(models.Buyer),
admin.site.register(models.Seller)