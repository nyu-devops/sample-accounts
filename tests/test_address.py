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
# pylint: disable=duplicate-code

"""
Test cases for Address Model
"""

import logging
import os
from unittest import TestCase
from wsgi import app
from service.models import Account, Address, db
from tests.factories import AccountFactory, AddressFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        A D D R E S S   M O D E L   T E S T   C A S E S
######################################################################
class TestAccount(TestCase):
    """Address Model Test Cases"""

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

    def test_add_account_address(self):
        """It should Create an account with an address and add it to the database"""
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = AccountFactory()
        address = AddressFactory(account=account)
        account.addresses.append(address)
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(account.id)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)

        new_account = Account.find(account.id)
        self.assertEqual(new_account.addresses[0].name, address.name)

        address2 = AddressFactory(account=account)
        account.addresses.append(address2)
        account.update()

        new_account = Account.find(account.id)
        self.assertEqual(len(new_account.addresses), 2)
        self.assertEqual(new_account.addresses[1].name, address2.name)

    def test_update_account_address(self):
        """It should Update an accounts address"""
        accounts = Account.all()
        self.assertEqual(accounts, [])

        account = AccountFactory()
        address = AddressFactory(account=account)
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(account.id)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)

        # Fetch it back
        account = Account.find(account.id)
        old_address = account.addresses[0]
        print("%r", old_address)
        self.assertEqual(old_address.city, address.city)
        # Change the city
        old_address.city = "XX"
        account.update()

        # Fetch it back again
        account = Account.find(account.id)
        address = account.addresses[0]
        self.assertEqual(address.city, "XX")

    def test_delete_account_address(self):
        """It should Delete an accounts address"""
        accounts = Account.all()
        self.assertEqual(accounts, [])

        account = AccountFactory()
        address = AddressFactory(account=account)
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(account.id)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)

        # Fetch it back
        account = Account.find(account.id)
        address = account.addresses[0]
        address.delete()
        account.update()

        # Fetch it back again
        account = Account.find(account.id)
        self.assertEqual(len(account.addresses), 0)

    def test_serialize_an_address(self):
        """It should serialize an Address"""
        address = AddressFactory()
        serial_address = address.serialize()
        self.assertEqual(serial_address["id"], address.id)
        self.assertEqual(serial_address["account_id"], address.account_id)
        self.assertEqual(serial_address["name"], address.name)
        self.assertEqual(serial_address["street"], address.street)
        self.assertEqual(serial_address["city"], address.city)
        self.assertEqual(serial_address["state"], address.state)
        self.assertEqual(serial_address["postal_code"], address.postal_code)

    def test_deserialize_an_address(self):
        """It should deserialize an Address"""
        address = AddressFactory()
        address.create()
        new_address = Address()
        new_address.deserialize(address.serialize())
        self.assertEqual(new_address.account_id, address.account_id)
        self.assertEqual(new_address.name, address.name)
        self.assertEqual(new_address.street, address.street)
        self.assertEqual(new_address.city, address.city)
        self.assertEqual(new_address.state, address.state)
        self.assertEqual(new_address.postal_code, address.postal_code)
