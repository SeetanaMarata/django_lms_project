from decimal import Decimal

import stripe
from django.conf import settings

# Инициализируем Stripe с секретным ключом
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description=None):
    """
    Создает продукт в Stripe.

    Args:
        name (str): Название продукта
        description (str): Описание продукта

    Returns:
        stripe.Product: Объект продукта Stripe
    """
    try:
        product = stripe.Product.create(
            name=name,
            description=description or f"Курс: {name}",
        )
        return product
    except stripe.error.StripeError as e:
        print(f"❌ Ошибка создания продукта в Stripe: {e}")
        raise


def create_stripe_price(product_id, amount, currency="rub"):
    """
    Создает цену для продукта в Stripe.

    Args:
        product_id (str): ID продукта Stripe
        amount (Decimal): Сумма в рублях
        currency (str): Валюта (по умолчанию RUB)

    Returns:
        stripe.Price: Объект цены Stripe
    """
    try:
        # Stripe требует сумму в копейках (центах)
        amount_in_cents = int(amount * 100)

        price = stripe.Price.create(
            product=product_id,
            unit_amount=amount_in_cents,
            currency=currency,
        )
        return price
    except stripe.error.StripeError as e:
        print(f"❌ Ошибка создания цены в Stripe: {e}")
        raise


def create_stripe_checkout_session(price_id, success_url, cancel_url, metadata=None):
    """
    Создает сессию оформления заказа в Stripe.

    Args:
        price_id (str): ID цены Stripe
        success_url (str): URL для перенаправления после успешной оплаты
        cancel_url (str): URL для перенаправления при отмене
        metadata (dict): Дополнительные метаданные

    Returns:
        stripe.checkout.Session: Объект сессии Stripe
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {},
        )
        return session
    except stripe.error.StripeError as e:
        print(f"❌ Ошибка создания сессии в Stripe: {e}")
        raise


def get_stripe_session_status(session_id):
    """
    Получает статус сессии оплаты.

    Args:
        session_id (str): ID сессии Stripe

    Returns:
        dict: Информация о статусе платежа
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            "id": session.id,
            "status": session.payment_status,
            "amount_total": session.amount_total,
            "currency": session.currency,
            "customer_email": (
                session.customer_details.get("email")
                if session.customer_details
                else None
            ),
            "paid": session.payment_status == "paid",
        }
    except stripe.error.StripeError as e:
        print(f"❌ Ошибка получения статуса сессии: {e}")
        raise
