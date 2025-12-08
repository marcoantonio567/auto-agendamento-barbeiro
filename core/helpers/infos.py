SERVICES = [
    {
        'key': 'barba',
        'label': 'Fazer a barba',
        'price': 50,
        'icon': 'moustache',
        'description': 'Linhas precisas e acabamento quente para realçar o rosto.',
    },
    {
        'key': 'cabelo',
        'label': 'Cortar o cabelo',
        'price': 50,
        'icon': 'comb',
        'description': 'Corte clássico ou moderno com finalização profissional.',
    },
    {
        'key': 'combo',
        'label': 'Barba + cabelo',
        'price': 100,
        'icon': 'sparkles',
        'description': 'Pacote completo para sair renovado do totem.',
    },
]
BARBERS = [
    {
        'key': 'Japa',
        'name': 'Japa',
        'photo': '/static/agendamento/img/barbers/japa.svg',
    },
    {
        'key': 'João',
        'name': 'João',
        'photo': '/static/agendamento/img/barbers/joao.svg',
    },
    {
        'key': 'Marco',
        'name': 'Marco',
        'photo': '/static/agendamento/img/barbers/marco.svg',
    },
    {
        'key': 'Daniel',
        'name': 'Daniel',
        'photo': '/static/agendamento/img/barbers/daniel.svg',
    },
]

def obter_barbers_keys():
    return [b['key'] for b in BARBERS]
