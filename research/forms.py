from django import forms


class ResearchForm(forms.Form):
    research = forms.CharField(label='Aliment à rechercher', max_length=100)
