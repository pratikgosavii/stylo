# Generated manually: Order trial_otp (6-digit) and trial_begins_at (set when OTP verified)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_order_orderitem_status_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='trial_otp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='trial_begins_at',
            field=models.DateTimeField(blank=True, help_text='Set when trial OTP is verified (trial begin)', null=True),
        ),
    ]
