from django import forms
from allauth.account.forms import SignupForm
from .models import CustomUser, Author

class MyCustomSocialSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        # Call the init of the parent class
        super().__init__(*args, **kwargs)
        self.fields[('phone')] = forms.CharField(max_length=70, required=True)

    def custom_signup(self, request, user):
        user.phone = self.cleaned_data[('phone')]
        user.save()

    def save(self, request):
        user = super(MyCustomSocialSignupForm, self).save(request)
        return user


class AuthorForm(forms.ModelForm):
	class Meta:
		model = Author
		fields = '__all__'
		exclude = ['identity', 'is_banned']


class CreateAuthorForm(forms.Form):
    profile_pic = forms.ImageField(label='Your profile picture')


class SMSForm(forms.Form):
    SMS_code = forms.IntegerField(label='SMS code')