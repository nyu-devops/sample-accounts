######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Account Service API Service Test Suite
"""
import os
import logging
from unittest import TestCase
from wsgi import app
from tests.factories import AccountFactory, AddressFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            resp = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = resp.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the Home Page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_account_list(self):
        """It should Get a list of Accounts"""
        self._create_accounts(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_account_by_name(self):
        """It should Get an Account by Name"""
        accounts = self._create_accounts(3)
        resp = self.client.get(BASE_URL, query_string=f"name={accounts[1].name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], accounts[1].name)

    def test_get_account(self):
        """It should Read a single Account"""
        # get the id of an account
        account = self._create_accounts(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{account.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], account.name)

    def test_get_account_not_found(self):
        """It should not Read an Account that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        resp = self.client.post(
            BASE_URL, json=account.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = resp.get_json()
        self.assertEqual(new_account["name"], account.name, "Names does not match")
        self.assertEqual(
            new_account["addresses"], account.addresses, "Address does not match"
        )
        self.assertEqual(new_account["email"], account.email, "Email does not match")
        self.assertEqual(
            new_account["phone_number"], account.phone_number, "Phone does not match"
        )
        self.assertEqual(
            new_account["date_joined"],
            str(account.date_joined),
            "Date Joined does not match",
        )

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_account = resp.get_json()
        self.assertEqual(new_account["name"], account.name, "Names does not match")
        self.assertEqual(
            new_account["addresses"], account.addresses, "Address does not match"
        )
        self.assertEqual(new_account["email"], account.email, "Email does not match")
        self.assertEqual(
            new_account["phone_number"], account.phone_number, "Phone does not match"
        )
        self.assertEqual(
            new_account["date_joined"],
            str(account.date_joined),
            "Date Joined does not match",
        )

    def test_update_account(self):
        """It should Update an existing Account"""
        # create an Account to update
        test_account = AccountFactory()
        resp = self.client.post(BASE_URL, json=test_account.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_account = resp.get_json()
        new_account["name"] = "Happy-Happy Joy-Joy"
        new_account_id = new_account["id"]
        resp = self.client.put(f"{BASE_URL}/{new_account_id}", json=new_account)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_account = resp.get_json()
        self.assertEqual(updated_account["name"], "Happy-Happy Joy-Joy")

    def test_delete_account(self):
        """It should Delete an Account"""
        # get the id of an account
        account = self._create_accounts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{account.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        account = AccountFactory()
        resp = self.client.post(
            BASE_URL, json=account.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    ######################################################################
    #  A D D R E S S   T E S T   C A S E S
    ######################################################################

    def test_get_address_list(self):
        """It should Get a list of Addresses"""
        # add two addresses to account
        account = self._create_accounts(1)[0]
        address_list = AddressFactory.create_batch(2)

        # Create address 1
        resp = self.client.post(
            f"{BASE_URL}/{account.id}/addresses", json=address_list[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create address 2
        resp = self.client.post(
            f"{BASE_URL}/{account.id}/addresses", json=address_list[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{account.id}/addresses")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_add_address(self):
        """It should Add an address to an account"""
        account = self._create_accounts(1)[0]
        address = AddressFactory()
        resp = self.client.post(
            f"{BASE_URL}/{account.id}/addresses",
            json=address.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["account_id"], account.id)
        self.assertEqual(data["name"], address.name)
        self.assertEqual(data["street"], address.street)
        self.assertEqual(data["city"], address.city)
        self.assertEqual(data["state"], address.state)
        self.assertEqual(data["postal_code"], address.postal_code)

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_address = resp.get_json()
        self.assertEqual(new_address["name"], address.name, "Address name does not match")

    def test_get_address(self):
        """It should Get an address from an account"""
        # create a known address
        account = self._create_accounts(1)[0]
        address = AddressFactory()
        resp = self.client.post(
            f"{BASE_URL}/{account.id}/addresses",
            json=address.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        address_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{account.id}/addresses/{address_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["account_id"], account.id)
        self.assertEqual(data["name"], address.name)
        self.assertEqual(data["street"], address.street)
        self.assertEqual(data["city"], address.city)
        self.assertEqual(data["state"], address.state)
        self.assertEqual(data["postal_code"], address.postal_code)

    def test_update_address(self):
        """It should Update an address on an account"""
        # create a known address
        account = self._create_accounts(1)[0]
        address = AddressFactory()
        resp = self.client.post(
            f"{BASE_URL}/{account.id}/addresses",
            json=address.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        address_id = data["id"]
        data["name"] = "XXXX"

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{account.id}/addresses/{address_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{account.id}/addresses/{address_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], address_id)
        self.assertEqual(data["account_id"], account.id)
        self.assertEqual(data["name"], "XXXX")

    def test_delete_address(self):
        """It should Delete an Address"""
        account = self._create_accounts(1)[0]
        address = AddressFactory()
        resp = self.client.post(
            f"{BASE_URL}/{account.id}/addresses",
            json=address.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        address_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{account.id}/addresses/{address_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure address is not there
        resp = self.client.get(
            f"{BASE_URL}/{account.id}/addresses/{address_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
