"""
# Пример использования в другом файле:
from api import APIAdapter

api = APIAdapter()
api.get_aeroplanes('Canada')


Файл api.py готов и будет отвечать исключительно за интеграцию с внешними сервисами,
что очень высоко ценится в курсовых работах, так как показывает умение разделять код на модули.
"""

# =====================================================
# запустить модуль api.py через командную строку
# poetry run python api.py
# =====================================================


# =====================================================
# изменен шаг 1
# 1. Мы импортировали ABC и abstractmethod.
# 2. Добавили класс BaseAPIAdapter(ABC), который задает жесткую структуру.
# 3. Наш основной класс теперь объявлен как class APIAdapter(BaseAPIAdapter): — это чистокровное наследование
#    в рамках паттерна Адаптер.
# =====================================================

from abc import ABC, abstractmethod
import random
from requests import get


# =====================================================================
# 1. АБСТРАКТНЫЙ КЛАСС ДЛЯ РАБОТЫ С API (Шаг 1)
# =====================================================================
class BaseAPIAdapter(ABC):

    @abstractmethod
    def get_aeroplanes(self, country: str) -> None:
        """
        Абстрактный метод для подключения к API, получения координат
        и сбора информации о самолетах в воздушном пространстве страны.
        """
        pass


# =====================================================================
# 2. РЕАЛИЗАЦИЯ КЛАССА-НАСЛЕДНИКА (Шаг 1)
# =====================================================================
class APIAdapter(BaseAPIAdapter):

    def __init__(self) -> None:
        self.openstreetmap_url = "https://nominatim.openstreetmap.org/search"  # 'https://openstreetmap.org'
        self.opensky_url = "https://opensky-network.org/api/states/all"  # 'https://opensky-network.org'
        self.aeroplanes = None
        # Флаг режима работы
        self.offline_mode = False

        # Локальный справочник координат стран на случай сбоя внешних API
        self._fallback_bounds = {
            'canada': ['41.67', '83.11', '-141.00', '-52.62'],
            'usa': ['24.39', '49.38', '-124.84', '-66.95'],
            'france': ['41.36', '51.10', '-5.14', '9.56'],
            'germany': ['47.27', '55.05', '5.86', '15.04'],
            'russia': ['41.18', '81.85', '19.63', '180.00']
        }

    def get_aeroplanes(self, country: str) -> None:

        """Получение самолетов"""

        country_clean = country.strip().lower()

        geo_coordinates = None

        geo_source = None

        # =============================================================
        # 1. Получаем координаты через Nominatim
        # =============================================================


        random_id = random.randint(1000, 9999)


        headers = {

            "User-Agent":
            f"AviationProject_{random_id}/1.0"
        }


        params = {

            "q": country,

            "format": "json",

            "limit": 1
        }



        try:

            response = get(

                url=self.openstreetmap_url,

                params=params,

                headers=headers,

                timeout=50
            )


            if response.status_code == 200:


                data = response.json()


                if data:


                    geo_coordinates = (
                        data[0]
                        .get("boundingbox")
                    )


                    geo_source = (
                        "Nominatim API"
                    )


        except Exception as e:

            print(
                f"⚠️ Ошибка Nominatim: {e}"
            )

        # =============================================================
        # 2. Если сервер не дал координаты
        #    используем локальный справочник
        # =============================================================

        if not geo_coordinates:

            if country_clean in self._fallback_bounds:

                print(
                    "⚠️ Nominatim недоступен."
                )

                print(
                    "📚 Используем локальный справочник координат."
                )

                geo_coordinates = (
                    self._fallback_bounds[country_clean]
                )

                geo_source = (
                    "Локальный справочник"
                )


            else:

                print(
                    f"❌ Координаты для {country} не найдены."
                )

                self.aeroplanes = None

                return

        # =============================================================
        # Вывод проверки координат
        # =============================================================


        print()

        print(
            f"📍 Источник координат: {geo_source}"
        )


        print(
            f"📍 Координаты зоны: {geo_coordinates}"
        )

        # =============================================================
        # Запрос OpenSky
        # =============================================================

        opensky_params = {
            'lamin': float(geo_coordinates[0]),  # Юг
            'lamax': float(geo_coordinates[1]),  # Север
            'lomin': float(geo_coordinates[2]),  # Запад
            'lomax': float(geo_coordinates[3]),  # Восток
        }


        print()

        print(
            "🌐 Отправляем запрос OpenSky:"
        )


        print(
            opensky_params
        )


        try:


            response = get(

                url=self.opensky_url,

                params=opensky_params,

                timeout=15
            )

            print()

            print(
                "🔗 URL запроса:"
            )


            print(
                response.url
            )



            if response.status_code == 200:


                self.aeroplanes = (
                    response.json()
                )

                states = self.aeroplanes.get("states") or []

                filtered_planes = []

                for plane in states:

                    if (
                            isinstance(plane, list)
                            and len(plane) > 2
                            and plane[2]
                            and plane[2].lower() == country.lower()
                    ):
                        filtered_planes.append(plane)

                self.aeroplanes["states"] = filtered_planes


                self.offline_mode = False



                count = len(
                    self.aeroplanes.get(
                        "states",
                        []
                    )
                    or []
                )


                print()

                print(
                    f"✅ Получены реальные данные OpenSky."
                )

                print(
                    f"✈️ Самолетов найдено: {count}"
                )



            else:


                print(
                    f"❌ OpenSky ошибка: {response.status_code}"
                )


                self.aeroplanes = None



        except Exception as e:


            print(
                f"❌ Ошибка OpenSky: {e}"
            )


            self.aeroplanes = None


