from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('agendamento', '0005_appointment_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='status',
            field=models.CharField(max_length=10, default='ativo'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='cancel_reason',
            field=models.CharField(max_length=255, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='appointment',
            name='cancelled_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='cancelled_by',
            field=models.CharField(max_length=10, blank=True, default=''),
        ),
        migrations.AlterUniqueTogether(
            name='appointment',
            unique_together={('barber', 'date', 'hour', 'status')},
        ),
    ]
