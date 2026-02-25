from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_youtube_only(value):
    """Проверяет, что ссылка ведёт только на youtube.com"""

    # Разбираем URL
    parsed_url = urlparse(value)

    # Проверяем, что это вообще HTTP/HTTPS ссылка
    if parsed_url.scheme not in ["http", "https"]:
        raise ValidationError("Разрешены только HTTP/HTTPS ссылки")

    # Проверяем домен
    if parsed_url.netloc not in ["youtube.com", "www.youtube.com"]:
        raise ValidationError("Разрешены только ссылки на youtube.com")