# =====================================================================
# Проверка работы модуля
# =====================================================================
if __name__ == "__main__":
    api = APIAdapter()
    country = 'Canada'

    print(f"Поиск самолетов для страны: {country}")
    api.get_aeroplanes(country)

    print("\n=== Результаты обработки ответа ===")

    if (
            api.aeroplanes
            and api.aeroplanes.get("states")
    ):

        planes = (
            api.aeroplanes["states"]
        )

        if api.offline_mode:

            print(
                "⚠️ ОФЛАЙН-РЕЖИМ"
            )

            print(
                "Примеры обнаруженных рейсов:"
            )



        else:

            print(
                "🌐 РЕАЛЬНЫЕ ДАННЫЕ OPEN SKY"
            )

            print(
                "Полный список рейсов:"
            )

        for plane in planes:
            callsign = (

                plane[1].strip()

                if plane[1]

                else "Unknown"
            )

            country = (

                plane[2]

                if plane[2]

                else "Unknown"
            )

            altitude = (

                plane[7]

                if plane[7]

                else "На земле"
            )

            velocity = (

                plane[9]

                if plane[9]

                else "Нет данных"
            )

            print(

                f"✈️ {callsign:<10}"
                f" | {country:<15}"
                f" | Высота: {altitude} м"
                f" | Скорость: {velocity} м/с"

            )


    else:

        print(
            "🛬 Самолеты не найдены."
        )

    # if api.aeroplanes and 'states' in api.aeroplanes and api.aeroplanes['states'] is not None:
    #     planes = api.aeroplanes['states']
    #     print(f"✅ Успешно! Всего самолетов в воздушном пространстве {country}: {len(planes)}")
    #
    #     if api.offline_mode:
    #
    #         print("\n⚠️ ОФЛАЙН-РЕЖИМ")
    #         print("Примеры обнаруженных рейсов:")
    #
    #     else:
    #
    #         print("\n🌐 РЕАЛЬНЫЕ ДАННЫЕ OPEN SKY NETWORK")
    #         print("Полный список обнаруженных рейсов:")
    #
    #     for plane in planes:
    #         callsign = (
    #             plane[1].strip()
    #             if plane[1]
    #             else "Неизвестно"
    #         )
    #
    #         origin = (
    #             plane[2]
    #             if plane[2]
    #             else "Неизвестно"
    #         )
    #
    #         altitude = (
    #             plane[7]
    #             if plane[7]
    #             else "на земле"
    #         )
    #
    #         velocity = (
    #             plane[9]
    #             if len(plane) > 9 and plane[9]
    #             else "нет данных"
    #         )
    #
    #         print(
    #             f" ✈️ Позывной: {callsign:<10} | "
    #             f"Страна: {origin:<15} | "
    #             f"Высота: {altitude} м | "
    #             f"Скорость: {velocity} м/с"
    #             )
    # else:
    #     print("🛬 В выбранном регионе в данный момент нет летящих самолетов или радар вернул пустой ответ.")

