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
# cspell:ignore userid
"""
Test cases for Account Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Account, Address, DataValidationError, db
from tests.factories import AccountFactory, AddressFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        A C C O U N T   M O D E L   T E S T   C A S E S
######################################################################
class TestAccount(TestCase):
    """Account Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.query(Address).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_account(self):
        """It should Create an Account and assert that it exists"""
        fake_account = AccountFactory()
        # pylint: disable=unexpected-keyword-arg
        account = Account(
            name=fake_account.name,
            userid=fake_account.userid,
            email=fake_account.email,
            phone_number=fake_account.phone_number,
            date_joined=fake_account.date_joined,
        )
        self.assertIsNotNone(account)
        self.assertEqual(account.id, None)
        self.assertEqual(account.name, fake_account.name)
        self.assertEqual(account.userid, fake_account.userid)
        self.assertEqual(account.email, fake_account.email)
        self.assertEqual(account.phone_number, fake_account.phone_number)
        self.assertEqual(account.date_joined, fake_account.date_joined)

    def test_add_a_account(self):
        """It should Create an account and add it to the database"""
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = AccountFactory()
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(account.id)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)

    @patch("service.models.db.session.commit")
    def test_add_account_failed(self, exception_mock):
        """It should not create an Account on database error"""
        exception_mock.side_effect = Exception()
        account = AccountFactory()
        self.assertRaises(DataValidationError, account.create)

    def test_read_account(self):
        """It should Read an account"""
        account = AccountFactory()
        account.create()

        # Read it back
        found_account = Account.find(account.id)
        self.assertEqual(found_account.id, account.id)
        self.assertEqual(found_account.name, account.name)
        self.assertEqual(found_account.userid, account.userid)
        self.assertEqual(found_account.email, account.email)
        self.assertEqual(found_account.phone_number, account.phone_number)
        self.assertEqual(found_account.date_joined, account.date_joined)
        self.assertEqual(found_account.addresses, [])

    def test_update_account(self):
        """It should Update an account"""
        account = AccountFactory(email="advent@change.me")
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(account.id)
        self.assertEqual(account.email, "advent@change.me")

        # Fetch it back
        account = Account.find(account.id)
        account.email = "XYZZY@plugh.com"
        account.update()

        # Fetch it back again
        account = Account.find(account.id)
        self.assertEqual(account.email, "XYZZY@plugh.com")

    @patch("service.models.db.session.commit")
    def test_update_account_failed(self, exception_mock):
        """It should not update an Account on database error"""
        exception_mock.side_effect = Exception()
        account = AccountFactory()
        self.assertRaises(DataValidationError, account.update)

    def test_delete_an_account(self):
        """It should Delete an account from the database"""
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = AccountFactory()
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(account.id)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        account.delete()
        accounts = Account.all()
        self.assertEqual(len(accounts), 0)

    @patch("service.models.db.session.commit")
    def test_delete_account_failed(self, exception_mock):
        """It should not delete an Account on database error"""
        exception_mock.side_effect = Exception()
        account = AccountFactory()
        self.assertRaises(DataValidationError, account.delete)

    def test_list_all_accounts(self):
        """It should List all Accounts in the database"""
        accounts = Account.all()
        self.assertEqual(accounts, [])
        for account in AccountFactory.create_batch(5):
            account.create()
        # Assert that there are not 5 accounts in the database
        accounts = Account.all()
        self.assertEqual(len(accounts), 5)

    def test_find_by_name(self):
        """It should Find an Account by name"""
        account = AccountFactory()
        account.create()

        # Fetch it back by name
        same_account = Account.find_by_name(account.name)[0]
        self.assertEqual(same_account.id, account.id)
        self.assertEqual(same_account.name, account.name)

    def test_serialize_an_account(self):
        """It should Serialize an account"""
        account = AccountFactory()
        address = AddressFactory()
        account.addresses.append(address)
        serial_account = account.serialize()
        self.assertEqual(serial_account["id"], account.id)
        self.assertEqual(serial_account["name"], account.name)
        self.assertEqual(serial_account["userid"], account.userid)
        self.assertEqual(serial_account["email"], account.email)
        self.assertEqual(serial_account["phone_number"], account.phone_number)
        self.assertEqual(serial_account["date_joined"], str(account.date_joined))
        self.assertEqual(len(serial_account["addresses"]), 1)
        addresses = serial_account["addresses"]
        self.assertEqual(addresses[0]["id"], address.id)
        self.assertEqual(addresses[0]["account_id"], address.account_id)
        self.assertEqual(addresses[0]["name"], address.name)
        self.assertEqual(addresses[0]["street"], address.street)
        self.assertEqual(addresses[0]["city"], address.city)
        self.assertEqual(addresses[0]["state"], address.state)
        self.assertEqual(addresses[0]["postal_code"], address.postal_code)

    def test_deserialize_an_account(self):
        """It should Deserialize an account"""
        account = AccountFactory()
        account.addresses.append(AddressFactory())
        account.create()
        serial_account = account.serialize()
        new_account = Account()
        new_account.deserialize(serial_account)
        self.assertEqual(new_account.name, account.name)
        self.assertEqual(new_account.userid, account.userid)
        self.assertEqual(new_account.email, account.email)
        self.assertEqual(new_account.phone_number, account.phone_number)
        self.assertEqual(new_account.date_joined, account.date_joined)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an account with a KeyError"""
        account = Account()
        self.assertRaises(DataValidationError, account.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an account with a TypeError"""
        account = Account()
        self.assertRaises(DataValidationError, account.deserialize, [])

    def test_deserialize_address_key_error(self):
        """It should not Deserialize an address with a KeyError"""
        address = Address()
        self.assertRaises(DataValidationError, address.deserialize, {})

    def test_deserialize_address_type_error(self):
        """It should not Deserialize an address with a TypeError"""
        address = Address()
        self.assertRaises(DataValidationError, address.deserialize, [])
