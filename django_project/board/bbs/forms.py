from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    contents = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '10'}))

    class Meta:
        model = Post
        fields = ('name', 'title', 'contents',)