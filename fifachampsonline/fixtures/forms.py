from django import forms
from django.contrib.auth import get_user_model
from .models import Fixture, Purchase, HeadToHead
from datetime import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

User = get_user_model()

class HeadToHeadForm(forms.ModelForm):
    opponent = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label='Select opponent'
    )

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__()
        self.fields['opponent'].queryset = User.objects.exclude(pk=current_user.pk)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        if date and time:
            datetime_obj = datetime.datetime.combine(date, time)
            if datetime_obj <= datetime.datetime.now():
                raise forms.ValidationError("The date and time must be in the future.")
        return cleaned_data

    def clean_opponent(self):
        opponent = self.cleaned_data.get('opponent')
        if opponent == self.instance.player1:
            raise forms.ValidationError("You cannot play against yourself.")
        return opponent

    class Meta:
        model = Fixture
        fields = ['opponent']


class HeadToHeadRequestForm(forms.ModelForm):
    player2 = forms.ModelChoiceField(queryset=get_user_model().objects.all(), label='Opponent')
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), help_text='Please use 24-hour time format, e.g. 14:30')
    immediate_game = forms.BooleanField(required=False)

    class Meta:
        model = HeadToHead
        fields = ('player2', 'date', 'time', 'immediate_game')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(HeadToHeadRequestForm, self).__init__(*args, **kwargs)
        self.fields['player2'].queryset = self.fields['player2'].queryset.exclude(pk=self.request.user.pk)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        immediate_game = cleaned_data.get('immediate_game')

        # Check that the requested date is in the future
        if date and date < timezone.now().date():
            raise ValidationError('The requested date must be in the future.')

        # Check that the requested time is at least 30 minutes from now
        datetime = timezone.make_aware(timezone.datetime.combine(date, time))
        if datetime < timezone.now() + timezone.timedelta(minutes=30):
            raise ValidationError('The requested time must be at least 30 minutes from now.')

        # Check that an immediate game is not requested in the past
        if immediate_game and datetime < timezone.now():
            raise ValidationError('An immediate game cannot be requested in the past.')

        return cleaned_data


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['buyer', 'price', 'email', 'phone_number']
