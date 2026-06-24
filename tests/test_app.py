import pytest
import database
import converter

@pytest.fixture
def test_db(tmp_path):
    """
    Фикстура для создания чистой базы данных в оперативной памяти (:memory:)
    перед каждым тестом. Гарантирует изоляцию тестов друг от друга.
    """
    db_file = tmp_path / "test_currency.db"
    
    database.init_db(str(db_file))
    
    return str(db_file)

def test_save_and_get_rate(test_db):
    """Проверка сохранения и успешного чтения курса валют."""
    database.save_or_update_rate("USD", "RUB", 90.5, test_db)
    rate = database.get_rate("USD", "RUB", test_db)
    assert rate == 90.5

def test_update_existing_rate(test_db):
    """Проверка обновления уже существующего курса (ON CONFLICT)."""
    database.save_or_update_rate("USD", "RUB", 90.5, test_db)
    database.save_or_update_rate("USD", "RUB", 92.0, test_db)
    rate = database.get_rate("USD", "RUB", test_db)
    assert rate == 92.0

def test_get_nonexistent_rate(test_db):
    """Проверка возврата None, если пара валют отсутствует в БД."""
    rate = database.get_rate("EUR", "JPY", test_db)
    assert rate is None

def test_add_and_get_history(test_db):
    """Проверка корректной записи операции обмена в историю и её чтения."""
    database.add_history_record("USD", "RUB", 100.0, 9050.0, 90.5, test_db)
    history = database.get_all_history(test_db)
    
    assert len(history) == 1
    assert history[0][1] == "USD"
    assert history[0][2] == "RUB"
    assert history[0][3] == 100.0
    assert history[0][4] == 9050.0
    assert history[0][5] == 90.5

def test_validate_currency_code_success():
    """Проверка обработки корректных кодов валют."""
    assert converter.validate_currency_code("usd") == "USD"
    assert converter.validate_currency_code("  rUb  ") == "RUB"

def test_validate_currency_code_exceptions():
    """Проверка генерации ошибок при неверном формате кода валюты."""
    with pytest.raises(ValueError, match="Код валюты должен состоять ровно из 3 латинских букв"):
        converter.validate_currency_code("US")
    with pytest.raises(ValueError, match="Код валюты должен состоять ровно из 3 латинских букв"):
        converter.validate_currency_code("123")
    with pytest.raises(ValueError, match="Код валюты не может быть пустым"):
        converter.validate_currency_code("")

def test_validate_amount_success():
    """Проверка обработки корректных сумм."""
    assert converter.validate_amount("100") == 100.0
    assert converter.validate_amount(50.5) == 50.5

def test_validate_amount_exceptions():
    """Проверка генерации ошибок при некорректной сумме."""
    with pytest.raises(ValueError, match="Сумма должна быть числом"):
        converter.validate_amount("сто")
    with pytest.raises(ValueError, match="Сумма должна быть строго больше нуля"):
        converter.validate_amount("-10")
    with pytest.raises(ValueError, match="Сумма должна быть строго больше нуля"):
        converter.validate_amount("0")


def test_perform_conversion_success(test_db):
    """Проверка успешного расчёта конвертации и автоматического логирования в историю."""
    database.save_or_update_rate("USD", "RUB", 90.0, test_db)
    
    result = converter.perform_conversion("USD", "RUB", "100", test_db)
    assert result == 9000.0
    
    history = database.get_all_history(test_db)
    assert len(history) == 1

def test_perform_conversion_same_currencies(test_db):
    """Проверка запрета конвертации валюты саму в себя."""
    with pytest.raises(ValueError, match="Исходная и целевая валюты совпадают"):
        converter.perform_conversion("USD", "USD", "100", test_db)

def test_perform_conversion_missing_rate(test_db):
    """Проверка поведения системы при отсутствии курса в БД."""
    with pytest.raises(ValueError, match="Курс обмена из USD в EUR не найден"):
        converter.perform_conversion("USD", "EUR", "100", test_db)