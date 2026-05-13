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

class VendedorEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Nombre del vendedor'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Apellido del vendedor'
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'Usuario de acceso'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Correo electrónico'
            }),
        }

        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'username': 'Vendedor',
            'email': 'Correo'
        }       
