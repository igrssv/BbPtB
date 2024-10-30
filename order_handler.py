
def place_order(session, symbol, amount,side):
    # Long = "Bye" , Short "Sell"
    #qty и цена покупки
    amount_and_qty = get_amount(session=session,amount=amount,symbol=symbol)
    qty=round_qty(amount_and_qty[0])
    price=amount_and_qty[1]

    # Рассчитываем уровни тейк-профита и стоп-лосса
    take_profit_price, stop_loss_price = tp_and_sl(price=price, side=side)
    # if side == "Sell":
    #     take_profit_price = round(price * 0.99, 2)  # TP на -1% от цены покупки
    #     stop_loss_price = round(price * 1.004, 2)   # SL на +0.4% от цены покупки
    # else:  # side == "Buy"
    #     take_profit_price = round(price * 1.01, 2)   # TP на +1% от цены покупки
    #     stop_loss_price = round(price * 0.996, 2)    # SL на -0.4% от цены покупки

    
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
def round_qty(qty):
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

    # Если длина целой части больше 2 знаков, оставляем только целую часть
    if len(integer_part) > 2:
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
        else:
            print("Ошибка при получении цены:", response.get("retMsg"))
            return None
    except Exception as e:
        print("Ошибка при выполнении запроса:", e)
        return None

# тейк-профит и стоп-лосс
def tp_and_sl(price,side):
    if side == "Sell":
        take_profit_price = price * 0.99  # TP на -1% от цены покупки
        stop_loss_price = price * 1.004   # SL на +0.4% от цены покупки
    else:  # side == "Buy"
        take_profit_price = price * 1.01  # TP на +1% от цены покупки
        stop_loss_price = price * 0.996    # SL на -0.4% от цены покупки
    
    print("take_profit_price: ", take_profit_price)
    print("stop_loss_price: ", stop_loss_price)
    return (take_profit_price, stop_loss_price)