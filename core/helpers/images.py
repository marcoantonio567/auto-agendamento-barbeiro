from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def process_avatar_image(user, image_file, crop_params):
    """
    Processa o upload de imagem de avatar: valida, recorta e salva.
    
    Args:
        user: Instância do usuário.
        image_file: Arquivo de imagem enviado no request.FILES.
        crop_params: Dicionário (request.POST) contendo 'crop_x', 'crop_y', 'crop_w', 'crop_h'.
        
    Returns:
        (bool, str): (Sucesso, Mensagem de erro ou sucesso)
    """
    if not image_file:
        return False, 'Nenhuma imagem enviada'

    try:
        ctype = getattr(image_file, 'content_type', '') or ''
        if ctype not in ('image/png', 'image/jpeg', 'image/jpg'):
            return False, 'Formato inválido. Envie PNG ou JPEG.'

        img = Image.open(image_file)
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')

        ow, oh = img.size
        if ow < 96 or oh < 96:
            return False, 'Imagem muito pequena. Mínimo 96×96 px.'

        try:
            x = float(crop_params.get('crop_x', '0') or '0')
            y = float(crop_params.get('crop_y', '0') or '0')
            w = float(crop_params.get('crop_w', '0') or '0')
            h = float(crop_params.get('crop_h', '0') or '0')
        except ValueError:
            x = y = w = h = 0

        if w <= 0 or h <= 0:
            side = min(ow, oh)
            x = (ow - side) / 2
            y = (oh - side) / 2
            w = h = side

        box = (max(0, int(x)), max(0, int(y)), min(ow, int(x + w)), min(oh, int(y + h)))
        cropped = img.crop(box)
        final = cropped.resize((96, 96), Image.Resampling.LANCZOS)

        buffer = BytesIO()
        final.save(buffer, format='PNG', optimize=True)
        buffer.seek(0)

        filename = f'avatar_user_{user.id}.png'
        user.avatar.save(filename, ContentFile(buffer.read()), save=True)
        
        return True, 'Foto de perfil atualizada'

    except Exception:
        return False, 'Falha ao processar a imagem. Tente outro arquivo.'
