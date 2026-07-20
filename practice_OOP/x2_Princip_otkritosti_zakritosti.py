"""
Принцип открытости/закрытости
Open/Closed — программные сущности (классы, модули, функции и т. п.) должны быть открыты для расширения,
но закрыты для изменения.

Подход к реализации
Используйте абстрактные классы. Они могут определить, какие подклассы требуются,
и усилить принцип единой ответственности, разделив обязанности кода.
"""

from abc import ABC, abstractmethod


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


class PaymentProcessor(ABC):  # абстрактный класс
    """Проведение платежа"""

    @abstractmethod
    def pay(self, order, securite_code):  # блокируем изменение интерфейса
        pass


class DebitPaymentProcessor(PaymentProcessor):

    def pay(self, order, security_code):
        """Оплата заказа дебетовой картой"""
        print("Обработка дебетового типа платежа")
        print(f"Проверка кода безопасности: {security_code}")
        order.status = "paid"


class CreditPaymentProcessor(PaymentProcessor):

    def pay(self, order, security_code):
        """Оплата заказа кредитной картой"""
        print("Обработка кредитного типа платежа")
        print(f"Проверка кода безопасности: {security_code}")
        order.status = "paid"


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
    payment_processor = DebitPaymentProcessor()
    payment_processor.pay(order, "0372846")
