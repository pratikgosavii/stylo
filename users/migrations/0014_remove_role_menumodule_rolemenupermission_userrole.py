# Remove Role, MenuModule, RoleMenuPermission, UserRole (no longer used)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_remove_user_firebase_uid'),
    ]

    operations = [
        migrations.DeleteModel(name='UserRole'),
        migrations.DeleteModel(name='RoleMenuPermission'),
        migrations.DeleteModel(name='MenuModule'),
        migrations.DeleteModel(name='Role'),
    ]
