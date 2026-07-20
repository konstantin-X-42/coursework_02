"""
Принцип подстановки Барбары Лисков
Liskov Substitution — если класс Parent является родительским классу Child,
то любые методы класса Parent могут заменяться методами класса Child без возникновения ошибок в программе.

Подход к реализации
Используйте аргументы конструктора, чтобы обеспечить гибкость наследования.
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
    def pay(self, order):  # блокируем изменение интерфейса
        pass


class DebitPaymentProcessor(PaymentProcessor):

    def __init__(self, securite_code):
        self.securite_code = securite_code

    def pay(self, order):
        """Оплата заказа дебетовой картой"""
        print("Обработка дебетового типа платежа")
        print(f"Проверка кода безопасности: {self.securite_code}")
        order.status = "paid"


class CreditPaymentProcessor(PaymentProcessor):

    def __init__(self, securite_code):
        self.securite_code = securite_code

    def pay(self, order):
        """Оплата заказа кредитной картой"""
        print("Обработка кредитного типа платежа")
        print(f"Проверка кода безопасности: {self.securite_code}")
        order.status = "paid"


class PaypalPaymentProcessor(PaymentProcessor):

    def __init__(self, user_email):
        self.user_email = user_email

    def pay(self, order):
        """Оплата заказа через систему Paypal"""
        print("Обработка типа платежа Paypal")
        print(f"Отправка платежа на почту: {self.user_email}")
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
    payment_processor = DebitPaymentProcessor("0372846")
    payment_processor.pay(order)

    # Оплачиваем заказ через Paypal
    print("\n- - оплата Paypal - -")
    paypal_paymentProcessor = PaypalPaymentProcessor("user@mail.com")
    paypal_paymentProcessor.pay(order)