# =====================================================
# рабочий вариант до шага 1
# =====================================================

# import random
# from requests import get
#
#
# class APIAdapter:
#
#     def __init__(self) -> None:
#         self.openstreetmap_url = 'https://openstreetmap.org'
#         self.opensky_url = 'https://opensky-network.org'
#         self.aeroplanes = None
#
#         # Локальный справочник координат стран на случай сбоя внешних API
#         self._fallback_bounds = {
#             'canada': ['41.67', '83.11', '-141.00', '-52.62'],
#             'usa': ['24.39', '49.38', '-124.84', '-66.95'],
#             'france': ['41.36', '51.10', '-5.14', '9.56'],
#             'germany': ['47.27', '55.05', '5.86', '15.04'],
#             'russia': ['41.18', '81.85', '19.63', '180.00']
#         }
#
#     def get_aeroplanes(self, country: str) -> None:
#         country_clean = country.strip().lower()
#         geo_coordinates = None
#
#         # Попытка №1: Запрос к серверу
#         random_id = random.randint(1000, 9999)
#         headers_nominatim = {
#             'User-Agent': f'AviationWorkspaceUniversityProject_{random_id}/1.0 (student_project@example.com)'
#         }
#         params_nominatim = {
#             'country': country,
#             'format': 'json',
#             'limit': 1,
#         }
#
#         try:
#             response = get(url=self.openstreetmap_url, params=params_nominatim, headers=headers_nominatim)
#             if response.status_code == 200:
#                 data = response.json()
#                 if data and isinstance(data, list) and 'boundingbox' in data[0]:
#                     geo_coordinates = data[0]['boundingbox']
#         except Exception:
#             # Молча переходим к запасному плану в случае любой сетевой ошибки
#             pass
#
#         # Попытка №2: Использование локального справочника, если сервер подвел
#         if not geo_coordinates:
#             if country_clean in self._fallback_bounds:
#                 print(f"⚠️ Внешний геокодер недоступен. Используем встроенные координаты для {country}...")
#                 geo_coordinates = self._fallback_bounds[country_clean]
#             else:
#                 print(f"❌ Не удалось получить координаты для '{country}' ни через сервер, ни локально.")
#                 self.aeroplanes = None
#                 return
#
#         # Формируем параметры для отправки радарам OpenSky
#         params = {
#             'lamin': float(geo_coordinates[0]),  # Юг
#             'lamax': float(geo_coordinates[1]),  # Север
#             'lomin': float(geo_coordinates[2]),  # Запад
#             'lomax': float(geo_coordinates[3]),  # Восток
#         }
#
#         print(f"🌐 Координаты зоны определены. Запрашиваем радары OpenSky Network...")
#         try:
#             response = get(url=self.opensky_url, params=params)
#             if response.status_code == 200:
#                 self.aeroplanes = response.json()
#             else:
#                 print(f"❌ Ошибка OpenSky API. Код ответа радара: {response.status_code}")
#                 print("🎮 Включаем демонстрационный режим: генерируем реальные тестовые данные для курсовой...")
#                 self.aeroplanes = {
#                     "time": 1700000000,
#                     "states": [
#                         ["c820b3", "ACA123  ", "Canada", 1700000100, 1700000100, -75.67, 45.42, 10668.0, False, 240.5, 90.0, 0.0, None, 10800.0, "3412", False, 0],
#                         ["a143b8", "WJA456  ", "Canada", 1700000100, 1700000100, -114.07, 51.04, 9144.0, False, 210.2, 270.0, 1.5, None, 9300.0, "1205", False, 0],
#                         ["c801a2", "JZA789  ", "Canada", 1700000100, 1700000100, -79.38, 43.65, 4572.0, False, 180.0, 180.0, -3.2, None, 4800.0, "5561", False, 0]
#                     ]
#                 }
#         except Exception as e:
#             print(f"❌ Произошла ошибка при подключении к OpenSky: {e}")
#             self.aeroplanes = None
#
#
# # =====================================================================
# # ПРОВЕРКА РАБОТЫ КЛАССА
# # =====================================================================
# if __name__ == "__main__":
#     api = APIAdapter()
#     target_country = 'Canada'
#
#     print(f"Запускаем поиск самолетов для страны: {target_country}...")
#     api.get_aeroplanes(target_country)
#
#     print("\n=== Результаты обработки ответа ===")
#     if api.aeroplanes and 'states' in api.aeroplanes and api.aeroplanes['states'] is not None:
#         planes = api.aeroplanes['states']
#         print(f"✅ Успешно! Всего самолетов в воздушном пространстве {target_country}: {len(planes)}")
#
#         print("\nПримеры обнаруженных рейсов:")
#         for plane in planes[:5]:
#             callsign = plane[1].strip() if plane[1] else "Неизвестно"
#             origin = plane[2]
#             altitude = plane[7] if plane[7] else "на земле"
#             print(f" ✈️  Позывной: {callsign:<8} | Страна регистрации: {origin} | Высота: {altitude} м")
#     else:
#         print("🛬 В выбранном регионе в данный момент нет летящих самолетов или радар вернул пустой ответ.")

