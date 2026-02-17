from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0004_create_tool'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculumday',
            name='tools',
            field=models.ManyToManyField(blank=True, related_name='curriculum_days', to='lms.tool'),
        ),
    ]
