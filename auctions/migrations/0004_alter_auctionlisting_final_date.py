# Generated by Django 4.2.6 on 2023-11-06 17:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_alter_auctionlisting_final_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='final_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 21, 17, 3, 39, 751555, tzinfo=datetime.timezone.utc)),
        ),
    ]
