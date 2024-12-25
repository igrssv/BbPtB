import json
import os

def save_order_to_json(order_data, filename="orders.json"):
    # Проверяем, существует ли файл
    if os.path.exists(filename):
        # Читаем существующий файл
        with open(filename, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Добавляем новый ордер к данным
    data.append(order_data)

    # Сохраняем обновленные данные
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


# Подключение к API
def load_orders(filename="orders.json"):
    """Загружает ордера из JSON файла, если файл существует."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print("Ошибка: orders.json не содержит корректные данные.")
                return []
    return []

def save_orders(orders, filename="orders.json"):
    """Сохраняет обновленный список ордеров в JSON файл."""
    with open(filename, "w") as file:
        json.dump(orders, file, indent=4)

def check_order_status(session, filename="orders.json"):
    """Проверяет статус активных ордеров в orders.json и обновляет статус."""
    orders = load_orders(filename)
    if not orders:
        print("Ордеры отсутствуют в orders.json.")
        return
    
    # Проверяем каждый ордер
    for order in orders:
        if order.get("status") == "active":
            symbol = order["symbol"]
            order_id = order["order_id"]
            
            # Запрос статуса ордера
            try:
                response = session.get_order(symbol=symbol, orderId=order_id)
                if response.get("retMsg") == "OK":
                    order_status = response["result"].get("status")
                    
                    # Проверка: если ордер исполнен, обновляем статус
                    if order_status == "Filled":
                        print(f"Ордер {order_id} для {symbol} исполнен.")
                        order["status"] = "closed"  # Меняем статус на закрыт
                    else:
                        print(f"Ордер {order_id} для {symbol} все еще активен.")
                else:
                    print(f"Не удалось получить статус ордера {order_id}: {response.get('retMsg')}")
            
            except Exception as e:
                print(f"Ошибка при проверке статуса ордера {order_id} для {symbol}: {e}")
    
    # Сохраняем обновленный список ордеров
    save_orders(orders, filename)

# Пример использования
