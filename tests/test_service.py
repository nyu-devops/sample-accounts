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
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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
