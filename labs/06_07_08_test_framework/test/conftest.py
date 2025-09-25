import os
import time
import requests
from models.api.user import UserAPI
from models.api.admin import AdminAPI

BACKEND_URL = os.getenv("BACKEND_URL", "http://app-backend:8000")


def wait_for_backend(url: str, retries: int = 10, delay: int = 1):
    """Wait until the backend responds or raise an error."""
    for _ in range(retries):
        try:
            requests.get(f"{url}/health")  # or "/" if no health endpoint
            return
        except requests.ConnectionError:
            time.sleep(delay)
    raise RuntimeError(f"Backend at {url} did not start in time")


def pytest_sessionstart(session):
    # Wait until backend is ready
    wait_for_backend(BACKEND_URL)

    # Initialize API clients
    user_api = UserAPI(BACKEND_URL)

    # Create users
    user_api.signup("admin", "1234")
    user_api.signup("testuser00", "1234")
    user_api.signup("testuser11", "1234")

    # Login as admin to create products
    user_api.login("admin", "1234")
    admin_api = AdminAPI(BACKEND_URL, token=user_api.token)
    admin_api.create_product("testproduct00")
    admin_api.create_product("testproduct11")

    # Assign products to testuser00
    user_api.login("testuser00", "1234")
    user_api.add_product_to_user("testproduct00")
    user_api.add_product_to_user("testproduct11")

    print("Test data setup via API completed!")
