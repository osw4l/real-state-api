from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class BaseUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label=_('first name'))
    last_name = forms.CharField(label=_('last name'))

    class Meta:
        model = User
        exclude = (
            'last_login',
            'date_joined',
            'groups',
            'user_permissions',
            'password',
            'is_active',
            'email',
            'is_staff',
            'is_superuser',
        )
        fields = '__all__'


