from django.contrib import messages
from whastsapp_api import send_mensage
from core.helpers.phone_validation import PhoneValidator


def format_reschedule_message(appointment, new_hour):
    """Gera texto de WhatsApp para reagendamento.
    
    - inclui cliente, barbeiro, data e nova hora
    """
    date_str = appointment.date.strftime('%d/%m/%Y')
    hour_str = new_hour.strftime('%H:%M')
    return f"Olá, {appointment.client_name}! Seu horário com {appointment.barber} foi alterado para {date_str} às {hour_str}."


def format_cancel_message(appointment, reason):
    """Gera texto de WhatsApp para cancelamento.
    
    - inclui cliente, barbeiro, data e hora original
    - adiciona motivo quando informado
    """
    date_str = appointment.date.strftime('%d/%m/%Y')
    hour_str = appointment.hour.strftime('%H:%M')
    base_text = f"Olá, {appointment.client_name}! Seu horário com {appointment.barber} em {date_str} às {hour_str} foi cancelado pelo barbeiro."
    if reason:
        base_text += f" Motivo: {reason}."
    return base_text


def send_whatsapp_and_feedback(request, number, text):
    """Envia WhatsApp e adiciona mensagens de feedback no Django.
    
    - messages.success quando ok
    - messages.error com detalhes quando falha
    - retorna o resultado bruto da API
    """
    result = send_mensage(number, text)
    if result.get('ok'):
        messages.success(request, 'WhatsApp enviado ao cliente')
    else:
        err = result.get('error') or 'erro_desconhecido'
        details = result.get('details')
        if details:
            messages.error(request, f'Falha ao enviar WhatsApp: {err} ({details})')
        else:
            messages.error(request, f'Falha ao enviar WhatsApp: {err}')
    return result


def notify_client_change(request, appointment, message_text):
    """Valida telefone e envia mensagem via WhatsApp.
    
    - Valida se o telefone tem 10 dígitos.
    - Envia mensagem se válido.
    - Adiciona warning ao request se inválido.
    """
    phone_digits = PhoneValidator.extract_digits(appointment.client_phone)
    if phone_digits and len(phone_digits) == 10:
        send_whatsapp_and_feedback(request, phone_digits, message_text)
    else:
        messages.warning(request, 'Telefone do cliente inválido para envio de WhatsApp')
