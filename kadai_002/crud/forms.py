from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Review, Reservation

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('score', 'comment')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['score'].widget = forms.Select(choices=[
            (1, '★'),
            (2, '★★'),
            (3, '★★★'),
            (4, '★★★★'),
            (5, '★★★★★'),
        ])
        self.fields['score'].widget.attrs['class'] = 'form-select'
        
        self.fields['comment'].widget = forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 5, 
            'placeholder': '店舗の感想を書いてください'
        })

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('reservation_date', 'number_of_people')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 日時入力フォーム
        self.fields['reservation_date'].widget = forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'min': '2023-01-01T00:00' 
        })
        self.fields['reservation_date'].label = "予約日時"

        self.fields['number_of_people'].widget = forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'placeholder': '人数を入力してください'
        })

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'