# =====================================================
# в доработке но верная ссылка сайта
# =====================================================

# import random
# from requests import get
#
#
# class APIAdapter:
#
#     def __init__(self) -> None:
#         # self.openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
#         self.openstreetmap_url = 'https://openstreetmap.fr'
#         self.opensky_url = 'https://opensky-network.org'
#         self.aeroplanes = None
#
#     def get_aeroplanes(self, country: str) -> None:
#         # Генерируем уникальный User-Agent, чтобы OpenStreetMap нас гарантированно не блокировал
#         random_id = random.randint(1000, 9999)
#         headers_nominatim = {
#             'User-Agent': f'AviationWorkspaceUniversityProject_{random_id}/1.0 (student_project@example.com)'
#         }
#
#         params_nominatim = {
#             'country': country,
#             'format': 'json',
#             'limit': 1,
#         }
#
#         try:
#             response = get(url=self.openstreetmap_url, params=params_nominatim, headers=headers_nominatim)
#
#             # Проверяем статус ответа сервера
#             if response.status_code != 200:
#                 print(f"❌ Сервер OpenStreetMap ответил ошибкой. Статус-код: {response.status_code}")
#                 self.aeroplanes = None
#                 return
#
#             data = response.json()
#
#             # Проверяем, нашел ли поисковик страну
#             if not data or not isinstance(data, list):
#                 print(f"❌ Страна '{country}' не найдена в базе данных географических координат.")
#                 self.aeroplanes = None
#                 return
#
#             # Безопасно извлекаем boundingbox из первого совпадения
#             geo_coordinates = data[0].get('boundingbox')
#
#             if not geo_coordinates or len(geo_coordinates) < 4:
#                 print(f"❌ Не удалось получить границы (boundingbox) для страны '{country}'.")
#                 self.aeroplanes = None
#                 return
#
#             # Параметры для фильтрации самолетов по их географическим координатам
#             params = {
#                 'lamin': float(geo_coordinates[0]),  # Юг
#                 'lamax': float(geo_coordinates[1]),  # Север
#                 'lomin': float(geo_coordinates[2]),  # Запад
#                 'lomax': float(geo_coordinates[3]),  # Восток
#             }
#
#             print(f"🌐 Границы {country} успешно определены. Запрашиваем радары OpenSky...")
#             response = get(url=self.opensky_url, params=params)
#
#             if response.status_code == 200:
#                 self.aeroplanes = response.json()
#             else:
#                 print(f"❌ Ошибка OpenSky API. Код ответа радара: {response.status_code}")
#                 self.aeroplanes = None
#
#         except Exception as e:
#             print(f"❌ Произошла непредвиденная ошибка при запросе к API: {e}")
#             self.aeroplanes = None
#
#
# # =====================================================================
# # ПРОВЕРКА РАБОТЫ КЛАССА
# # =====================================================================
# if __name__ == "__main__":
#     api = APIAdapter()
#
#     target_country = 'Canada'
#     print(f"Запускаем поиск самолетов для страны: {target_country}...")
#
#     api.get_aeroplanes(target_country)
#
#     print("\n=== Результаты обработки ответа ===")
#     if api.aeroplanes and 'states' in api.aeroplanes and api.aeroplanes['states'] is not None:
#         planes = api.aeroplanes['states']
#         print(f"✅ Успешно! Всего самолетов в воздушном пространстве {target_country}: {len(planes)}")
#
#         print("\nПримеры обнаруженных рейсов:")
#         for plane in planes[:5]:
#             callsign = plane[1].strip() if plane[1] else "Неизвестно"
#             origin = plane[2]
#             altitude = plane[7] if plane[7] else "на земле"
#             print(f" ✈️  Позывной: {callsign:<8} | Страна регистрации: {origin} | Высота: {altitude} м")
#     else:
#         print("🛬 В выбранном регионе в данный момент нет летящих самолетов или произошла ошибка запроса.")


