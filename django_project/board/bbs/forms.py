from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'name'}))
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'title'}))
    contents = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'contents'}))

    class Meta:
        model = Post
        fields = ['name', 'title', 'contents']