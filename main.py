# ====================================================================
# ПРОЕКТ СОСТОИТ ИЗ 4 МОДУЛЕЙ:
# 1. api.py — реализует паттерн «Адаптер» и абстрактный класс для работы со сторонними сетевыми API
#    (Nominatim и OpenSky Network) с механизмом защиты от сетевых блокировок.
# 2. models.py — инкапсулирует данные о воздушном судне в объекты класса Aeroplane,
#    осуществляет валидацию типов и перегрузку операторов сравнения (<, >, ==) для анализа скорости и высоты полёта.
# 3. storage.py — реализует паттерн «Репозиторий» для персистентного хранения информации в формате
#    JSON внутри изолированной директории data/.
# 4. main.py — организует интерактивный CLI-интерфейс для конечного пользователя
#    (сортировка ТОП-N, фильтрация по стране, удаление).

# СТРУКТУРА ЭЛЕМЕНТОВ:
# 📁 data/ — папка с базой данных JSON.
# 📄 api.py — интеграция с внешними сервисами.
# 📄 models.py — объектные модели самолетов.
# 📄 storage.py — сохранение и фильтрация в файлах.
# 📄 main.py — запуск программы и меню пользователя.
# 📁 tests/ — пакет модулей автоматических тестов проекта.
# ====================================================================
"""
СТРУКТУРА ПРОЕКТА:
coursework_02/
├── main.py
├── models.py
├── storage.py
├── api.py
├── data/
│
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_storage.py
│   └── test_api.py
└── pyproject.toml
"""
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Запуск всех тестов проекта
# poetry run pytest
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# запуск всех тестов в проекте с покрытием html
# poetry run pytest --cov=. --cov-report=html
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ========================================================
# изменения шаг 4
# 1. Консольный интерактивный интерфейс: Меню бесконечно крутится в цикле while True,
#    пока пользователь явно не выберет пункт 5.
# 2. Запрос страны при старте: Автоматически подгружает и сохраняет свежие данные в data/flights_data.json.
# 3. ТОП N по высоте (Требование ТЗ): Пользователь сам вводит число N,
#    программа сортирует объекты самолётов и отдаёт самые высокие рейсы.
# 4. Фильтр по стране регистрации (Требование ТЗ): Программа ищет совпадения по полю origin_country.
# 5. Дополнительная фича: Возможность удаления самолёта по позывному прямо из меню.
# ========================================================


from api import APIAdapter
from models import Aeroplane
from storage import JsonFileStorage


