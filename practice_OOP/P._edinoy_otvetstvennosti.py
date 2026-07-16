class Order:
    """Товар информация и стоимость"""
    def __init__(self):
        """Конструктор инициализирует пустые списки"""
        self.items = []
        self.quantities = []
        self.prices = []
        self.status = "open"

    def add_item(self, name, quantity, price):
        """Добавляем товар и информацию в пустые списки"""
        self.items.append(name)
        self.quantities.append(quantity)
        self.prices.append(price)

    def total_price(self):
        """Добавляем общую стоимость, что в заказе (перемножаем количество на цену)"""
        return sum(quantities * prices for quantities, prices in zip(self.quantities, self.prices))


class PaymentProcessor:
    """Проведение платежа"""
    def pay_debit(self, security_code):
        """Оплата заказа в дебетовой карте"""
        print("Обработка дебетового типа платежа")
        print(f"Проверка кода безопасности: {security_code}")

    def pay_credit(self, security_code):
        """Оплата заказа в кредитной карте"""
        print("Обработка дебетового типа платежа")
        print(f"Проверка кода безопасности: {security_code}")



if __name__ == '__main__':
    # Создаем заказ
    order = Order()

    # Добавляем товары в заказ
    order.add_item("Клавиатура", 1, 2500)
    order.add_item("SSD", 1, 7500)
    order.add_item("USB-кабель", 2, 250)

    # Печатаем стоимость заказа
    print(order.total_price())

    # Оплачиваем заказ
    payment_processor = PaymentProcessor()
    payment_processor.pay_debit("0372846")
