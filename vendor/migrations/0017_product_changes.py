# Remove wholesale_price, purchase_price; change color to FK; add size_chart_image

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0006_color'),
        ('vendor', '0016_product_fabric_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='wholesale_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='purchase_price',
        ),
        migrations.AddField(
            model_name='product',
            name='size_chart_image',
            field=models.ImageField(blank=True, null=True, upload_to='product_size_charts/'),
        ),
        migrations.RemoveField(
            model_name='product',
            name='color',
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='products',
                to='masters.color',
            ),
        ),
    ]
