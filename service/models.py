"""
Models for Account

All of the models are stored in this module
"""

import logging
from datetime import date
from abc import abstractmethod
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""

    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""

    def create(self) -> None:
        """
        Creates a Account to the database
        """
        logger.info("Creating %s", self)
        # id must be none to generate next primary key
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self) -> None:
        """
        Updates a Account to the database
        """
        logger.info("Updating %s", self)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self) -> None:
        """Removes a Account from the data store"""
        logger.info("Deleting %s", self)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        # pylint: disable=no-member
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        # pylint: disable=no-member
        return cls.query.session.get(cls, by_id)


######################################################################
#  A D D R E S S   M O D E L
######################################################################
class Address(db.Model, PersistentBase):
    """
    Class that represents an Address
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(
        db.Integer, db.ForeignKey("account.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(64))  # e.g., work, home, vacation, etc.
    street = db.Column(db.String(64))
    city = db.Column(db.String(64))
    state = db.Column(db.String(2))
    postal_code = db.Column(db.String(16))

    def __repr__(self):
        return f"<Address {self.name} id=[{self.id}] account[{self.account_id}]>"

    def __str__(self):
        return (
            f"{self.name}: {self.street}, {self.city}, {self.state} {self.postal_code}"
        )

    def serialize(self) -> dict:
        """Converts an Address into a dictionary"""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "name": self.name,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates an Address from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.account_id = data["account_id"]
            self.name = data["name"]
            self.street = data["street"]
            self.city = data["city"]
            self.state = data["state"]
            self.postal_code = data["postal_code"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Address: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Address: body of request contained bad or no data "
                + str(error)
            ) from error

        return self


######################################################################
#  A C C O U N T   M O D E L
######################################################################
class Account(db.Model, PersistentBase):
    """
    Class that represents an Account
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    phone_number = db.Column(db.String(32), nullable=True)  # phone number is optional
    date_joined = db.Column(db.Date(), nullable=False, default=date.today())
    addresses = db.relationship("Address", backref="account", passive_deletes=True)

    def __repr__(self):
        return f"<Account {self.name} id=[{self.id}]>"

    def serialize(self):
        """Converts an Account into a dictionary"""
        account = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "date_joined": self.date_joined.isoformat(),
            "addresses": [],
        }
        for address in self.addresses:
            account["addresses"].append(address.serialize())
        return account

    def deserialize(self, data):
        """
        Populates an Account from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.email = data["email"]
            self.phone_number = data.get("phone_number")
            self.date_joined = date.fromisoformat(data["date_joined"])
            # handle inner list of addresses
            address_list = data.get("addresses")
            for json_address in address_list:
                address = Address()
                address.deserialize(json_address)
                self.addresses.append(address)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Account: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Account: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    @classmethod
    def find_by_name(cls, name):
        """Returns all Accounts with the given name

        Args:
            name (string): the name of the Accounts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
