import os
import shutil
import pytest

from storage import JsonFileStorage


@pytest.fixture
def temp_storage():
    test_dir = "data_test"
    test_file = f"{test_dir}/test_flights.json"

    storage = JsonFileStorage(filename=test_file)

    yield storage

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
