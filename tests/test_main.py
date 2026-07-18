from unittest.mock import patch

import main

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# запуск тестов в модуле main/py:
# poetry run pytest tests/test_main.py -v
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# запуск тестов в модуле test_main.py с покрытием в html
# poetry run pytest tests/test_main.py --cov=main --cov-report=html
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ====================================================================
# В ТЕСТАХ ПРОВЕРЯЕМ:
# запуск программы main();
# создание APIAdapter и JsonFileStorage;
# загрузку данных из API;
# преобразование данных API в объекты Aeroplane;
# сохранение самолетов в хранилище;
# пункт меню 1 — вывод всех самолетов;
# пункт меню 2 — вывод ТОП-N самолетов по высоте;
# пункт меню 3 — поиск самолетов по стране;
# пункт меню 4 — удаление самолета;
# пункт меню 5 — корректный выход из программы;
# обработку неверного пункта меню;
# обработку некорректного ввода числа для ТОП-N.
# ====================================================================


# ====================================================================
# Проверка функции main()
# ====================================================================

@patch("main.user_interaction")
def test_main_function(mock_user):
    """
    Проверяет запуск главной функции программы.
    """

    main.main()

    mock_user.assert_called_once()



# ====================================================================
# Проверка загрузки данных из API и сохранения
# ====================================================================

@patch("main.APIAdapter")
@patch("main.JsonFileStorage")
def test_user_interaction_loads_planes(
        mock_storage,
        mock_api,
        monkeypatch,
        fake_api_data
):
    """
    Проверяет:
    - получение данных API;
    - создание Aeroplane;
    - сохранение самолетов.
    """

    mock_api.return_value.aeroplanes = fake_api_data

    inputs = iter([
        "Canada",
        "5"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs)
    )

    main.user_interaction()


    assert (
        mock_storage.return_value
        .add_aeroplane
        .call_count
        == 2
    )



# ====================================================================
# Проверка меню 1
# Показать все самолеты
# ====================================================================

@patch("main.APIAdapter")
@patch("main.JsonFileStorage")
def test_menu_show_all_planes(
        mock_storage,
        mock_api,
        monkeypatch,
        fake_api_data,
        capsys
):
    """
    Проверяет вывод всех самолетов.
    """

    mock_api.return_value.aeroplanes = fake_api_data


    mock_storage.return_value.get_aeroplanes.return_value = [
        {
            "callsign": "AAA111",
            "origin_country": "Canada",
            "velocity": 250.5,
            "altitude": 10000
        }
    ]


    inputs = iter([
        "Canada",
        "1",
        "5"
    ])


    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs)
    )


    main.user_interaction()


    output = capsys.readouterr().out


    assert "AAA111" in output
    assert "10000" in output



# ====================================================================
# Проверка меню 2
# TOP-N по высоте
# ====================================================================

@patch("main.APIAdapter")
@patch("main.JsonFileStorage")
def test_menu_top_altitude(
        mock_storage,
        mock_api,
        monkeypatch,
        fake_api_data,
        capsys
):
    """
    Проверяет сортировку по высоте.
    """

    mock_api.return_value.aeroplanes = fake_api_data


    mock_storage.return_value.get_aeroplanes.return_value = [
        {
            "callsign": "HIGH",
            "origin_country": "Canada",
            "velocity": 300,
            "altitude": 12000
        },
        {
            "callsign": "LOW",
            "origin_country": "USA",
            "velocity": 150,
            "altitude": 3000
        }
    ]


    inputs = iter([
        "Canada",
        "2",
        "1",
        "5"
    ])


    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs)
    )


    main.user_interaction()


    output = capsys.readouterr().out


    assert "HIGH" in output
    assert "12000" in output



# ====================================================================
# Проверка ошибки TOP-N
# ====================================================================

@patch("main.APIAdapter")
@patch("main.JsonFileStorage")
def test_menu_top_invalid_number(
        mock_storage,
        mock_api,
        monkeypatch,
        capsys
):
    """
    Проверяет ввод неправильного числа TOP-N.
    """

    mock_api.return_value.aeroplanes = None


    mock_storage.return_value.get_aeroplanes.return_value = [
        {
            "callsign": "AAA111",
            "origin_country": "Canada",
            "velocity": 250,
            "altitude": 10000
        }
    ]


    inputs = iter([
        "Canada",
        "2",
        "abc",
        "5"
    ])


    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs)
    )


    main.user_interaction()


    output = capsys.readouterr().out


    assert "корректное целое число" in output



