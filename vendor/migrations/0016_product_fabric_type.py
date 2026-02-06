# Add fabric_type choice field to product

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0015_bannercampaign_main_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='fabric_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('cotton', 'Cotton'),
                    ('polyester', 'Polyester'),
                    ('silk', 'Silk'),
                    ('wool', 'Wool'),
                    ('linen', 'Linen'),
                    ('rayon', 'Rayon'),
                    ('nylon', 'Nylon'),
                    ('denim', 'Denim'),
                    ('velvet', 'Velvet'),
                    ('chiffon', 'Chiffon'),
                    ('georgette', 'Georgette'),
                    ('satin', 'Satin'),
                    ('leather', 'Leather'),
                    ('blend', 'Blend'),
                    ('other', 'Other'),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
