import logging
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from . import forms
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from .models import Apartment, Buyer, Inquiry, Seller, Mediator,ApartmentImage,Purchase
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
import datetime
from decimal import Decimal


def Login(request):
    if request.method == 'POST':
        logging.debug(f"request = {request}")
        userform = AuthenticationForm(request,request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/apartments')

    userform = AuthenticationForm()
    return render(request, 'Login.html', {'form': userform})

def Logout(request):
    logout(request)
    messages.warning(request, 'התנתקת, תמיד אפשר לחזור שוב!')

    return render(request, 'HomePage.html')



def Register(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                user_id = user.id

            if form.cleaned_data['user_type'] == 'buyer':
                buyer = Buyer(userId=user)
                buyer.save()

            elif form.cleaned_data['user_type'] == 'seller':
                seller = Seller(userId=user)
                seller.save()

            elif form.cleaned_data['user_type'] == 'mediator':
                mediator = Mediator(userId=user, totalFees=0)
                mediator.save()

            messages.success(request, 'ההרשמה בוצעה בהצלחה!')
            return redirect('/login')
    else:
        form = forms.RegisterForm()
    return render(request, 'register.html', {'form': form})



def Apartments(request):
    user = request.user
    query = request.GET.get('q', '')
    filterBy = request.GET.get('filter_by', '')
    mediators = Mediator.objects.all().select_related('userId').values('userId__username','userId__id')
    sellers = Seller.objects.all().values()

    if is_mediator(user):
        apartments = Apartment.objects.filter(mediatorId=user.id)

    elif is_seller(user):
        apartments = Apartment.objects.filter(sellerId=user.id, mediatorId__isnull=True)

    else:
        apartments = Apartment.objects.all()

    if query and filterBy != '':
        if filterBy == 'city':
            apartments = apartments.filter(city__icontains=query)

        elif filterBy == 'rooms':
            apartments = apartments.filter(rooms=query)

        elif filterBy == 'floor':
            apartments = apartments.filter(floor=query)

        elif filterBy == 'neighborhood':
            apartments = apartments.filter(neighborhood__icontains=query)

    return render(request,'Apartments.html', {'apartments': apartments, 'sellers': sellers, 'mediators': mediators})

def HomePage(request):
    if request.session.get('first_visit', True):
        if request.user.is_authenticated:
            logout(request)

        request.session['first_visit'] = False

    return render(request, 'HomePage.html')


def is_mediator(user):
    print(f"user = {user}")
    return hasattr(user, 'mediator')

def is_buyer(user):
    return hasattr(user, 'buyer')

def is_seller(user):
    return hasattr(user, 'seller')


def add_inquiry(request):
    if request.method == 'POST':
        apartment_id = request.POST.get('apartmentId')
        buyer_id = request.user
        message = request.POST.get('message')

        try:
            apartment = Apartment.objects.get(id=apartment_id)
        except Apartment.DoesNotExist:
            messages.error(request, 'הדירה לא נמצאה')
            return redirect('homepage')

        buyer = Buyer.objects.filter(userId=buyer_id).first()
        if not buyer:
            messages.error(request, "הקונה לא נמצא")
            return redirect('homepage')

        inquiry = Inquiry(
            inquiriedId=buyer,
            apartmentId=apartment,
            message=message,
        )
        inquiry.save()
        messages.success(request, 'הפניה נשלחה בהצלחה')
        return redirect('homepage')

    messages.error(request, "בקשה לא חוקית")
    return HttpResponseBadRequest("Invalid request")



@login_required
def add_apartment(request):
    if request.method == 'POST':
        try:
            city = request.POST['city']
            neighborhood = request.POST['neighborhood']
            street = request.POST['street']
            house_number = request.POST['houseNumber']
            zip_code = request.POST['ZIP_code']
            floor = request.POST['floor']
            rooms = request.POST['rooms']
            price = request.POST['price']

        except KeyError as e:
            messages.error(request, f"חסרים נתונים: {e}")
            return redirect('add_apartment')

        is_immediate_evacuation = 'isImmediateEvacuation' in request.POST
        is_through_mediation = 'isThroughMediation' in request.POST
        mediator_id = request.POST.get('mediatorId') if is_through_mediation else None
        images = request.FILES.getlist('images')

        try:
            seller = Seller.objects.get(userId=request.user)
        except Seller.DoesNotExist:
            messages.error(request, 'המשתמש לא נמצא כ"מוכר"')
            return redirect('apartments')

        apartment = Apartment(
            city=city,
            neighborhood=neighborhood,
            street=street,
            houseNumber=house_number,
            ZIP_code=zip_code,
            floor=floor,
            rooms=rooms,
            price=price,
            isImmediateEvacuation=is_immediate_evacuation,
            isThroughMediation=is_through_mediation,
            sellerId=seller
        )

        if is_through_mediation:
            try:
                apartment.mediatorId = Mediator.objects.get(userId_id=mediator_id)
            except Mediator.DoesNotExist:
                messages.error(request, "המתווך לא נמצא")
                return redirect('add_apartment')

        apartment.save()

        for image in images:
            ApartmentImage.objects.create(apartment=apartment, image=image)

        messages.success(request, 'הדירה נוספה בהצלחה')
        return redirect('apartments')

    messages.error(request, "בקשה לא חוקית")
    return HttpResponse("Invalid request", status=400)

def apartment_inquiries(request,id):

    if request.method == 'GET':

        apartment = Apartment.objects.get(id=id)
        inquiries = Inquiry.objects.filter(apartmentId=apartment)

    return render(request, 'Inquiries.html', {
        'apartment': apartment,
        'inquiries': inquiries
    })



def buy(request,id,appartId):
    if request.method == 'GET':
        apartment = Apartment.objects.get(id=appartId)
        buyer = Buyer.objects.filter(userId=id).first()
        if apartment:
            apartment.isSoled = True
            apartment.save()
            if buyer:
                purchase = Purchase(
                    buyerId=buyer,
                    apartmentId=apartment,
                    date=datetime.datetime.now(),
                )
                purchase.save()
                if apartment.isThroughMediation:
                    medId=apartment.mediatorId
                    mediator = Mediator.objects.get(userId=medId)
                    if mediator:
                        if apartment.price is not None:
                            mediator.totalFees = apartment.price * Decimal('0.1')
                            mediator.save()
                            messages.success(request, 'העמלה נוספה למתווך שלך!')
                        else:
                            messages.error(request, 'המחיר לא נמצא עבור הדירה.')

                messages.success(request, 'המכירה בוצעה בהצלחה!!')
        else:
            return HttpResponse("הדירה לא נמצאה", status=404)

    return redirect('/apartments')

def Fees(request):

    if request.method == 'GET':
        user = request.user
        mediator = Mediator.objects.get(userId=user)
        fees = mediator.totalFees

    return render(request, 'Fees.html', {
        'fees': fees
    })