def user_interaction():
    """Функция для взаимодействия с пользователем через консоль (Шаг 4)."""
    api = APIAdapter()
    storage = JsonFileStorage()

    print("====================================================")
    print("🛫  ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ МОНИТОРИНГА АВИАРЕЙСОВ 🛬")
    print("====================================================")

    # 1. Первый обязательный шаг: запрос данных по стране
    target_country = input("👉 Введите название страны на английском (например, Canada): ").strip()

    print(f"\n[Запрос] Поиск самолетов для страны: {target_country}...")
    api.get_aeroplanes(target_country)

    # Загружаем полученные данные в список объектов Aeroplane и сохраняем в файл
    aeroplanes_objects = []
    if api.aeroplanes and 'states' in api.aeroplanes and api.aeroplanes['states'] is not None:
        raw_planes = api.aeroplanes['states']
        # ОЧИЩАЕМ СТАРЫЕ ДАННЫЕ ПЕРЕД НОВОЙ ЗАГРУЗКОЙ
        storage.clear_storage()

        for p in raw_planes:
            plane_obj = Aeroplane(
                callsign=p[1],        # Индекс 1 — Позывной (например, "ACA123")
                origin_country=p[2],  # Индекс 2 — Страна регистрации ("Canada")
                velocity=p[9],        # Индекс 9 — Скорость
                altitude=p[7]         # Индекс 7 — Высота
            )
            storage.add_aeroplane(plane_obj)
            aeroplanes_objects.append(plane_obj)

        print(f"✅ Данные успешно обновлены. Загружено объектов: {len(aeroplanes_objects)}")
    else:
        print("🛬 В этой зоне сейчас нет активных самолетов. Работаем с ранее сохраненной базой.")

    # 2. Основной цикл интерактивного меню
    while True:
        print("\n" + "=" * 40)
        print("📱 ГЛАВНОЕ МЕНЮ ПРОГРАММЫ:")
        print("=" * 40)
        print("1. Показать все самолеты в зоне")
        print("2. Получить ТОП-N самолетов по высоте полета")
        print("3. Найти самолеты по конкретной стране регистрации")
        print("4. Удалить самолет из локальной базы по позывному")
        print("5. Выйти из программы")
        print("=" * 40)

        choice = input("👉 Выберите пункт меню (1-5): ").strip()

        # Перечитываем актуальные данные из JSON для точности
        current_data = storage.get_aeroplanes()
        planes_list = [
            Aeroplane(p["callsign"], p["origin_country"], p["velocity"], p["altitude"])
            for p in current_data
        ]

        if choice == "1":
            print(f"\n📊 Всего самолетов в базе: {len(planes_list)}")
            for idx, plane in enumerate(planes_list, 1):
                print(
                    f"{idx}. Позывной: {plane.callsign:<8} | Страна рег.: {plane.origin_country:<10} | Высота: {plane.altitude} м | Скорость: {plane.velocity} м/с")

        elif choice == "2":
            if not planes_list:
                print("❌ База данных пуста.")
                continue

            try:
                n = int(input(f"🔢 Сколько самолетов вывести в ТОП? (Доступно {len(planes_list)}): ").strip())
                if n <= 0:
                    print("❌ Число должно быть больше нуля.")
                    continue

                # Используем встроенный метод сортировки. Так как мы настроили методы __lt__ и __gt__ в Шаге 2,
                # Python может сортировать объекты. Отсортируем по высоте явно через lambda:
                sorted_by_alt = sorted(planes_list, key=lambda x: x.altitude, reverse=True)

                print(f"\n👑 ТОП-{min(n, len(sorted_by_alt))} САМОЛЕТОВ ПО ВЫСОТЕ ПОЛЕТА:")
                for idx, plane in enumerate(sorted_by_alt[:n], 1):
                    print(
                        f"🏆 {idx}. {plane.callsign:<8} -> Высота: {plane.altitude} м (Скорость: {plane.velocity} м/с)")
            except ValueError:
                print("❌ Пожалуйста, введите корректное целое число.")

        elif choice == "3":
            search_country = input(
                "🔍 Введите название страны регистрации для поиска (например, Canada): ").strip().lower()
            filtered = [p for p in planes_list if p.origin_country.lower() == search_country]

            if filtered:
                print(f"\n✈️ Найденные самолеты, зарегистрированные в {search_country.capitalize()}:")
                for plane in filtered:
                    print(
                        f"• Позывной: {plane.callsign:<8} | Высота: {plane.altitude} м | Скорость: {plane.velocity} м/с")
            else:
                print(f"ℹ️ Самолётов со страной регистрации '{search_country.capitalize()}' не найдено.")

        elif choice == "4":
            callsign_to_del = input("🗑️ Введите позывной самолета для удаления: ").strip()
            storage.delete_aeroplanes_by_callsign(callsign_to_del)

        elif choice == "5":
            print("\n👋 Программа успешно завершена. Спасибо за использование!")
            break
        else:
            print("❌ Неверный пункт меню. Попробуйте еще раз.")


def main():
    user_interaction()


if __name__ == "__main__":
    main()

# ========================================================
# изменения шаг 3
# 1. Полностью выполнены требования Шага 3: создан абстрактный класс BaseStorage и дочерний класс JsonFileStorage.
# 2. Реализовано сохранение объектов в физический файл flights_data.json на диске.
# 3. Реализован поиск по критериям (фильтрация по высоте/скорости) и удаление записей по позывному.
# ========================================================

