# Generated by Django 4.2.6 on 2023-11-06 15:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='final_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 21, 15, 50, 12, 594711)),
        ),
    ]
