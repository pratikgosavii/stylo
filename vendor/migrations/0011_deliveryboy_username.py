# Generated manually: DeliveryBoy username for login

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0010_remove_reel_boost_post_budget'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryboy',
            name='username',
            field=models.CharField(blank=True, help_text='Login username for delivery boy', max_length=150, null=True, unique=True),
        ),
    ]
