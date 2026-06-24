import database

def validate_currency_code(code):
    """Проверяет корректность кода валюты."""
    if not code or not isinstance(code, str):
        raise ValueError("Код валюты не может быть пустым.")
    clean_code = code.strip().upper()
    if len(clean_code) != 3 or not clean_code.isalpha():
        raise ValueError("Код валюты должен состоять ровно из 3 латинских букв (например, USD).")
    return clean_code

def validate_amount(amount):
    """Проверяет корректность введенной суммы. Поддерживает запятые и пробелы."""
    if amount is None:
        raise ValueError("Сумма не может быть пустой.")
    clean_str = str(amount).replace(" ", "").replace(",", ".")
    try:
        val = float(clean_str)
    except (ValueError, TypeError):
        raise ValueError("Сумма должна быть числом.")
    if val <= 0:
        raise ValueError("Сумма должна быть строго больше нуля.")
    return val

def validate_rate(rate):
    """Проверяет корректность введенного курса. Поддерживает запятые и пробелы."""
    if rate is None:
        raise ValueError("Курс не может быть пустым.")
    clean_str = str(rate).replace(" ", "").replace(",", ".")
    try:
        val = float(clean_str)
    except (ValueError, TypeError):
        raise ValueError("Курс должен быть числом.")
    if val <= 0:
        raise ValueError("Курс должен быть строго больше нуля.")
    return val

def perform_conversion(from_curr, to_curr, amount_str, db_path="currency_converter.db"):
    """
    Выполняет конвертацию валюты, сохраняет результат в историю и возвращает округленную сумму.
    """
    from_curr = validate_currency_code(from_curr)
    to_curr = validate_currency_code(to_curr)
    amount = validate_amount(amount_str)
    
    if from_curr == to_curr:
        raise ValueError("Исходная и целевая валюты совпадают. Конвертация не требуется.")

    rate = database.get_rate(from_curr, to_curr, db_path)
    if not rate:
        raise ValueError(f"Курс обмена из {from_curr} в {to_curr} не найден в системе. Сначала добавьте его.")

    result_amount = round(amount * rate, 2)
    
    # Записываем операцию в историю
    database.add_history_record(from_curr, to_curr, amount, result_amount, rate, db_path)
    
    return result_amount