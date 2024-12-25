import pandas as pd
import time

# Извлекает исторические данные по заданной паре и интервалу
def fetch_historical_data(session, symbol, interval, minutes):
    end_time = int(time.time() * 1000)  # Текущее время в миллисекундах
    start_time = end_time - (minutes * 60 * 1000)  # Время на hours назад

    response = session.get_kline(
        category="inverse",
        symbol=symbol,
        interval=interval,
        start=start_time,
        end=end_time,
    )

    # Проверка ответа на успешность запроса
    if response['retCode'] != 0:
        print("Ошибка получения данных:", response['retMsg'])
        return None
    print(response)

    data = response['result']['list']  # Извлекаем нужные данные
    
    # Создаем DataFrame и задаем нужные колонки
    df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'quote_asset_volume'])
    # Преобразуем open_time в числовой тип и конвертируем в дату и время
    df['open_time'] = pd.to_datetime(df['open_time'].astype(int), unit='ms')
    
    # Преобразуем необходимые столбцы в числовой тип
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    
    return df[['open_time', 'close', 'high', 'low']]  # Возвращаем необходимые колонки

# Скользящая Средняя (MA)
def calculate_moving_average(data, period):
    print('START calculate_moving_average')
    return data['close'].rolling(window=period).mean()

# RSI 
def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# MACD
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    return pd.DataFrame({'macd': macd, 'signal_line': signal_line})

# настроение рынка
def fetch_market_sentiment(session,symbol):
    period = "5min" # Data recording period. 5min, 15min, 30min, 1h, 4h, 1d
    try:
        # Получаем соотношение длинных и коротких позиций
        ratio_data = session.get_long_short_ratio(category="inverse",period=period, symbol=symbol)
        # Извлекаем buyRatio и sellRatio из ответа
        buy_ratio = float(ratio_data['result']['list'][0]['buyRatio'])
        sell_ratio = float(ratio_data['result']['list'][0]['sellRatio'])

        # Определяем настроение рынка на основе соотношения
        if buy_ratio > sell_ratio:  # Если соотношение покупок больше продаж
            print("Бычье настроение - bullish")
            return "bullish"  # Бычье настроение
        elif buy_ratio < sell_ratio:  # Если продажи больше покупок
            print("Медвежье настроение - bearish")
            return "bearish"  # Медвежье настроение
        else:
            print("Нейтральное настроение - neutral")
            return "neutral"  # Нейтральное настроение

    except Exception as e:
        print(f"Ошибка при получении настроения рынка: {e}")
        return "neutral"  # Если произошла ошибка, возвращаем нейтральное настроение


#Уровни Поддержки и Сопротивления
def calculate_support_resistance(data):
    support = data['low'].min()
    resistance = data['high'].max()
    return support, resistance


def analyze_order_book(session, symbol):
    order_book = session.get_orderbook(
    category="linear",
    symbol=symbol,
    )
    asks = order_book['result']['a']  # Заявки на продажу
    bids = order_book['result']['b']  # Заявки на покупку

    # Самая низкая цена продажи и самая высокая цена покупки
    best_ask_price, best_ask_volume = float(asks[0][0]), float(asks[0][1])
    best_bid_price, best_bid_volume = float(bids[0][0]), float(bids[0][1])

    # Рыночный спред
    spread = best_ask_price - best_bid_price

    print(f"Лучший Ask: {best_ask_price} (объем: {best_ask_volume})")
    print(f"Лучший Bid: {best_bid_price} (объем: {best_bid_volume})")
    print(f"Рыночный спред: {spread}")

    # Оценка ликвидности
    total_ask_volume = sum(float(ask[1]) for ask in asks)
    total_bid_volume = sum(float(bid[1]) for bid in bids)

    print(f"Общий объем Ask: {total_ask_volume}")
    print(f"Общий объем Bid: {total_bid_volume}")

    # Настроение рынка
    if total_bid_volume > total_ask_volume:
        print("Настроение рынка: Бычье (покупатели преобладают)")
        sentiment = "bullish"
        return sentiment
    elif total_bid_volume < total_ask_volume:
        print("Настроение рынка: Медвежье (продавцы преобладают)")
        sentiment = "bearish"
        return  sentiment
    else:
        print("Настроение рынка: Нейтральное")
        sentiment = "none"
        return sentiment



def fetch_strategy(session, symbol, interval,minutes):
    symbol = symbol  
    interval = interval  # Интервал в минутах (1, 5, 15 и т.д.)

    # Получаем исторические данные
    data = fetch_historical_data(session, symbol, interval,minutes=minutes)

    # Рассчитываем индикаторы
    data['ma_5'] = calculate_moving_average(data, period=5)
    data['rsi'] = calculate_rsi(data)
    macd_df = calculate_macd(data)
    data = pd.concat([data, macd_df], axis=1)

    # Определяем уровни поддержки и сопротивления
    support, resistance = calculate_support_resistance(data)
    sentiment = fetch_market_sentiment(session=session, symbol=symbol)
    print("Поддержка:", support)
    print("Сопротивление:", resistance)
    return (support, resistance, sentiment)