import os

import pytest


@pytest.fixture
def agents_root():
    current_path = os.path.abspath(os.path.dirname(__file__))
    root_path = os.path.split(current_path)[0]
    return os.path.join(root_path, "agents")
