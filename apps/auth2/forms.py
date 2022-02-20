from .models import CompanyUser
from apps.utils.forms import BaseUserCreationForm


class CompanyUserAdminForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = CompanyUser
