import random

from locust import HttpUser, task, between


CATEGORIES = ["Іграшки", "Одяг", "Взуття", "Коляски", "Книги", "Меблі"]
CONDITIONS = ["new", "like_new", "good", "fair"]


class GuestUser(HttpUser):
    
    weight = 5
    wait_time = between(1, 3)

    @task(5)
    def browse_listings(self):
        """Найчастіша дія: відкрити список оголошень (головна сторінка)."""
        self.client.get("/api/listings/", name="/api/listings/ (список)")

    @task(3)
    def browse_listings_filtered(self):
        """Список із фільтром по категорії - складніший SQL-запит."""
        category = random.choice(CATEGORIES)
        self.client.get(
            f"/api/listings/?category={category}",
            name="/api/listings/ (з фільтром категорії)",
        )

    @task(4)
    def view_listing_detail(self):
        """Відкрити конкретне оголошення - типова дія після перегляду списку."""
        listing_id = random.randint(1, 50)
        with self.client.get(
            f"/api/listings/{listing_id}",
            name="/api/listings/{id} (деталі)",
            catch_response=True,
        ) as response:
            if response.status_code == 404:
                response.success()


class SellerUser(HttpUser):
    
    weight = 1
    wait_time = between(2, 5)

    def on_start(self):
        self.token = None
        email = f"loadtest_{random.randint(1, 10_000_000)}@example.com"
        password = "TestPassword123"

        register_response = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": "Навантажувальний Тест",
            },
            name="/api/auth/register",
        )

        if register_response.status_code != 201:
            return

        login_response = self.client.post(
            "/api/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="/api/auth/login",
        )

        if login_response.status_code == 200:
            self.token = login_response.json()["access_token"]

    @property
    def auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(3)
    def create_listing(self):
        if not self.token:
            return

        self.client.post(
            "/api/listings/",
            json={
                "title": f"Тестовий товар {random.randint(1, 100000)}",
                "description": "Опис товару для навантажувального тестування системи.",
                "price": round(random.uniform(50, 2000), 2),
                "condition": random.choice(CONDITIONS),
                "category": random.choice(CATEGORIES),
            },
            headers=self.auth_headers,
            name="/api/listings/ (створення)",
        )

    @task(1)
    def view_my_listings(self):
        if not self.token:
            return

        self.client.get(
            "/api/listings/my",
            headers=self.auth_headers,
            name="/api/listings/my",
        )

    @task(2)
    def get_my_profile(self):
        if not self.token:
            return

        self.client.get(
            "/api/auth/me",
            headers=self.auth_headers,
            name="/api/auth/me",
        )