# from api import APIAdapter
# from models import Aeroplane
# from storage import JsonFileStorage  # Импортируем наш новый JSON-коннектор
#
#
# def main():
#     print("=== Программа отслеживания самолетов (Шаг 3) ===")
#
#     api = APIAdapter()
#     storage = JsonFileStorage()  # Инициализируем хранилище (создаст flights_data.json)
#
#     target_country = input("Введите название страны на английском (например, Canada): ").strip()
#
#     print(f"\n[Запрос] Ищем самолеты для страны: {target_country}...")
#     api.get_aeroplanes(target_country)
#
#     if api.aeroplanes and 'states' in api.aeroplanes and api.aeroplanes['states'] is not None:
#         raw_planes = api.aeroplanes['states']
#
#         # 1. Парсинг в объекты и сохранение в файл
#         print("\n📥 Сохраняем полученные самолеты в JSON-файл...")
#         for p in raw_planes:
#             plane_obj = Aeroplane(
#                 callsign=p[1],
#                 origin_country=p[2],
#                 velocity=p[9],
#                 altitude=p[7]
#             )
#             storage.add_aeroplane(plane_obj)
#         print("✅ Данные успешно записаны в файл 'flights_data.json'.")
#
#         # 2. Чтение данных из файла с фильтрацией (Критерий: Высота > 5000м)
#         print("\n📋 Считываем из файла самолеты на высоте более 5000 метров:")
#         high_planes = storage.get_aeroplanes(min_altitude=5000.0)
#
#         for p in high_planes:
#             print(f" 🛫 Позывной: {p['callsign']:<8} | Скорость: {p['velocity']} м/с | Высота: {p['altitude']} м")
#
#         # 3. Демонстрация удаления информации из файла
#         print("\n🗑️ Тестирование удаления из файла...")
#         # Попробуем удалить один из демонстрационных самолетов
#         storage.delete_aeroplanes_by_callsign("WJA456")
#
#         # Проверяем файл после удаления
#         remaining_planes = storage.get_aeroplanes()
#         print(f"📊 Осталось самолетов в файле после удаления: {len(remaining_planes)}")
#
#     else:
#         print("🛬 В этой зоне сейчас нет самолетов или произошла ошибка запроса.")
#
#
# if __name__ == "__main__":
#     main()


# ========================================================
# изменения шаг 2
# 1. Создан модуль models.py, полностью закрывающий ТЗ Шага 2.
# 2. Программа теперь оперирует не абстрактными индексами, а понятными свойствами объектов
#    (plane.velocity, plane.altitude).
# 3. Реализована валидация (защита от значений None, когда самолет стоит на взлетной полосе).
# ========================================================

# from api import APIAdapter
# from models import Aeroplane  # Импортируем наш новый класс
#
#
# def main():
#     print("=== Программа отслеживания самолетов (Шаг 2) ===")
#
#     api = APIAdapter()
#     target_country = input("Введите название страны на английском (например, Canada): ").strip()
#
#     print(f"\n[Запрос] Ищем самолеты для страны: {target_country}...")
#     api.get_aeroplanes(target_country)
#
#     print("\n=== Результаты обработки через класс Aeroplane ===")
#     if api.aeroplanes and 'states' in api.aeroplanes and api.aeroplanes['states'] is not None:
#         raw_planes = api.aeroplanes['states']
#
#         # Превращаем сырые списки OpenSky в список объектов нашего нового класса Aeroplane
#         aeroplanes_objects = []
#         for p in raw_planes:
#             plane_obj = Aeroplane(
#                 callsign=p[1],  # Индекс 1 — Позывной
#                 origin_country=p[2],  # Индекс 2 — Страна регистрации
#                 velocity=p[9],  # Индекс 9 — Скорость полета (м/с)
#                 altitude=p[7]  # Индекс 7 — Высота полета (м)
#             )
#             aeroplanes_objects.append(plane_obj)
#
#         print(f"✅ Успешно преобразовано объектов: {len(aeroplanes_objects)}\n")
#
#         # Выводим информацию о созданных объектах
#         for plane in aeroplanes_objects:
#             print(f"✈️  Позывной: {plane.callsign:<8} | Скорость: {plane.velocity:<5} м/с | Высота: {plane.altitude} м")
#
#         # ДЕМОНСТРАЦИЯ СРАВНЕНИЯ САМОЛЕТОВ (если их больше одного)
#         if len(aeroplanes_objects) >= 2:
#             plane1 = aeroplanes_objects[0]
#             plane2 = aeroplanes_objects[1]
#
#             print("\n=== Тестирование методов сравнения ООП ===")
#             # Проверка сравнения по скорости через оператор >
#             if plane1 > plane2:
#                 print(
#                     f"🏎️  Самолет {plane1.callsign} летит БЫСТРЕЕ, чем {plane2.callsign} ({plane1.velocity} > {plane2.velocity} м/с)")
#             else:
#                 print(
#                     f"🏎️  Самолет {plane2.callsign} летит БЫСТРЕЕ, чем {plane1.callsign} ({plane2.velocity} > {plane1.velocity} м/с)")
#
#             # Проверка сравнения по высоте через наш метод is_higher_than
#             if plane1.is_higher_than(plane2):
#                 print(
#                     f"⛰️  Самолет {plane1.callsign} летит ВЫШЕ, чем {plane2.callsign} ({plane1.altitude} > {plane2.altitude} м)")
#             else:
#                 print(
#                     f"⛰️  Самолет {plane2.callsign} летит ВЫШЕ, чем {plane1.callsign} ({plane2.altitude} > {plane1.altitude} м)")
#     else:
#         print("🛬 В этой зоне сейчас нет самолетов или произошла ошибка запроса.")
#
#
# if __name__ == "__main__":
#     main()


