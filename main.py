# ================================ +
# установка утилит isort black flake8 mypy
# poetry add --group dev isort black flake8 mypy
# ================================ +
# Git-репозиторий для проекта
# git init
# ================================ -
# установка зависимости из файла pyproject.toml (для тестов)
# poetry install
# ================================
# запуск проверки
# poetry run isort .; poetry run black .; poetry run flake8; poetry run mypy
# ================================
# запуск всех тестов с покрытием
# poetry run pytest tests/ --cov=src --cov-report=html
# ================================

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
