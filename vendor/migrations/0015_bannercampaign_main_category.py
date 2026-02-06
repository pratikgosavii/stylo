# Add main_category to BannerCampaign for filtering banners by main category

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0005_notification_campaign_full_model'),
        ('vendor', '0014_bannercampaign_store_and_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='bannercampaign',
            name='main_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='banner_campaigns', to='masters.maincategory'),
        ),
    ]
