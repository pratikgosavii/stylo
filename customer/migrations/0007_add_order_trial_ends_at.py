# Generated manually: Order trial_ends_at (set when delivery boy ends trial)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_add_order_trial_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='trial_ends_at',
            field=models.DateTimeField(blank=True, help_text='Set when delivery boy ends trial (trial ended)', null=True),
        ),
    ]
