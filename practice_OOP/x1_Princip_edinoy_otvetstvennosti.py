"""
Принцип единой ответственности
Single Responsibility — каждый класс должен иметь только одну зону ответственности.

Подход к реализации
Выделите зоны ответственности в отдельные классы.
"""


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
        return sum(
            quantities * prices
            for quantities, prices in zip(self.quantities, self.prices)
        )


class PaymentProcessor:
    """Проведение платежа"""

    def pay_debit(self, security_code):
        """Оплата заказа дебетовой картой"""
        print("Обработка дебетового типа платежа")
        print(f"Проверка кода безопасности: {security_code}")

    def pay_credit(self, security_code):
        """Оплата заказа кредитной картой"""
        print("Обработка кредитного типа платежа")
        print(f"Проверка кода безопасности: {security_code}")


if __name__ == "__main__":
    # Создаем заказ
    order = Order()

    # Добавляем товары в заказ
    order.add_item("Клавиатура", 1, 2500)
    order.add_item("SSD", 1, 7500)
    order.add_item("USB-кабель", 2, 250)

    # Печатаем стоимость заказа
    print("- - полная стоимость заказа - -")
    print(order.total_price())

    # Оплачиваем заказ дебетовой картой
    print("\n- - оплата дебетовой картой - -")
    payment_processor = PaymentProcessor()
    payment_processor.pay_debit("0372846")
