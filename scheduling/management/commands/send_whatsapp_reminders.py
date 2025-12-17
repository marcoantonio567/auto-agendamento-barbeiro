from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime, timedelta
from scheduling.models import Appointment
from core.helpers.phone_validation import PhoneValidator
from whastsapp_api import send_mensage


class Command(BaseCommand):
    help = "Envia lembrete por WhatsApp 30 minutos antes do agendamento"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Não envia WhatsApp e não altera o banco; apenas loga a ação",
        )
        parser.add_argument(
            "--window-seconds",
            type=int,
            default=60,
            help="Janela de disparo em segundos ao redor dos 30 minutos (padrão: 60s)",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        window_seconds = int(options.get("window_seconds", 60))

        now = datetime.now()
        window = timedelta(seconds=window_seconds)
        target_offset = timedelta(minutes=30)

        qs = Appointment.objects.filter(status="ativo", reminder_sent=False)

        processed = 0
        to_send = []

        for ap in qs:
            ap_dt = datetime.combine(ap.date, ap.hour)
            reminder_time = ap_dt - target_offset
            if reminder_time <= now < (reminder_time + window):
                phone_digits = PhoneValidator.extract_digits(ap.client_phone)
                if not phone_digits or len(phone_digits) != 10:
                    continue
                date_str = ap.date.strftime("%d/%m/%Y")
                hour_str = ap.hour.strftime("%H:%M")
                text = (
                    f"Olá, {ap.client_name}! "
                    f"Seu horário com {ap.barber} é em 30 minutos "
                    f"(às {hour_str} de {date_str}). Não se esqueça!"
                )
                to_send.append((ap, phone_digits, text))

        for ap, number, text in to_send:
            processed += 1
            if dry_run:
                self.stdout.write(f"[dry-run] Lembrete para #{ap.id} -> {number}: {text}")
                continue
            with transaction.atomic():
                result = send_mensage(number, text)
                if result.get("ok"):
                    ap.reminder_sent = True
                    ap.save(update_fields=["reminder_sent"])
                    self.stdout.write(f"Enviado lembrete para #{ap.id} ({number})")
                else:
                    err = result.get("error")
                    details = result.get("details")
                    self.stdout.write(
                        self.style.WARNING(
                            f"Falha no envio para #{ap.id} ({number}): {err} {details or ''}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS(f"Processados: {processed}, enviados: {0 if options.get('dry_run') else len([1 for _ in to_send])}"))