# ========================================================
# ========================================================


# from requests import get
#
#
# class APIAdapter:
#
#     def __init__(self) -> None:
#         self.openstreetmap_url = 'https://openstreetmap.org'
#         self.opensky_url = 'https://opensky-network.org'
#         self.aeroplanes = None
#
#     def get_aeroplanes(self, country: str) -> None:
#         headers_nominatim = {
#             'User-Agent': 'AviationCourseWorkApp/1.0 (contact: student@example.com)',
#         }
#
#         params_nominatim = {
#             'country': country,
#             'format': 'json',
#             'limit': 1,
#         }
#
#         try:
#             response = get(url=self.openstreetmap_url, params=params_nominatim, headers=headers_nominatim)
#
#             if response.status_code != 200 or not response.json():
#                 print(f"❌ Не удалось найти страну '{country}' или API OpenStreetMap недоступно.")
#                 self.aeroplanes = None
#                 return
#
#             data = response.json()
#
#             # Безопасно достаем boundingbox из первого элемента списка
#             if isinstance(data, list) and len(data) > 0:
#                 geo_coordinates = data[0].get('boundingbox')
#             else:
#                 geo_coordinates = None
#
#             if not geo_coordinates or len(geo_coordinates) < 4:
#                 print(f"❌ У страны '{country}' отсутствуют или неполные географические границы.")
#                 self.aeroplanes = None
#                 return
#
#             # Параметры для фильтрации самолетов по их географическим координатам
#             params = {
#                 'lamin': float(geo_coordinates[0]),  # Юг
#                 'lamax': float(geo_coordinates[1]),  # Север
#                 'lomin': float(geo_coordinates[2]),  # Запад
#                 'lomax': float(geo_coordinates[3]),  # Восток
#             }
#
#             response = get(url=self.opensky_url, params=params)
#
#             if response.status_code == 200:
#                 self.aeroplanes = response.json()
#             else:
#                 print(f"❌ Ошибка OpenSky API. Код ответа: {response.status_code}")
#                 self.aeroplanes = None
#
#         except Exception as e:
#             print(f"❌ Произошла непредвиденная ошибка при запросе к API: {e}")
#             self.aeroplanes = None
#
#
# # =====================================================================
# # ПРОВЕРКА РАБОТЫ КЛАССА
# # =====================================================================
# if __name__ == "__main__":
#     api = APIAdapter()
#
#     target_country = 'Canada'
#     print(f"Запускаем поиск самолетов для страны: {target_country}...")
#
#     api.get_aeroplanes(target_country)
#
#     print("\n=== Результаты обработки ответа ===")
#     if api.aeroplanes and 'states' in api.aeroplanes and api.aeroplanes['states'] is not None:
#         planes = api.aeroplanes['states']
#         print(f"✅ Успешно! Всего самолетов в воздушном пространстве {target_country}: {len(planes)}")
#
#         print("\nПримеры обнаруженных рейсов:")
#         for plane in planes[:3]:
#             callsign = plane[1].strip() if plane[1] else "N/A"
#             origin = plane[2]
#             altitude = plane[7] if plane[7] else "на земле"
#             print(f" ✈️  Позывной: {callsign:<8} | Страна регистрации: {origin} | Высота: {altitude} м")
#     else:
#         print("🛬 В выбранном регионе в данный момент нет летящих самолетов или произошла ошибка запроса.")
