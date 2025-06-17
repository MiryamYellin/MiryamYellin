from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Apartment, Mediator


class RegisterForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=[('buyer', 'קונה'), ('seller', 'מוכר'), ('mediator', 'מתווך')])

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'user_type']

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['city', 'neighborhood', 'street', 'houseNumber', 'ZIP_code', 'floor', 'rooms', 'price',
                  'isImmediateEvacuation', 'isThroughMediation', 'mediatorId', 'sellerId']

    def clean_mediatorId(self):
        is_through_mediation = self.cleaned_data.get('isThroughMediation', False)
        mediator = self.cleaned_data.get('mediatorId')
        if is_through_mediation and not mediator:
            raise forms.ValidationError('יש לבחור מתווך אם בחרת בתיווך')
        return mediator