# ========================================================
# рабочий вариант до шага 1
# ========================================================


# # Импортируем созданный вами класс из соседнего файла api.py
# from api import APIAdapter
#
#
# def main():
#     print("=== Программа отслеживания самолетов ===")
#
#     # Создаем инструмент для работы с API
#     api = APIAdapter()
#
#     # Запрашиваем у пользователя страну
#     target_country = input("Введите название страны на английском (например, Canada): ").strip()
#
#     print(f"\n[Запрос] Ищем самолеты для страны: {target_country}...")
#
#     # Запускаем метод из файла api.py
#     api.get_aeroplanes(target_country)
#
#     print("\n=== Результаты ===")
#     # Проверяем, удалось ли получить данные и записать их в self.aeroplanes
#     if api.aeroplanes and 'states' in api.aeroplanes and api.aeroplanes['states'] is not None:
#         planes = api.aeroplanes['states']
#         print(f"✅ Успешно! Всего самолетов в воздухе: {len(planes)}")
#
#         # Выводим первые 5 самолетов с точными индексами из ТЗ
#         print("\nСписок первых 5 самолетов:")
#         for plane in planes[:5]:
#             callsign = plane[1].strip() if plane[1] else "Неизвестно"
#             origin = plane[2]
#             altitude = plane[7] if plane[7] else "на земле"
#             print(f" ✈️  Позывной: {callsign:<8} | Страна регистрации: {origin} | Высота: {altitude} м")
#     else:
#         print("🛬 В этой зоне сейчас нет самолетов или произошла ошибка запроса.")
#
#
# if __name__ == "__main__":
#     main()


# ===============================================================================================
# в доработке
# ===============================================================================================


