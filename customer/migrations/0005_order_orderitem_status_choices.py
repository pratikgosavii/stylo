# Generated manually: Order and OrderItem status choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0004_order_delivery_otp_order_delivery_otp_generated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('ready_to_dispatch', 'Ready to Dispatch'),
                    ('not_accepted', 'Not Accepted'),
                    ('accepted', 'Accepted'),
                    ('in_transit', 'In Transit'),
                    ('trial_begin', 'Trial Begin'),
                    ('trial_ended', 'Trial Ended'),
                    ('cancelled', 'Cancelled'),
                    ('completed', 'Completed'),
                ],
                default='not_accepted',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(
                choices=[
                    ('ordered', 'Ordered'),
                    ('returned', 'Returned'),
                    ('replace', 'Replace'),
                ],
                default='ordered',
                max_length=28,
            ),
        ),
    ]
