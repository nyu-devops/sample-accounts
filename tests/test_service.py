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
        test_account = {
            "name": "Joe Jones",
            "address": "123 Main Street",
            "email": "jjones@gmail.com",
            "phone_number": "800-555-1212",
        }
        resp = self.app.post(
            "/accounts", 
            json=test_account, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        
        # Check the data is correct
        new_account = resp.get_json()
        self.assertEqual(new_account["name"], test_account["name"], "Names does not match")
        self.assertEqual(new_account["address"], test_account["address"], "Address does not match")
        self.assertEqual(new_account["email"], test_account["email"], "Email does not match")
        self.assertEqual(new_account["phone_number"], test_account["phone_number"], "Phone does not match")
        
        # TODO: When get_account is implemented uncomment below]
        # Check that the location header was correct
        # resp = self.app.get(location, content_type="application/json")
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # new_account = resp.get_json()
        # self.assertEqual(new_account["name"], test_account["name"], "Names does not match")
        # self.assertEqual(new_account["address"], test_account["address"], "Address does not match")
        # self.assertEqual(new_account["email"], test_account["email"], "Email does not match")
        # self.assertEqual(new_account["phone_number"], test_account["phone_number"], "Phone does not match")
