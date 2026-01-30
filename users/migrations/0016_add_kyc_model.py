# Generated manually for KYC model (Tax & KYC Verification + Upload Documents)

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_remove_user_city_remove_user_is_subuser_user_address_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='KYC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gst', models.CharField(blank=True, help_text='GST (Mandatory for selling, unless exempted)', max_length=50, null=True)),
                ('pan_card_number', models.CharField(blank=True, max_length=20, null=True)),
                ('bank_account_number', models.CharField(blank=True, max_length=50, null=True)),
                ('account_holder_name', models.CharField(blank=True, max_length=255, null=True)),
                ('ifsc_code', models.CharField(blank=True, max_length=20, null=True)),
                ('gst_document', models.FileField(blank=True, help_text='GST (Scanned Copy)', null=True, upload_to='kyc/gst/')),
                ('pan_card_document', models.FileField(blank=True, help_text='Pan card (Scanned Copy)', null=True, upload_to='kyc/pan/')),
                ('address_proof_document', models.FileField(blank=True, help_text='Address Proof (Scanned Copy)', null=True, upload_to='kyc/address_proof/')),
                ('bank_proof_document', models.FileField(blank=True, help_text='Bank Proof (Scanned Copy)', null=True, upload_to='kyc/bank_proof/')),
                ('is_verified', models.BooleanField(default=False)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='kyc', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
