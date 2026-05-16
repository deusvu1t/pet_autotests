import random

from faker import Faker

fake = Faker()

COUNTRIES = [
    "Austria",
    "Belgium",
    "Croatia",
    "Germany",
]


def valid_registration_data():
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=75).strftime(
            "%Y-%m-%d"
        ),
        "country": random.choice(COUNTRIES),
        "postal_code": fake.postcode(),
        "house_number": fake.building_number(),
        "street": fake.street_name(),
        "city": fake.city(),
        "state": fake.state(),
        "phone": fake.msisdn()[:11],
        "email": fake.unique.email(),
        "password": fake.password(),
    }


def valid_contact_data():
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "subject": "Customer service",
        "message": fake.text(249),
    }


VALID_LOGIN_USER = {
    "email": "customer@practicesoftwaretesting.com",
    "password": "welcome01",
}
INVALID_LOGIN_USER = {"email": "invaliduser@test.com", "password": "test123"}
