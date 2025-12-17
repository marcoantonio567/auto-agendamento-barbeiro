from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('agendamento', '0008_alter_appointment_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='reminder_sent',
            field=models.BooleanField(default=False),
        ),
    ]

