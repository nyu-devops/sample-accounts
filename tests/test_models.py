"""
Test cases for Account Model

"""
import logging
import unittest
import os
from service import app
from service.models import Account, DataValidationError, db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
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
#  P L A C E   T E S T   C A S E S   H E R E 
######################################################################

    def test_create_an_account(self):
        """ Create a Account and assert that it exists """
        account = Account(
            name="Jim Jones", 
            address="123 Main Street, Anytown USA", 
            email="jjames@gmail.com", 
            phone_number="(800) 555-1212"
        )
        self.assertTrue(account != None)
        self.assertEqual(account.id, None)
        self.assertEqual(account.name, "Jim Jones")
        self.assertEqual(account.address, "123 Main Street, Anytown USA")
        self.assertEqual(account.email, "jjames@gmail.com")
        self.assertEqual(account.phone_number, "(800) 555-1212")

    def test_add_a_account(self):
        """ Create an account and add it to the database """
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = Account(
            name="Jim Jones", 
            address="123 Main Street, Anytown USA", 
            email="jjames@gmail.com", 
            phone_number="(800) 555-1212"
        )
        self.assertTrue(account != None)
        self.assertEqual(account.id, None)
        account.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(account.id, 1)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)