# ====================================================================
# Проверка меню 3
# Фильтр по стране
# ====================================================================

@patch("main.APIAdapter")
@patch("main.JsonFileStorage")
def test_menu_filter_country(
        mock_storage,
        mock_api,
        monkeypatch,
        fake_api_data,
        capsys
):
    """
    Проверяет поиск самолетов по стране.
    """

    mock_api.return_value.aeroplanes = fake_api_data


    mock_storage.return_value.get_aeroplanes.return_value = [
        {
            "callsign": "AAA111",
            "origin_country": "Canada",
            "velocity": 250,
            "altitude": 10000
        },
        {
            "callsign": "BBB222",
            "origin_country": "USA",
            "velocity": 150,
            "altitude": 5000
        }
    ]


    inputs = iter([
        "Canada",
        "3",
        "Canada",
        "5"
    ])


    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs)
    )


    main.user_interaction()


    output = capsys.readouterr().out


    assert "AAA111" in output
    assert "BBB222" not in output



# ====================================================================
# Проверка меню 4
# Удаление самолета
# ====================================================================

@patch("main.APIAdapter")
@patch("main.JsonFileStorage")
def test_menu_delete_plane(
        mock_storage,
        mock_api,
        monkeypatch,
        fake_api_data
):
    """
    Проверяет удаление самолета по позывному.
    """

    mock_api.return_value.aeroplanes = fake_api_data


    inputs = iter([
        "Canada",
        "4",
        "AAA111",
        "5"
    ])


    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs)
    )


    main.user_interaction()


    (
        mock_storage
        .return_value
        .delete_aeroplanes_by_callsign
        .assert_called_once_with("AAA111")
    )



# ====================================================================
# Проверка меню 5
# Выход из программы
# ====================================================================

@patch("main.APIAdapter")
@patch("main.JsonFileStorage")
def test_menu_exit(
        mock_storage,
        mock_api,
        monkeypatch,
        capsys
):
    """
    Проверяет корректный выход.
    """

    mock_api.return_value.aeroplanes = None


    inputs = iter([
        "Canada",
        "5"
    ])


    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs)
    )


    main.user_interaction()


    output = capsys.readouterr().out


    assert "Программа успешно завершена" in output



# ====================================================================
# Проверка неверного пункта меню
# ====================================================================

@patch("main.APIAdapter")
@patch("main.JsonFileStorage")
def test_invalid_menu_choice(
        mock_storage,
        mock_api,
        monkeypatch,
        capsys
):
    """
    Проверяет обработку неизвестного пункта меню.
    """

    mock_api.return_value.aeroplanes = None


    inputs = iter([
        "Canada",
        "9",
        "5"
    ])


    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs)
    )


    main.user_interaction()


    output = capsys.readouterr().out


    assert "Неверный пункт меню" in output

# =======================================================================
# =======================================================================

# from unittest.mock import patch
#
# import main

