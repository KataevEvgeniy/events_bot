import database


def get_star_balance(telegram_id: int) -> int:
    """Возвращает текущее количество звёзд у пользователя."""
    user = database.get_user(telegram_id)
    return user.count_stars

def add_stars(telegram_id: int, amount: int) -> int:
    """Начисляет указанное количество звёзд"""
    user = database.get_user(telegram_id)
    new_star_count = user.count_stars + amount
    database.update_user(
        user.telegram_id,
        user.is_admin,
        new_star_count,
        user.is_apocalypse_quiz_complete
    )
    return new_star_count

class InsufficientStarsError(Exception):
    """Исключение, если не хватает звёзд на балансе."""
    pass


def remove_stars(telegram_id: int, amount: int) -> int:
    """
    Списывает указанное количество звёзд у пользователя.
    Бросает исключение, если звёзд недостаточно.
    """
    user = database.get_user(telegram_id)

    if user.count_stars < amount:
        raise InsufficientStarsError(f"Недостаточно звёзд: нужно {amount}, есть {user.count_stars}")

    new_star_count = user.count_stars - amount
    database.update_user(
        user.telegram_id,
        user.is_admin,
        new_star_count,
        user.is_apocalypse_quiz_complete
    )
    return new_star_count