# Generated manually: StoreCoverMedia model and media_type

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0007_add_store_address_contact_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreCoverMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video')], default='image', help_text='Photo or video', max_length=10)),
                ('media', models.FileField(help_text='Cover photo or video file', upload_to='store/cover_media/')),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order (lower first)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cover_media', to='vendor.vendor_store')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
    ]
