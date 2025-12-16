from django.db import migrations, models


def set_initial_payment_method(apps, schema_editor):
    Appointment = apps.get_model('agendamento', 'Appointment')
    for ap in Appointment.objects.all():
        if ap.payment_status == 'pago':
            ap.payment_method = 'pix'
        else:
            ap.payment_method = 'cash'
        ap.save(update_fields=['payment_method'])


class Migration(migrations.Migration):

    dependencies = [
        ('agendamento', '0004_alter_appointment_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='payment_method',
            field=models.CharField(choices=[('pix', 'Pix'), ('cash', 'Dinheiro')], default='cash', max_length=10),
        ),
        migrations.RunPython(set_initial_payment_method, migrations.RunPython.noop),
    ]

