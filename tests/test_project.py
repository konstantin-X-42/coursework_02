import os
import shutil
import pytest
from models import Aeroplane
from storage import JsonFileStorage

# =====================================================
# запуск тестов в файле
# poetry run pytest test_project.py
# =====================================================

# =====================================================================
# 1. ТЕСТЫ ДЛЯ МОДЕЛИ САМОЛЕТА (КЛАСС Aeroplane)
# =====================================================================
def test_aeroplane_creation_and_validation():
    """Проверка корректного создания объекта и валидации данных."""
    plane = Aeroplane(callsign="  AFL123  ", origin_country="Russia", velocity=250.5, altitude=10000.0)
    assert plane.callsign == "AFL123"  # Проверка очистки пробелов
    assert plane.velocity == 250.5
    assert plane.altitude == 10000.0


def test_aeroplane_none_validation():
    """Проверка защиты от значений None (когда самолет на земле)."""
    plane = Aeroplane(callsign=None, origin_country=None, velocity=None, altitude=None)
    assert plane.callsign == "UNKNOWN"
    assert plane.origin_country == "Unknown"
    assert plane.velocity == 0.0
    assert plane.altitude == 0.0


def test_aeroplane_comparison():
    """Проверка работы магических методов сравнения по скорости и высоте."""
    plane1 = Aeroplane("AAA", "Canada", velocity=200.0, altitude=11000.0)
    plane2 = Aeroplane("BBB", "Canada", velocity=300.0, altitude=9000.0)

    # Сравнение по скорости (операторы <, >)
    assert plane2 > plane1
    assert plane1 < plane2

    # Сравнение по высоте через метод is_higher_than
    assert plane1.is_higher_than(plane2) is True


# =====================================================================
# 2. ТЕСТЫ ДЛЯ ХРАНИЛИЩА (КЛАСС JsonFileStorage)
# =====================================================================
@pytest.fixture
def temp_storage():
    """Фикстура для создания временной тестовой папки и файла."""
    test_dir = "data_test"
    test_file = f"{test_dir}/test_flights.json"

    # Создаем изолированное тестовое хранилище
    storage = JsonFileStorage(filename=test_file)
    yield storage

    # После окончания тестов удаляем тестовую папку, чтобы не засорять проект
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_storage_add_and_get(temp_storage):
    """Проверка добавления самолета в файл и чтения по критериям."""
    plane = Aeroplane("TEST100", "France", velocity=150.0, altitude=6000.0)
    temp_storage.add_aeroplane(plane)

    # Считываем обратно без фильтров
    all_planes = temp_storage.get_aeroplanes()
    assert len(all_planes) == 1
    assert all_planes[0]["callsign"] == "TEST100"


def test_storage_filtration(temp_storage):
    """Проверка фильтрации данных по высоте при чтении из файла."""
    plane_high = Aeroplane("HIGH", "USA", velocity=200.0, altitude=9000.0)
    plane_low = Aeroplane("LOW", "USA", velocity=100.0, altitude=2000.0)

    temp_storage.add_aeroplane(plane_high)
    temp_storage.add_aeroplane(plane_low)

    # Запрашиваем только те, что выше 5000м
    filtered = temp_storage.get_aeroplanes(min_altitude=5000.0)
    assert len(filtered) == 1
    assert filtered[0]["callsign"] == "HIGH"


def test_storage_delete(temp_storage):
    """Проверка удаления самолета из файла по позывному."""
    plane = Aeroplane("DEL777", "Germany", velocity=200.0, altitude=4000.0)
    temp_storage.add_aeroplane(plane)

    # Удаляем
    temp_storage.delete_aeroplanes_by_callsign("DEL777")

    # Проверяем, что файл пуст
    assert len(temp_storage.get_aeroplanes()) == 0
