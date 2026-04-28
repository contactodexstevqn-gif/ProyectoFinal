from django import forms
from django.contrib.auth.models import User


class VendedorForm(forms.ModelForm):
    contra = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput()
    )

    confirmarContra = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean(self):
        cleaned_data = super().clean()

        contra = cleaned_data.get('contra')
        confirmarContra = cleaned_data.get('confirmarContra')

        if contra and confirmarContra and contra != confirmarContra:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        return cleaned_data

        
