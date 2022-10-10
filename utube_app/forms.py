from .models import CustomUser
from django import forms
from allauth.account.forms import SignupForm

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