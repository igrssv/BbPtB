import sys
import save_order

def execute_trade(session, symbol, support, resistance, amount, sentiment):
    amount_and_qty = get_amount(session=session,amount=amount,symbol=symbol)
    qty=round_qty(amount_and_qty[0],symbol=symbol)
    current_price=amount_and_qty[1]

    side, take_profit_price, stop_loss_price = signal_definition(support=support, resistance=resistance,current_price=current_price,sentiment=sentiment)
    if side and take_profit_price and stop_loss_price:
        place_order(
            session=session,
            symbol=symbol,
            side=side,
            qty=qty,
            price=current_price,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price, 
            support=support, 
            resistance=resistance, 
            sentiment=sentiment)
    else:
        print("Нет подходящего сигнала для сделки. Сделка не будет размещена.")


def signal_definition(support, resistance, current_price, sentiment):
    print('current_price:', current_price)
    print('support:', support)
    print('resistance:', resistance)
    print('sentiment:', sentiment)

    # Устанавливаем погрешность для покупки и продажи в 3%
    tolerance = 0.01

    # Вычисляем верхнюю границу для покупки и нижнюю границу для продажи
    buy_price_threshold = support * (1 + tolerance)
    sell_price_threshold = resistance * (1 - tolerance)

    print('buy_price_threshold:', buy_price_threshold)
    print('sell_price_threshold:', sell_price_threshold)

    if support <= current_price <= buy_price_threshold and sentiment == "bullish":
    # if sentiment == "bullish":

        # Если цена близка к поддержке в пределах допустимого диапазона и настроение бычье, открываем лонг
        side = "Buy"
        take_profit_price, stop_loss_price = tp_and_sl(price=current_price, side=side)
        return side, take_profit_price, stop_loss_price
    elif sell_price_threshold <= current_price <= resistance and sentiment == "bearish":
    # elif sentiment == "bearish":
        # Если цена близка к сопротивлению в пределах допустимого диапазона и настроение медвежье, открываем шорт
        side = "Sell"
        take_profit_price, stop_loss_price = tp_and_sl(price=current_price, side=side)
        return side, take_profit_price, stop_loss_price

    else:
        print("Нет подходящего сигнала для сделки.")
        return None, None, None  # Если сигнала нет, возвращаем None для всех значений



    
# покупка
def place_order(session, symbol, side, qty, price, take_profit_price, stop_loss_price, support, resistance, sentiment):

    #Размещает ордер на покупку или продажу.
    order = session.place_order (
    category="linear",
    symbol=symbol,
    side=side,
    orderType="Limit",
    qty=qty,
    price=price,
    isLeverage=0,
    orderFilter="Order",
    takeProfit= take_profit_price,
    stopLoss=stop_loss_price,
    )

    print(f"Размещен ордер {side} с TP: {take_profit_price}, SL: {stop_loss_price}")

    # сохранение ордера в БД
    if order.get("retMsg") == "OK":
        # Извлекаем информацию о размещенном ордере
        order_data = {
            "order_id": order.get("result", {}).get("orderId"),
            "symbol": symbol,
            "status": "active",
            "side": side,
            "qty": qty,
            "price": price,
            "support": support,
            "resistance": resistance,
            "sentiment": sentiment,
            "take_profit_price": take_profit_price,
            "stop_loss_price": stop_loss_price,
            "timestamp": order.get("time")
        }
        # Сохраняем ордер в JSON
        save_order.save_order_to_json(order_data)
        print("Информация об ордере сохранена.")
    else:
        print("Ошибка при размещении ордера:", order.get("retMsg"))

    response_order(order=order)

#Информация о размещенном ордере
def response_order(order):
    ret_msg = order.get("retMsg")
    order_id = order.get("result", {}).get("orderId")
    order_link_id = order.get("result", {}).get("orderLinkId")
    time = order.get("time")

    # Вывод значений для проверки
    print("retMsg:", ret_msg)
    print("orderId:", order_id)
    print("orderLinkId:", order_link_id)
    print("time:", time)


# Рассчет qty и цена покупки
def get_amount(session, amount, symbol):
    price = get_current_price(session=session, symbol=symbol)
    qty = amount / price
    print("qty:",qty)
    return qty, price

# Окргуление qty
def round_qty(qty, symbol):
    qty_str = str(qty)
    print("Исходное qty:", qty)

    # Проверяем, есть ли дробная часть
    if '.' in qty_str:
        integer_part, decimal_part = qty_str.split('.')
    else:
        integer_part = qty_str
        decimal_part = ''

    # Печатаем длину целой части и дробной части
    print(f"Длина целой части: {len(integer_part)}")
    print(f"Дробная часть: {decimal_part}")
    

    if symbol == "BTCUSDT":
        rounded_qty = round(qty, 3)  # Оставляем только целую часть
        print("BTCUSDT. Оставлено только целое число:", rounded_qty)
    elif symbol == "ETHUSDT":
        rounded_qty = round(qty, 2)  # Оставляем только целую часть
        print("ETHUSDT. Оставлено только целое число:", rounded_qty)
    else:
        # Если длина целой части больше 1 знаков, оставляем только целую часть
        if len(integer_part) >= 1:
            rounded_qty = int(qty)  # Оставляем только целую часть
            print("Оставлено только целое число:", rounded_qty)
        else:
            # Проверяем, начинаются ли первые три знака дробной части с "00"
            if decimal_part.startswith("00"):
                rounded_qty = round(qty, 3)  # Округляем до 4 знаков после запятой
                print("Округлено до 4 знаков:", rounded_qty)
            else:
                rounded_qty = round(qty, 2)  # Округляем до 2 знаков после запятой
                print("Округлено до 2 знаков:", rounded_qty)

    return rounded_qty




#Текущая цена актива
def get_current_price(session, symbol):
    try:
        response = session.get_tickers(
            category="spot",  # Выбор категории (например, "inverse", "spot")
            symbol=symbol
        )
        # Проверка успешного запроса
        if response.get("retCode") == 0:
            last_price = response['result']['list'][0]['lastPrice']
            print("Последняя цена актива", symbol, ":", last_price)
            return float(last_price)
        #Рассмотреть возможность брать при покупке по самой низкой или высокой цене на основе bye или sell и списка ордеров
        else:
            print("Ошибка при получении цены:", response.get("retMsg"))
            return None
    except Exception as e:
        print("Ошибка при выполнении запроса:", e)
        return None

# тейк-профит и стоп-лосс
def tp_and_sl(price,side):
    if side == "Sell":
        take_profit_price = price * 0.25  # TP на -1% от цены покупки
        stop_loss_price = price * 1.009   # SL на +0.4% от цены покупки
    else:  # side == "Buy"
        take_profit_price = price * 1.025  # TP на +1% от цены покупки
        stop_loss_price = price * 0.98    # SL на -0.4% от цены покупки
    
    print("take_profit_price: ", take_profit_price)
    print("stop_loss_price: ", stop_loss_price)
    return (take_profit_price, stop_loss_price)