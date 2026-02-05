# OrderItem: only item-level statuses; accepted/rejected/in_transit/delivered live on Order only

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0014_alter_orderitem_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(
                choices=[
                    ('trial', 'Trial'),
                    ('ordered', 'Ordered'),
                    ('cancelled', 'Cancelled'),
                    ('returned', 'Returned'),
                    ('replace', 'Replace'),
                ],
                default='trial',
                max_length=28,
            ),
        ),
    ]
