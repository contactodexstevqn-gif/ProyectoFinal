from django import forms
from .models import Producto, Categoria


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Blusas, Vestidos, Accesorios'
            })
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'talla', 'color', 'precio', 'stock', 'imagen']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),

            'categoria': forms.Select(attrs={'class': 'form-control'}),

            'talla': forms.TextInput(attrs={'class': 'form-control'}),

            'color': forms.TextInput(attrs={'class': 'form-control'}),

            
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1000',
                'step': '1000',
                'placeholder': 'Ej: 50000'
            }),

            
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1'
            }),

            'imagen': forms.TextInput(attrs={'class': 'form-control'}),
        }