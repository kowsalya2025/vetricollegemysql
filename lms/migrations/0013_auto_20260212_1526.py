from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0012_alter_video_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='brochure',
            field=models.FileField(upload_to='brochures/', null=True, blank=True),
        ),
    ]

