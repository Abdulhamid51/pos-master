from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0331_merge_20250603_1442'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='returnproducttodeliver',
            name='valyuta',
        ),
        migrations.AlterField(
            model_name='debtor',
            name='tg_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='rejachiqim',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
