# Generated manually: Remove boost_post and budget from Reel

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0009_spotlightproduct'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reel',
            name='boost_post',
        ),
        migrations.RemoveField(
            model_name='reel',
            name='budget',
        ),
    ]
