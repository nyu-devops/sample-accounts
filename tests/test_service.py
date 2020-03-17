"""
<your resource name> API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from flask_api import status  # HTTP Status Codes
from tests.factories import AccountFactory, AddressFactory
from service.models import db
from service.service import app, init_db

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ <your resource name> Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """ Runs once before test suite """
        pass

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        """ Runs once after each test case """
        db.session.remove()
        db.drop_all()

######################################################################
#  H E L P E R   M E T H O D S
######################################################################

    def _create_accounts(self, count):
        """ Factory method to create accounts in bulk """
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            resp = self.app.post(
                "/accounts", json=account.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test Account"
            )
            new_account = resp.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

######################################################################
#  A C C O U N T   T E S T   C A S E S
######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_account_list(self):
        """ Get a list of Accounts """
        self._create_accounts(5)
        resp = self.app.get("/accounts")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_account_by_name(self):
        """ Get a Account by Name """
        accounts = self._create_accounts(3)
        resp = self.app.get("/accounts?name={}".format(accounts[1].name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], accounts[1].name)

    def test_get_account(self):
        """ Get a single Account """
        # get the id of an account
        account = self._create_accounts(1)[0]
        resp = self.app.get(
            "/accounts/{}".format(account.id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], account.name)

    def test_get_account_not_found(self):
        """ Get an Account that is not found """
        resp = self.app.get("/accounts/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_account(self):
        """ Create a new Account """
        account = AccountFactory()
        resp = self.app.post(
            "/accounts", 
            json=account.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        
        # Check the data is correct
        new_account = resp.get_json()
        self.assertEqual(new_account["name"], account.name, "Names does not match")
        self.assertEqual(new_account["addresses"], account.addresses, "Address does not match")
        self.assertEqual(new_account["email"], account.email, "Email does not match")
        self.assertEqual(new_account["phone_number"], account.phone_number, "Phone does not match")
        self.assertEqual(new_account["date_joined"], str(account.date_joined), "Date Joined does not match")

        # Check that the location header was correct by getting it
        resp = self.app.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_account = resp.get_json()
        self.assertEqual(new_account["name"], account.name, "Names does not match")
        self.assertEqual(new_account["addresses"], account.addresses, "Address does not match")
        self.assertEqual(new_account["email"], account.email, "Email does not match")
        self.assertEqual(new_account["phone_number"], account.phone_number, "Phone does not match")
        self.assertEqual(new_account["date_joined"], str(account.date_joined), "Date Joined does not match")

    def test_update_account(self):
        """ Update an existing Account """
        # create an Account to update
        test_account = AccountFactory()
        resp = self.app.post(
            "/accounts", 
            json=test_account.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_account = resp.get_json()
        new_account["name"] = "Happy-Happy Joy-Joy"
        resp = self.app.put(
            "/accounts/{}".format(new_account["id"]),
            json=new_account,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_account = resp.get_json()
        self.assertEqual(updated_account["name"], "Happy-Happy Joy-Joy")

    def test_delete_account(self):
        """ Delete an Account """
        # get the id of an account
        account = self._create_accounts(1)[0]
        resp = self.app.delete(
            "/accounts/{}".format(account.id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_bad_request(self):
        """ Send wrong media type """
        account = AccountFactory()
        resp = self.app.post(
            "/accounts", 
            json={"name": "not enough data"}, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """ Send wrong media type """
        account = AccountFactory()
        resp = self.app.post(
            "/accounts", 
            json=account.serialize(), 
            content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """ Make an illegal method call """
        resp = self.app.put(
            "/accounts", 
            json={"not": "today"}, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


######################################################################
#  A D D R E S S   T E S T   C A S E S
######################################################################

    def test_add_address(self):
        """ Add an address to an account """
        account = self._create_accounts(1)[0]
        address = AddressFactory()
        resp = self.app.post(
            "/accounts/{}/addresses".format(account.id), 
            json=address.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["account_id"], account.id)
        self.assertEqual(data["name"], address.name)
        self.assertEqual(data["street"], address.street)
        self.assertEqual(data["city"], address.city)
        self.assertEqual(data["state"], address.state)
        self.assertEqual(data["postalcode"], address.postalcode)

    def test_get_address(self):
        """ Get an address from an account """
        # create a known address
        account = self._create_accounts(1)[0]
        address = AddressFactory()
        resp = self.app.post(
            "/accounts/{}/addresses".format(account.id), 
            json=address.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        address_id = data["id"]

        # retrieve it back
        resp = self.app.get(
            "/accounts/{}/addresses/{}".format(account.id, address_id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["account_id"], account.id)
        self.assertEqual(data["name"], address.name)
        self.assertEqual(data["street"], address.street)
        self.assertEqual(data["city"], address.city)
        self.assertEqual(data["state"], address.state)
        self.assertEqual(data["postalcode"], address.postalcode)

    def test_update_address(self):
        """ Update an address on an account """
        # create a known address
        account = self._create_accounts(1)[0]
        address = AddressFactory()
        resp = self.app.post(
            "/accounts/{}/addresses".format(account.id), 
            json=address.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        address_id = data["id"]
        data["name"] = "XXXX"

        # send the update back
        resp = self.app.put(
            "/accounts/{}/addresses/{}".format(account.id, address_id), 
            json=data, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.app.get(
            "/accounts/{}/addresses/{}".format(account.id, address_id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], address_id)
        self.assertEqual(data["account_id"], account.id)
        self.assertEqual(data["name"], "XXXX")

    def test_delete_address(self):
        """ Delete an Address """
        account = self._create_accounts(1)[0]
        address = AddressFactory()
        resp = self.app.post(
            "/accounts/{}/addresses".format(account.id), 
            json=address.serialize(), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)
        address_id = data["id"]

        # send delete request
        resp = self.app.delete(
            "/accounts/{}/addresses/{}".format(account.id, address_id),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure address is not there
        resp = self.app.get(
            "/accounts/{}/addresses/{}".format(account.id, address_id), 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
