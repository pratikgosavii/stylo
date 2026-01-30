# Generated manually for vendor_store address and contact fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0006_store_offer_and_offer_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor_store',
            name='name',
            field=models.CharField(help_text='Store name', max_length=255),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='business_type',
            field=models.CharField(blank=True, help_text='Business type', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='store_mobile',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='store_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='house_building_no',
            field=models.CharField(blank=True, help_text='House/Building/Apartment No.', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='locality_street',
            field=models.CharField(blank=True, help_text='Locality/Area/Street', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='pincode',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='state',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='owner_gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='vendor_house_no',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='vendor_locality_street',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='vendor_pincode',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='vendor_state',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='vendor_store',
            name='vendor_city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
