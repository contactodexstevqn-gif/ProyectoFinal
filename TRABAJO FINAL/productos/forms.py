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
        fields = [
            'nombre',
            'categoria',
            'talla',
            'color',
            'precio',
            'stock',
            'imagen'
        ]

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),

            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),

            'talla': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: S, M, L'
            }),

            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Negro, Rosado, Blanco'
            }),

            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1000',
                'step': '1000',
                'placeholder': 'Ej: 50000'
            }),

            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1',
                'placeholder': 'Cantidad disponible'
            }),

            'imagen': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de la imagen'
            }),
        }

        labels = {
            'nombre': 'Nombre',
            'categoria': 'Categoría',
            'talla': 'Talla',
            'color': 'Color',
            'precio': 'Precio',
            'stock': 'Stock',
            'imagen': 'Imagen'
        }