# # =====================================================================
# # Проверка загрузки данных из API и сохранения в хранилище
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_user_interaction_loads_planes(
#         mock_storage,
#         mock_api,
#         monkeypatch,
#         fake_api_data
# ):
#     """
#     Проверяет:
#     - получение данных от API;
#     - создание объектов Aeroplane;
#     - сохранение самолетов в хранилище.
#     """
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#     inputs = iter([
#         "Canada",  # страна
#         "5"        # выход
#     ])
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#     main.user_interaction()
#
#     # В API находятся 2 самолета
#     assert mock_storage.return_value.add_aeroplane.call_count == 2
#
#
#
# # =====================================================================
# # Проверка пункта меню 1
# # Показать все самолеты
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_show_all_planes(
#         mock_storage,
#         mock_api,
#         monkeypatch,
#         fake_api_data,
#         capsys
# ):
#     """
#     Проверяет вывод всех самолетов из базы.
#     """
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#     mock_storage.return_value.get_aeroplanes.return_value = [
#         {
#             "callsign": "AAA111",
#             "origin_country": "Canada",
#             "velocity": 250.5,
#             "altitude": 10000.0
#         }
#     ]
#
#     inputs = iter([
#         "Canada",
#         "1",
#         "5"
#     ])
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#     main.user_interaction()
#
#     output = capsys.readouterr().out
#
#     assert "AAA111" in output
#
#
#
# # =====================================================================
# # Проверка пункта меню 2
# # ТОП-N по высоте
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_top_altitude(
#         mock_storage,
#         mock_api,
#         monkeypatch,
#         fake_api_data,
#         capsys
# ):
#     """
#     Проверяет сортировку самолетов
#     и вывод самых высоких.
#     """
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#     mock_storage.return_value.get_aeroplanes.return_value = [
#         {
#             "callsign": "HIGH",
#             "origin_country": "Canada",
#             "velocity": 300,
#             "altitude": 12000
#         },
#         {
#             "callsign": "LOW",
#             "origin_country": "USA",
#             "velocity": 150,
#             "altitude": 3000
#         }
#     ]
#
#     inputs = iter([
#         "Canada",
#         "2",
#         "1",
#         "5"
#     ])
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#     main.user_interaction()
#
#     output = capsys.readouterr().out
#
#     assert "HIGH" in output
#     assert "12000" in output
#
#
#
# # =====================================================================
# # Проверка пункта меню 3
# # Фильтрация по стране
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_filter_country(
#         mock_storage,
#         mock_api,
#         monkeypatch,
#         fake_api_data,
#         capsys
# ):
#     """
#     Проверяет поиск самолетов
#     по стране регистрации.
#     """
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#     mock_storage.return_value.get_aeroplanes.return_value = [
#         {
#             "callsign": "AAA111",
#             "origin_country": "Canada",
#             "velocity": 250,
#             "altitude": 10000
#         }
#     ]
#
#     inputs = iter([
#         "Canada",
#         "3",
#         "Canada",
#         "5"
#     ])
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#     main.user_interaction()
#
#     output = capsys.readouterr().out
#
#     assert "AAA111" in output
#
#
#
# # =====================================================================
# # Проверка пункта меню 4
# # Удаление самолета
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_delete_plane(
#         mock_storage,
#         mock_api,
#         monkeypatch,
#         fake_api_data
# ):
#     """
#     Проверяет удаление самолета
#     по позывному.
#     """
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#     inputs = iter([
#         "Canada",
#         "4",
#         "AAA111",
#         "5"
#     ])
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#     main.user_interaction()
#
#     mock_storage.return_value.delete_aeroplanes_by_callsign.assert_called_once_with(
#         "AAA111"
#     )
#
#
#
# # =====================================================================
# # Проверка выхода из программы
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_exit(
#         mock_storage,
#         mock_api,
#         monkeypatch
# ):
#     """
#     Проверяет корректный выход из программы.
#     """
#
#     mock_api.return_value.aeroplanes = None
#
#     inputs = iter([
#         "Canada",
#         "5"
#     ])
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#     main.user_interaction()




# ======================================================================
# ранее до разбики фикстур в другой модуль
# ======================================================================

# import pytest
# from unittest.mock import patch
#
# import main
# from storage import JsonFileStorage
#
# # =====================================================================
# # Фикстура тестовых данных API
# # =====================================================================
#
# @pytest.fixture
# def fake_api_data():
#     return {
#         "states": [
#             [
#                 "id1",
#                 "AAA111",
#                 "Canada",
#                 0,
#                 0,
#                 0,
#                 0,
#                 10000.0,
#                 False,
#                 250.0
#             ],
#             [
#                 "id2",
#                 "BBB222",
#                 "USA",
#                 0,
#                 0,
#                 0,
#                 0,
#                 5000.0,
#                 False,
#                 150.0
#             ],
#             [
#                 "id3",
#                 "CCC333",
#                 "Canada",
#                 0,
#                 0,
#                 0,
#                 0,
#                 8000.0,
#                 False,
#                 200.0
#             ]
#         ]
#     }
#
#
# # =====================================================================
# # Проверка загрузки данных из API
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_user_interaction_loads_planes(
#         mock_storage,
#         mock_api,
#         monkeypatch,
#         fake_api_data
# ):
#     """
#     Проверяет:
#     - получение данных от API;
#     - создание Aeroplane;
#     - сохранение самолетов.
#     """
#
#     api_instance = mock_api.return_value
#     api_instance.aeroplanes = fake_api_data
#
#
#     storage_instance = mock_storage.return_value
#
#
#     inputs = iter([
#         "Canada",  # страна
#         "5"        # выход
#     ])
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#
#     main.user_interaction()
#
#
#     assert storage_instance.add_aeroplane.call_count == 3
#
#
#
# # =====================================================================
# # Пункт меню 1 - показать все самолеты
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_show_all_planes(
#         mock_storage,
#         mock_api,
#         monkeypatch,
#         fake_api_data,
#         capsys
# ):
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#
#     mock_storage.return_value.get_aeroplanes.return_value = [
#         {
#             "callsign": "AAA111",
#             "origin_country": "Canada",
#             "velocity": 250,
#             "altitude": 10000
#         }
#     ]
#
#
#     inputs = iter([
#         "Canada",
#         "1",
#         "5"
#     ])
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#
#     main.user_interaction()
#
#
#     output = capsys.readouterr().out
#
#
#     assert "AAA111" in output
#
#
#
# # =====================================================================
# # Пункт меню 2 - ТОП N по высоте
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_top_n_altitude(
#         mock_storage,
#         mock_api,
#         monkeypatch,
#         fake_api_data,
#         capsys
# ):
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#
#     mock_storage.return_value.get_aeroplanes.return_value = [
#         {
#             "callsign": "HIGH",
#             "origin_country": "Canada",
#             "velocity": 300,
#             "altitude": 12000
#         },
#         {
#             "callsign": "LOW",
#             "origin_country": "USA",
#             "velocity": 100,
#             "altitude": 3000
#         }
#     ]
#
#
#     inputs = iter([
#         "Canada",
#         "2",
#         "1",
#         "5"
#     ])
#
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#
#     main.user_interaction()
#
#
#     output = capsys.readouterr().out
#
#
#     assert "HIGH" in output
#
#
#
# # =====================================================================
# # Пункт меню 3 - поиск по стране
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_filter_country(
#         mock_storage,
#         mock_api,
#         monkeypatch,
#         fake_api_data,
#         capsys
# ):
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#
#     mock_storage.return_value.get_aeroplanes.return_value = [
#         {
#             "callsign": "AAA111",
#             "origin_country": "Canada",
#             "velocity": 250,
#             "altitude": 10000
#         }
#     ]
#
#
#     inputs = iter([
#         "Canada",
#         "3",
#         "Canada",
#         "5"
#     ])
#
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#
#     main.user_interaction()
#
#
#     output = capsys.readouterr().out
#
#
#     assert "AAA111" in output
#
#
#
# # =====================================================================
# # Пункт меню 4 - удаление
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_menu_delete_plane(
#         mock_storage,
#         mock_api,
#         monkeypatch,
#         fake_api_data
# ):
#
#     mock_api.return_value.aeroplanes = fake_api_data
#
#
#     inputs = iter([
#         "Canada",
#         "4",
#         "AAA111",
#         "5"
#     ])
#
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#
#     main.user_interaction()
#
#
#     mock_storage.return_value.delete_aeroplanes_by_callsign.assert_called_once_with(
#         "AAA111"
#     )
#
#
#
# # =====================================================================
# # Проверка выхода из программы
# # =====================================================================
#
# @patch("main.APIAdapter")
# @patch("main.JsonFileStorage")
# def test_exit_program(
#         mock_storage,
#         mock_api,
#         monkeypatch
# ):
#
#     mock_api.return_value.aeroplanes = None
#
#
#     inputs = iter([
#         "Canada",
#         "5"
#     ])
#
#
#     monkeypatch.setattr(
#         "builtins.input",
#         lambda _: next(inputs)
#     )
#
#
#     main.user_interaction()