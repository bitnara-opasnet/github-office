from django import forms
from .models import Profile, ApiConfig
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model 

# 회원가입 폼
class RegisterForm(UserCreationForm):
    phone = forms.CharField()
    image = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = '아이디'
        self.fields['password1'].label = '암호'
        self.fields['password2'].label = '암호 확인'
        self.fields['email'].label = '이메일'
        self.fields['phone'].label = '전화번호'
        self.fields['last_name'].label = '성'
        self.fields['first_name'].label = '이름'
        self.fields['image'].label = '사진'
        self.fields['image'].required = False

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-user'

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email", "phone", "last_name", "first_name", "image")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data["phone"]
        user.image = self.cleaned_data["image"]
        user.save()
        
        user_profile = Profile(
            user = user,
            phone = self.cleaned_data["phone"],
            image = self.cleaned_data["image"],
        )
        if commit:
            user_profile.save()
        return user

# 회원 정보 폼
class ProfileForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-user'

    class Meta:
        model = Profile
        fields = ['phone', 'image']

# 회원 정보 수정 폼
class UserChangeForm(UserChangeForm):
    phone = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True
        self.fields['email'].label = '이메일'
        self.fields['last_name'].label = '성'
        self.fields['first_name'].label = '이름'
        self.fields['phone'].label = '전화번호' 

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-user'

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "last_name", "first_name", "phone") 

# 비밀번호 변경 폼
class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = '기존 비밀번호'
        self.fields['new_password1'].label = '새 비밀번호'
        self.fields['new_password2'].label = '새 비밀번호 확인'

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-user'

# 회원 정보 폼
class ApiConfigForm(forms.ModelForm):
    # password = forms.CharField(max_length=20, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-user'

    class Meta:
        model = ApiConfig
        fields = ['ipaddress', 'username', 'password']


# Flow Search 폼
class FlowSearchForm(forms.Form):
    time_range = forms.CharField()
    record_limit = forms.CharField()
    source_ip = forms.CharField()
    source_port = forms.CharField()
    destination_ip = forms.CharField()
    destination_port = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-user'
    