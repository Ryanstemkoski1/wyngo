from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("retailer", "0011_alter_location_address1_alter_location_address2_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailer',
            name='app_id',
            field=models.CharField(help_text='Please carefully review the entered value to ensure it is correct.',
                                   max_length=50),
        ),
        migrations.AlterField(
            model_name='retailer',
            name='app_secret',
            field=models.CharField(help_text='Please carefully review the entered value to ensure it is correct.',
                                   max_length=100),
        ),
    ]
