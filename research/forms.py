from django import forms


class ResearchForm(forms.Form):
    research = forms.CharField(max_length=100, label=False, widget=forms.TextInput(attrs={'placeholder': 'Chercher'}))
