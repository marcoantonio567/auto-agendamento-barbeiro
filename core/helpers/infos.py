SERVICES = [
    {
        'key': 'barba',
        'label': 'Fazer a barba',
        'price': 50,
        'icon': 'sparkles',
        'description': 'Linhas precisas e acabamento quente para realçar o rosto.',
    },
    {
        'key': 'cabelo',
        'label': 'Cortar o cabelo',
        'price': 50,
        'icon': 'scissors',
        'description': 'Corte clássico ou moderno com finalização profissional.',
    },
    {
        'key': 'combo',
        'label': 'Barba + cabelo',
        'price': 100,
        'icon': 'badge-check',
        'description': 'Pacote completo para sair renovado do totem.',
    },
]
BARBERS = [
    {
        'key': 'Japa',
        'name': 'Japa',
        'photo': '/static/scheduling/img/barbers/japa.svg',
    },
    {
        'key': 'João',
        'name': 'João',
        'photo': '/static/scheduling/img/barbers/joao.svg',
    },
    {
        'key': 'Marco',
        'name': 'Marco',
        'photo': '/static/scheduling/img/barbers/marco.svg',
    },
    {
        'key': 'Daniel',
        'name': 'Daniel',
        'photo': '/static/scheduling/img/barbers/daniel.svg',
    },
]

def obter_barbers_keys():
    """Retorna lista de chaves dos barbeiros disponíveis."""
    return [b['key'] for b in BARBERS]
