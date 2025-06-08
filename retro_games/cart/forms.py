from django import forms

class CartAddGameForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'style': 'width: 60px'}))
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)