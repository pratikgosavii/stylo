# Generated: Change product.serial_numbers from DecimalField to CharField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0012_alter_offer_heading_alter_offer_request_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='serial_numbers',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
