from django import forms

from .models import Categoria, Producto


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
            'imagen',
            'imagen_url'
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
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'imagen_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com/imagen.jpg'
            }),
        }

        labels = {
            'nombre': 'Nombre',
            'categoria': 'Categoria',
            'talla': 'Talla',
            'color': 'Color',
            'precio': 'Precio',
            'stock': 'Stock',
            'imagen': 'Imagen del producto',
            'imagen_url': 'URL de imagen'
        }


class ProductoEditForm(ProductoForm):
    class Meta(ProductoForm.Meta):
        fields = [
            'nombre',
            'categoria',
            'talla',
            'color',
            'precio',
            'imagen',
            'imagen_url'
        ]