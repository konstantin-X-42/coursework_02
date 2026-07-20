"""
Принцип инверсии зависимостей
Dependency Inversion — сделать классы зависимыми от абстрактных классов, а не от обычных классов.

Подход к реализации
Наследовать классы от абстрактных классов.
"""

"""
Принцип разделения интерфейсов
Interface Segregation — сделать интерфейсы (родительские абстрактные классы) более конкретными, а не общими.

Подход к реализации
При необходимости создайте дополнительные интерфейсы (классы).
"""

"""
Принцип подстановки Барбары Лисков
Liskov Substitution — если класс Parent является родительским классу Child,
то любые методы класса Parent могут заменяться методами класса Child без возникновения ошибок в программе.

Подход к реализации
Используйте аргументы конструктора, чтобы обеспечить гибкость наследования.
"""

from abc import ABC, abstractmethod


class Order:

    def __init__(self):
        self.items = []
        self.quantities = []
        self.prices = []
        self.status = "open"

    def add_item(self, name, quantity, price):
        self.items.append(name)
        self.quantities.append(quantity)
        self.prices.append(price)

    def total_price(self):
        return sum(
            quantities * prices
            for quantities, prices in zip(self.quantities, self.prices)
        )


class Authorizer(ABC):
    # Абстрактный клас авторизатор
    @abstractmethod
    # Абстрактный метод
    def is_authorized(
        self,
    ) -> bool:
        pass


class AuthorizerSMS(Authorizer):

    def __init__(self):
        # Конструктор авторизатор платежа
        self.authorized = False

    def verify_code(self, code):
        # Авторизация платежа через смс, расширение функциональности
        print(f"Верификация SMS кода {code}")
        self.authorized = True

    def is_authorized(self) -> bool:
        # Возвращаем авторизатор абстрактного метода от абстрактного класса родителя
        return self.authorized


class AuthorizerRobot(Authorizer):

    def __init__(self):
        # Конструктор авторизатор платежа
        self.authorized = False

    def not_a_robot(self):
        # Авторизация платежа через капча, расширение функциональности
        self.authorized = True

    def is_authorized(self) -> bool:
        # Возвращаем авторизатор абстрактного метода от абстрактного класса родителя
        return self.authorized


class PaymentProcessor(ABC):

    @abstractmethod
    def pay(self, order):
        pass


class DebitPaymentProcessor(PaymentProcessor):

    def __init__(self, authorizer: Authorizer):
        self.authorizer = authorizer

    def pay(self, order):
        if not self.authorizer.is_authorized():
            raise Exception("Не авторизован")
        print("Обработка дебетового типа платежа")
        order.status = "paid"


class CreditPaymentProcessor(PaymentProcessor):

    def __init__(self, security_code):
        self.security_code = security_code

    def pay(self, order):
        print("Обработка кредитного типа платежа")
        print(f"Проверка кода безопасности: {self.security_code}")
        order.status = "paid"


class PaypalPaymentProcessor(PaymentProcessor):

    def __init__(self, email_address, authorizer: Authorizer):
        self.email_address = email_address
        self.authorizer = authorizer

    def pay(self, order):
        if not self.authorizer.is_authorized():
            raise Exception("Не авторизован")
        print("Обработка типа платежа PayPal")
        print(f"Использование адреса электронной почты: {self.email_address}")
        order.status = "paid"


if __name__ == "__main__":
    # Создаем заказ
    order = Order()
    # Добавляем товары в заказ
    order.add_item("Клавиатура", 1, 2500)
    order.add_item("SSD", 1, 7500)
    order.add_item("USB-кабель", 2, 2500)

    # Печатаем стоимость заказа
    print("- - полная стоимость заказа - -")
    print(order.total_price())

    # Оплачиваем заказ дебетовой картой
    print("\n- - оплата дебетовой картой - -")
    authorizer = AuthorizerSMS()
    authorizer.verify_code("0372846")
    payment_processor = DebitPaymentProcessor(authorizer)
    # >>> Верификация SMS кода 0372846
    # >>> Обработка дебетового типа платежа
    payment_processor.pay(order)

    # Оплачиваем заказ через Paypal
    print("\n- - оплата Paypal - -")
    authorizer = AuthorizerRobot()
    authorizer.not_a_robot()
    paypal_payment_processor = PaypalPaymentProcessor("user@mail.com", authorizer)
    # >>> Обработка типа платежа PayPal
    # >>> Использование адреса электронной почты: user@mail.com
    paypal_payment_processor.pay(order)
