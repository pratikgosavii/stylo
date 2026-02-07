# Add Color model (master for product color)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0005_notification_campaign_full_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
    ]
