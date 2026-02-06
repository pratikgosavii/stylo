# Add store and product back to BannerCampaign for redirect_to logic

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0013_alter_product_serial_numbers'),
    ]

    operations = [
        migrations.AddField(
            model_name='bannercampaign',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='banners', to='vendor.vendor_store'),
        ),
        migrations.AddField(
            model_name='bannercampaign',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='banner_campaigns', to='vendor.product'),
        ),
    ]
