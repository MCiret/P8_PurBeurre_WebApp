from django import forms


class ResearchForm(forms.Form):
    research = forms.CharField(max_length=100, initial='Chercher', label=False)
