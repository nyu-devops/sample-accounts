"""
Models for Account

All of the models are stored in this module
"""
import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""

    pass


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

    def create(self):
        """
        Creates a Account to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Account to the database
        """
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """Removes a Account from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


######################################################################
#  A D D R E S S   M O D E L
######################################################################
class Address(db.Model, PersistentBase):
    """
    Class that represents an Address
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    name = db.Column(db.String(64))  # e.g., work, home, vacation, etc.
    street = db.Column(db.String(64))
    city = db.Column(db.String(64))
    state = db.Column(db.String(2))
    postalcode = db.Column(db.String(16))

    def __repr__(self):
        return "<Address %r id=[%s] account[%s]>" % (
            self.name,
            self.id,
            self.account_id,
        )

    def __str__(self):
        return "%s: %s, %s, %s %s" % (
            self.name,
            self.street,
            self.city,
            self.state,
            self.postalcode,
        )

    def serialize(self):
        """Serializes a Address into a dictionary"""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "name": self.name,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postalcode": self.postalcode,
        }

    def deserialize(self, data):
        """
        Deserializes a Address from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.account_id = data["account_id"]
            self.name = data["name"]
            self.street = data["street"]
            self.city = data["city"]
            self.state = data["state"]
            self.postalcode = data["postalcode"]
        except KeyError as error:
            raise DataValidationError("Invalid Address: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Address: body of request contained "
                "bad or no data " + error.args[0]
            )
        return self


######################################################################
#  A C C O U N T   M O D E L
######################################################################
class Account(db.Model, PersistentBase):
    """
    Class that represents an Account
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    phone_number = db.Column(db.String(32), nullable=True)  # phone is optional
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    addresses = db.relationship("Address", backref="account", lazy=True)

    def __repr__(self):
        return "<Account %r id=[%s]>" % (self.name, self.id)

    def serialize(self):
        """Serializes a Account into a dictionary"""
        account = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "date_joined": self.date_joined.strftime(DATETIME_FORMAT),
            "addresses": [],
        }
        for address in self.addresses:
            account["addresses"].append(address.serialize())
        return account

    def deserialize(self, data):
        """
        Deserializes a Account from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.email = data["email"]
            self.phone_number = data.get("phone_number")
            self.date_joined = datetime.strptime(data["date_joined"], DATETIME_FORMAT)
            # handle inner list of addresses
            address_list = data.get("addresses")
            for json_address in address_list:
                address = Address()
                address.deserialize(json_address)
                self.addresses.append(address)
        except KeyError as error:
            raise DataValidationError("Invalid Account: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid Account: body of request contained "
                "bad or no data - " + error.args[0]
            )
        return self

    @classmethod
    def find_by_name(cls, name):
        """Returns all Accounts with the given name

        Args:
            name (string): the name of the Accounts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
