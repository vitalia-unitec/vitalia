import os
import tempfile
from pathlib import Path

os.environ["DB_RUTA"] = str(Path(tempfile.mkdtemp()) / "vitalia_test.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()
