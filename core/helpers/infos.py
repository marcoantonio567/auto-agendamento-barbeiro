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
    }
]

def obter_barbers_keys():
    """Retorna lista de chaves dos barbeiros disponíveis."""
    return [b['key'] for b in BARBERS]

def obter_barbers():
    """Retorna lista de barbeiros com foto dinâmica vinculada ao avatar quando disponível."""
    try:
        from users.models import User
    except Exception:
        return BARBERS
    result = []
    for b in BARBERS:
        photo = b.get('photo')
        try:
            u = User.objects.filter(username=b['key']).first()
            if u and getattr(u, 'avatar', None) and u.avatar:
                photo = u.avatar.url
        except Exception:
            pass
        result.append({'key': b['key'], 'name': b['name'], 'photo': photo})
    return result