# import requests
#
# """
# 1.Вы запускаете файл main.py.
# 2.Вводите, например, Germany.
# 3.Код передает Germany в первую функцию. Та возвращает прямоугольник координат [lamin, lamax, lomin, lomax].
# 4.Эти координаты автоматически передаются во вторую функцию, которая подставляет их в запрос к OpenSky.
# 5.Вы получаете массив данных о самолетах и выводите их количество и информацию на экран.
# Вы можете скопировать этот код и проверить его работу.
# Скажите, получилось ли запустить, или вам нужно адаптировать этот код под уже существующий класс
# из вашего файла api.py? Если да — пришлите текст из вашего api.py.
# """
#
# # =====================================================================
# # 1. ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ КООРДИНАТ СТРАНЫ (Nominatim API)
# # =====================================================================
# def get_country_bounds(country_name):
#     """
#     Получает географические границы (boundingbox) для указанной страны.
#     """
#     url = "https://openstreetmap.org"
#     params = {
#         'country': country_name,
#         'format': 'json',
#         'limit': 1
#     }
#     # User-Agent обязателен по правилам Nominatim, чтобы запрос не заблокировали
#     headers = {'User-Agent': 'AviationTrackerCoursework/1.0'}
#
#     try:
#         response = requests.get(url, params=params, headers=headers)
#
#         if response.status_code == 200 and response.json():
#             data = response.json()
#             # Nominatim возвращает список: [south_lat, north_lat, west_lon, east_lon]
#             bbox = data[0]['boundingbox']
#
#             return {
#                 'lamin': float(bbox[0]),  # Юг (минимальная широта)
#                 'lamax': float(bbox[1]),  # Север (максимальная широта)
#                 'lomin': float(bbox[2]),  # Запад (минимальная долгота)
#                 'lomax': float(bbox[3])  # Восток (максимальная долгота)
#             }
#         else:
#             print("❌ Страна не найдена или API временно недоступно.")
#             return None
#     except Exception as e:
#         print(f"❌ Ошибка при запросе к Nominatim: {e}")
#         return None
#
#
# # =====================================================================
# # 2. ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ САМОЛЕТОВ В ЗОНЕ (OpenSky API)
# # =====================================================================
# def get_planes_in_zone(bounds):
#     """
#     Запрашивает список самолетов в прямоугольной зоне по координатам.
#     """
#     url = "https://opensky-network.org"
#     params = {
#         'lamin': bounds['lamin'],
#         'lamax': bounds['lamax'],
#         'lomin': bounds['lomin'],
#         'lomax': bounds['lomax']
#     }
#
#     try:
#         response = requests.get(url, params=params)
#
#         if response.status_code == 200:
#             data = response.json()
#             # Если самолетов в зоне нет, OpenSky вернет None вместо списка
#             states = data.get('states')
#             return states if states is not None else []
#         else:
#             print(f"❌ Ошибка OpenSky API. Код ответа: {response.status_code}")
#             return []
#     except Exception as e:
#         print(f"❌ Ошибка при запросе к OpenSky: {e}")
#         return []
#
#
# # =====================================================================
# # 3. ТОЧКА ВХОДА (Управляющая логика программы)
# # =====================================================================
# if __name__ == "__main__":
#     print("=== Программа отслеживания самолетов в воздушном пространстве ===")
#
#     # Запрашиваем у пользователя название страны (желательно на английском, например: France, Canada)
#     user_country = input("Введите название страны на английском языке: ").strip()
#
#     print(f"\n[1/2] Ищем координаты границ для страны: {user_country}...")
#     country_coordinates = get_country_bounds(user_country)
#
#     if country_coordinates:
#         print(f"✅ Координаты успешно получены:")
#         print(f"      Широта: от {country_coordinates['lamin']} до {country_coordinates['lamax']}")
#         print(f"      Долгота: от {country_coordinates['lomin']} до {country_coordinates['lomax']}")
#
#         print(f"\n[2/2] Запрашиваем данные о самолетах в этой зоне...")
#         planes_list = get_planes_in_zone(country_coordinates)
#
#         print(f"\n=== РЕЗУЛЬТАТЫ ===")
#         print(f"Найдено самолетов в воздушном пространстве: {len(planes_list)}")
#
#         # Если самолеты найдены, выведем первые 5 для примера
#         if planes_list:
#             print("\nПримеры летящих самолетов (первые 5):")
#             for plane in planes_list[:5]:
#                 # Индекс 1 — позывной (callsign), Индекс 2 — страна регистрации
#                 callsign = plane[1].strip() if plane[1] else "Неизвестно"
#                 origin_country = plane[2]
#                 altitude = plane[7] if plane[7] else "на земле"
#
#                 print(f"✈️ Позывной: {callsign:8} | Страна: {origin_country} | Высота: {altitude} м")
#     else:
#         print("❌ Не удалось продолжить выполнение программы без координат страны.")
#
#
# # ===============================================================================================
# # ===============================================================================================
#
#
# # Импортируем созданный вами класс из файла api.py
# from api import APIAdapter
#
#
# def main():
#     print("=== Программа отслеживания самолетов ===")
#
#     # Создаем экземпляр вашего класса
#     api = APIAdapter()
#
#     # Запрашиваем у пользователя страну
#     target_country = input("Введите название страны на английском (например, Canada): ").strip()
#
#     print(f"\n[Запрос] Запрашиваем данные для {target_country}...")
#
#     # Вызываем метод вашего класса
#     api.get_aeroplanes(target_country)
#
#     print("\n=== Результаты ===")
#     # Проверяем, записались ли данные в self.aeroplanes внутри api.py
#     if api.aeroplanes and 'states' in api.aeroplanes and api.aeroplanes['states'] is not None:
#         planes = api.aeroplanes['states']
#         print(f"✅ Успешно! Всего самолетов в воздухе: {len(planes)}")
#
#         # Выводим первые 5 самолетов
#         print("\nСписок первых 5 самолетов:")
#         for plane in planes[:5]:
#             callsign = plane[1].strip() if plane[1] else "N/A"
#             origin = plane[2]
#             altitude = plane[7] if plane[7] else "на земле"
#             print(f" ✈️  Позывной: {callsign:<8} | Страна регистрации: {origin} | Высота: {altitude} м")
#     else:
#         print("🛬 В этой зоне сейчас нет самолетов или произошла ошибка.")
#
#
# if __name__ == "__main__":
#     main()
#
