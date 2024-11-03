from django import forms
from . import models

class CreateFromIgcForm(forms.ModelForm):

    class Meta:
        model = models.Flight
        fields = ['site', 'wing', 'comment', 'igc']

        # Dont display labels, placeholders are enough
        labels = dict()
        for field in fields:
            labels[field] = ""
        labels["igc"] = "Trace .igc"

        widgets = {
            'site': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Site"
             }),
            'wing': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Aile"
             }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "Commentaires"
             }),
            'igc': forms.FileInput(attrs={
                'class': 'form-control',
                # 'placeholder': "igc" doesn't work for fileinput
             }),
        }

class CreateForm(forms.ModelForm):

    class Meta:
        model = models.Flight
        fields = ['date', 'site', 'duration', 'wing', 'context', 'comment']

        # Dont display labels, placeholders are enough
        labels = dict()
        for field in fields:
            labels[field] = ""
        labels["igc"] = "Trace .igc"

        widgets = {
            'date': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Date"
             }),
            'site': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Site"
             }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Durée"
             }),
            'wing': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Aile"
             }),
            'context': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Cadre"
             }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "Commentaires"
             }),
        }
