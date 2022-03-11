"""
Test cases for Account Model

"""
import logging
import unittest
import os
from service import app
from service.models import Account, Address, DataValidationError, db
from tests.factories import AccountFactory, AddressFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  Account   M O D E L   T E S T   C A S E S
######################################################################
class TestAccount(unittest.TestCase):
    """ Test Cases for Account Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Account.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

######################################################################
#  H E L P E R   M E T H O D S
######################################################################

    def _create_account(self, addresses=[]):
        """ Creates an account from a Factory """
        fake_account = AccountFactory()
        account = Account(
            name=fake_account.name, 
            email=fake_account.email, 
            phone_number=fake_account.phone_number, 
            date_joined=fake_account.date_joined,
            addresses=addresses
        )
        self.assertTrue(account != None)
        self.assertEqual(account.id, None)
        return account

    def _create_address(self):
        """ Creates fake addresses from factory """
        fake_address = AddressFactory()
        address = Address(
            name=fake_address.name,
            street=fake_address.street,
            city=fake_address.city,
            state=fake_address.state,
            postalcode=fake_address.postalcode
        )
        self.assertTrue(address != None)
        self.assertEqual(address.id, None)
        return address

######################################################################
#  T E S T   C A S E S
######################################################################

    def test_create_an_account(self):
        """ Create a Account and assert that it exists """
        fake_account = AccountFactory()
        account = Account(
            name=fake_account.name, 
            email=fake_account.email, 
            phone_number=fake_account.phone_number, 
            date_joined=fake_account.date_joined 
        )
        self.assertTrue(account != None)
        self.assertEqual(account.id, None)
        self.assertEqual(account.name, fake_account.name)
        self.assertEqual(account.email, fake_account.email)
        self.assertEqual(account.phone_number, fake_account.phone_number)
        self.assertEqual(account.date_joined, fake_account.date_joined)

    def test_add_a_account(self):
        """ Create an account and add it to the database """
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = self._create_account()
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(account.id, 1)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)

    def test_read_account(self):
        """ Read an account """
        account = self._create_account()
        account.create()

        # Read it back
        found_account = Account.find(account.id)
        self.assertEqual(found_account.id, account.id)
        self.assertEqual(found_account.name, account.name)
        self.assertEqual(found_account.email, account.email)
        self.assertEqual(found_account.phone_number, account.phone_number)
        self.assertEqual(found_account.date_joined, account.date_joined)

    def test_update_account(self):
        """ Update an account """
        account = self._create_account()
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(account.id, 1)

        # Fetch it back
        account = Account.find(account.id)
        account.email = "XYZZY@plugh.com"
        account.update()

        # Fetch it back again
        account = Account.find(account.id)
        self.assertEqual(account.email, "XYZZY@plugh.com")


    def test_delete_an_account(self):
        """ Delete an account from the database """
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = self._create_account()
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(account.id, 1)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        account.delete()
        accounts = Account.all()
        self.assertEqual(len(accounts), 0)

    def test_list_all_accounts(self):
        """ List all Accounts in the database """
        accounts = Account.all()
        self.assertEqual(accounts, [])
        for _ in range(5):
            account = self._create_account()
            account.create()
        # Assert that there are not 5 accounts in the database
        accounts = Account.all()
        self.assertEqual(len(accounts), 5)

    def test_find_by_name(self):
        """ Find by name """
        account = self._create_account()
        account.create()

        # Fetch it back by name
        same_account = Account.find_by_name(account.name)[0]
        self.assertEqual(same_account.id, account.id)
        self.assertEqual(same_account.name, account.name)

    def test_serialize_an_account(self):
        """ Serialize an account """
        address = self._create_address()
        account = self._create_account(addresses=[address])
        serial_account = account.serialize()
        self.assertEqual(serial_account['id'], account.id)
        self.assertEqual(serial_account['name'], account.name)
        self.assertEqual(serial_account['email'], account.email)
        self.assertEqual(serial_account['phone_number'], account.phone_number)
        self.assertEqual(serial_account['date_joined'], str(account.date_joined))
        self.assertEqual(len(serial_account['addresses']), 1)
        addresses = serial_account['addresses']
        self.assertEqual(addresses[0]['id'], address.id)
        self.assertEqual(addresses[0]['account_id'], address.account_id)
        self.assertEqual(addresses[0]['name'], address.name)
        self.assertEqual(addresses[0]['street'], address.street)
        self.assertEqual(addresses[0]['city'], address.city)
        self.assertEqual(addresses[0]['state'], address.state)
        self.assertEqual(addresses[0]['postalcode'], address.postalcode)

    def test_deserialize_an_account(self):
        """ Deserialize an account """
        address = self._create_address()
        account = self._create_account(addresses=[address])
        serial_account = account.serialize()
        new_account = Account()
        new_account.deserialize(serial_account)
        self.assertEqual(new_account.id, account.id)
        self.assertEqual(new_account.name, account.name)
        self.assertEqual(new_account.email, account.email)
        self.assertEqual(new_account.phone_number, account.phone_number)
        self.assertEqual(new_account.date_joined, account.date_joined)

    def test_deserialize_with_key_error(self):
        """ Deserialize an account with a KeyError """
        account = Account()
        self.assertRaises(DataValidationError, account.deserialize, {})

    def test_deserialize_with_type_error(self):
        """ Deserialize an account with a TypeError """
        account = Account()
        self.assertRaises(DataValidationError, account.deserialize, [])

    def test_deserialize_address_key_error(self):
        """ Deserialize an address with a KeyError """
        address = Address()
        self.assertRaises(DataValidationError, address.deserialize, {})

    def test_deserialize_address_type_error(self):
        """ Deserialize an address with a TypeError """
        address = Address()
        self.assertRaises(DataValidationError, address.deserialize, [])

    def test_add_account_address(self):
        """ Create an account with an address and add it to the database """
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = self._create_account()
        address = self._create_address()
        account.addresses.append(address)
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(account.id, 1)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)

        new_account = Account.find(account.id)
        self.assertEqual(account.addresses[0].name, address.name)

        address2 = self._create_address()
        account.addresses.append(address2)
        account.update()

        new_account = Account.find(account.id)
        self.assertEqual(len(account.addresses), 2)
        self.assertEqual(account.addresses[1].name, address2.name)

    def test_update_account_address(self):
        """ Update an accounts address """
        accounts = Account.all()
        self.assertEqual(accounts, [])

        address = self._create_address()
        account = self._create_account(addresses=[address])
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(account.id, 1)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)

        # Fetch it back
        account = Account.find(account.id)
        old_address = account.addresses[0]
        self.assertEqual(old_address.city, address.city)

        old_address.city = "XX"
        account.update()

        # Fetch it back again
        account = Account.find(account.id)
        address = account.addresses[0]
        self.assertEqual(address.city, "XX")

    def test_delete_account_address(self):
        """ Delete an accounts address """
        accounts = Account.all()
        self.assertEqual(accounts, [])

        address = self._create_address()
        account = self._create_account(addresses=[address])
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(account.id, 1)
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

