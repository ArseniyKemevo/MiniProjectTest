import database
import converter
import sys

def menu_add_rate():
    print("\n--- Добавление / Обновление курса ---")
    try:
        from_curr = input("Введите исходную валюту (например, USD): ")
        to_curr = input("Введите целевую валюту (например, RUB): ")
        rate_str = input("Введите курс обмена: ")
        
        from_curr = converter.validate_currency_code(from_curr)
        to_curr = converter.validate_currency_code(to_curr)
        rate = converter.validate_rate(rate_str)
        
        database.save_or_update_rate(from_curr, to_curr, rate)
        print(f"✓ Курс {from_curr} -> {to_curr} успешно сохранен со значением {rate}")
    except ValueError as e:
        print(f"🗴 Ошибка ввода: {e}")

def menu_convert():
    print("\n--- Конвертация валюты ---")
    try:
        from_curr = input("Из какой валюты переводим: ")
        to_curr = input("В какую валюту переводим: ")
        amount_str = input("Какую сумму переводим: ")
        
        result = converter.perform_conversion(from_curr, to_curr, amount_str)
        print(f"★ Результат: {amount_str} {from_curr.upper()} = {result} {to_curr.upper()}")
    except ValueError as e:
        print(f"🗴 Не удалось выполнить конвертацию: {e}")

def menu_show_history():
    print("\n--- История операций ---")
    history = database.get_all_history()
    if not history:
        print("История операций пока пуста.")
        return
        
    print(f"{'Дата и время':<20} | {'Обмен':<15} | {'Исходная сумма':<15} | {'Получено':<15} | {'Курс':<10}")
    print("-" * 85)
    for row in history:
        timestamp, from_c, to_c, amt_from, amt_to, rate = row
        pair = f"{from_c}->{to_c}"
        print(f"{timestamp:<20} | {pair:<15} | {amt_from:<15.2f} | {amt_to:<15.2f} | {rate:<10.4f}")

def main():
    database.init_db()
    
    while True:
        print("\n=== ВАЛЮТНЫЙ КОНВЕРТЕР ===")
        print("1. Добавить / обновить курс валюты")
        print("2. Конвертировать валюту")
        print("3. Просмотреть историю операций")
        print("0. Выход")
        
        choice = input("Выберите пункт меню: ").strip()
        
        if choice == "1":
            menu_add_rate()
        elif choice == "2":
            menu_convert()
        elif choice == "3":
            menu_show_history()
        elif choice == "0":
            print("Выход из программы. До свидания!")
            sys.exit(0)
        else:
            print("🗴 Некорректный пункт меню. Попробуйте снова.")

if __name__ == "__main__":
    main()