from dotenv import load_dotenv
from pybit.unified_trading import HTTP
import os
import order_handler
import strategy
import save_order
import time
import strategy_test
import order_handler_test

# Загружаем переменные окружения из key.env
load_dotenv('key.env')

# Настройка API-ключей для демо-счета
api_key = os.getenv('API_KEY')
api_secret = os.getenv('SECRET_KEY')

# Указываем торговую пару, сумму, тип операции
symbols = [ "BTCUSDT","ETHUSDT", "LTCUSDT", "XRPUSDT", "ADAUSDT"]
symbol="ETHUSDT"
amount=10000
side="Buy" # side Buy, Sell
interval = 1 # разрез по выборке свечей 1, 2, 3, 5 и тд
minutes = 60 #время

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
def execute_trade(symbol):
    
    support, resistance, sentiment = strategy.fetch_strategy(session=session, 
                                                             symbol=symbol,
                                                             interval=interval,
                                                             minutes=minutes)
    
    order_handler.execute_trade(session=session,
                                symbol=symbol, 
                                support=support,
                                resistance=resistance,
                                amount=amount,
                                sentiment=sentiment)

def strategy_try_test():
    print("Пара: " + symbol)
    strategy_test.fetch_strategy(session=session,
                                                             symbol=symbol,
                                                             interval=interval,
                                                             minutes=minutes)
# def main_loop():
#     # Начинаем цикл обработки торгов
#     while True:
#             execute_trade()
#     else:
#             # Если сигнала нет, пропускаем итерацию
#         print("Нет подходящего сигнала для сделки. Ждем следующую проверку...")
        
#         # Задержка перед следующим циклом, например, на 60 секунд
#     time.sleep(60)

def execute_trade_for_all_symbols():
    for symbol in symbols:
        print(f"Обработка символа: {symbol}")
        execute_trade(symbol=symbol)

def chek():
    response = session.get_order_history(category="linear", limit=10)
    print(response)

# order book analyse
def order_book():
    for symbol in symbols:
        print('===============================================')
        print(symbol)
        support, resistance, sentiment_none = strategy.fetch_strategy(session=session,
                                                                 symbol=symbol,
                                                                 interval=interval,
                                                                 minutes=minutes)
        sentiment = strategy_test.analyze_order_book(session=session, symbol=symbol)
        order_handler_test.execute_trade(session=session,
                                symbol=symbol,
                                support=support,
                                resistance=resistance,
                                amount=amount,
                                sentiment=sentiment)

if __name__ == "__main__":
    order_book()
  # execute_trade_for_all_symbols()
#    chek()