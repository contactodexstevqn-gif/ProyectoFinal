# Generated manually for project delivery

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ConfiguracionTienda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_tienda', models.CharField(default='Fucsia Boutique', max_length=100)),
                ('telefono', models.CharField(blank=True, max_length=30)),
                ('direccion', models.CharField(blank=True, max_length=150)),
                ('correo', models.EmailField(blank=True, max_length=254)),
                ('stock_minimo_alerta', models.PositiveIntegerField(default=5)),
                ('tema_defecto', models.CharField(choices=[('dark', 'Oscuro'), ('light', 'Claro')], default='dark', max_length=10)),
                ('mostrar_agotados_catalogo', models.BooleanField(default=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Configuración de tienda',
                'verbose_name_plural': 'Configuración de tienda',
            },
        ),
    ]
