STATUS_CHOICES = [
    ('ativo', 'Ativo'),
    ('cancelado', 'Cancelado'),
]

SERVICE_CHOICES = [
    ('barba', 'Fazer a barba'),
    ('cabelo', 'Cortar o cabelo'),
    ('combo', 'Barba + cabelo'),
]

BARBER_CHOICES = [
    ('Japa', 'Japa'),
]

PAYMENT_METHOD_CHOICES = [
    ('pix', 'Pix'),
    ('cash', 'Dinheiro'),
]

PAYMENT_CHOICES = [
    ('pendente', 'Pendente'),
    ('pago', 'Pago'),
    ('falhou', 'Falhou'),
]

CANCELLED_BY_CHOICES = [
    ('barber', 'Barbeiro'),
    ('client', 'Cliente'),
    ('system', 'Sistema'),
]
