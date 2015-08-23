from django import forms
from django.db import models
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from gallery.models import Image, Gallery


class SearchForm(forms.Form):
    search = forms.CharField(max_length=100,
                             label='',
                             widget=forms.TextInput(attrs={
                                   'placeholder': 'Voir une galerie',
                                   'class': 'tt-query',
                                   'type': 'text',
                                   'autocomplete': 'off',
                                   'data-dict': '[]',
                                   'data-items': '4',
                             }))

    def __init__(self, data_source):
        self.base_fields['search'].widget.attrs['data-dict'] = data_source
        super(SearchForm, self).__init__()


class UserForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput(attrs={
        'placeholder': 'Login',
        'id': 'id_username',
        'type': 'text'
    }))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
        'placeholder': 'Mot de passe',
        'id': 'id_password',
        'type': 'password'
    }))


class UploadImage(forms.Form):
    img = forms.FileField(
        label='Image',
    )
    description = forms.CharField(max_length=200)
    place = forms.CharField(max_length=60)
    gallery_slug = forms.CharField(widget=forms.HiddenInput())


class GalleryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.base_fields['title'].label = "Titre"
        self.base_fields['title'].widget = forms.TextInput(attrs={'placeholder': "Champ obligatoire"})
        self.base_fields['description'].label = "Description"
        self.base_fields['description'].widget = forms.TextInput(attrs={'placeholder': "Champ facultatif"})
        self.base_fields['place'].label = "Lieu"
        self.base_fields['place'].widget = forms.TextInput(attrs={'placeholder': "Champ facultatif"})
        self.base_fields['public'].label = "Publique ?"
        self.base_fields['password'].label = "Mot de passe"
        super(GalleryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Gallery
        fields = ['title', 'description', 'place', 'public', 'password']
