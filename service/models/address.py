"""
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")


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
