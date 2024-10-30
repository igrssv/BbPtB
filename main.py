from dotenv import load_dotenv
from pybit.unified_trading import HTTP
import os
import order_handler

# Загружаем переменные окружения из key.env
load_dotenv('key.env')

# Настройка API-ключей для демо-счета
api_key = os.getenv('API_KEY')
api_secret = os.getenv('SECRET_KEY')


# Подключение к счету Bybit
session = HTTP(
    api_key=api_key,
    api_secret=api_secret,
    # Подключение к демо-счету Bybit
    demo=True,
)

# Функция для получения и отображения баланса
def get_balance():
    try:
        balance_info = session.get_wallet_balance(accountType="UNIFIED")
        
        # Извлечение значений из ответа
        total_wallet_balance = balance_info['result']['list'][0]['totalWalletBalance']
        total_available_balance = balance_info['result']['list'][0]['totalAvailableBalance']
        
        # Вывод информации о балансе
        print("Баланс кошелька:")
        print(f"Общий баланс: {total_wallet_balance}")
        print(f"Доступный баланс: {total_available_balance}")
        
    except Exception as e:
        print("Ошибка при получении баланса:", e)     

# Покупка 
def place_order():
    order_handler.place_order(session=session,symbol="ETHUSDT", amount=500, side="Sell") # side Buy, Sell
    
# Продажа

#test
def test():
    market_info = session.get_symbol_info(symbol="ETHUSDT")
    print(market_info)  

# Пример использования
if __name__ == "__main__":
    place_order()
    # test()
    # get_balance()

    

