# Generated for User.is_deliveryboy (delivery boy account flag)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_add_kyc_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_deliveryboy',
            field=models.BooleanField(default=False),
        ),
    ]
