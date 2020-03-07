"""
Models for <your resource name>

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class YourResourceModel(db.Model):
    """
    Class that represents a <your resource model name>
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))

    def __repr__(self):
        return "<<your resource name> %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a <your resource name> to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a <your resource name> to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a <your resource name> from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a <your resource name> into a dictionary """
        return {
            "id": self.id,
            "name": self.name
        }

    def deserialize(self, data):
        """
        Deserializes a <your resource name> from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
        except KeyError as error:
            raise DataValidationError("Invalid <your resource name>: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid <your resource name>: body of request contained" "bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the <your resource name>s in the database """
        logger.info("Processing all <your resource name>s")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a <your resource name> by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a <your resource name> by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_name(cls, name):
        """ Returns all <your resource name>s with the given name

        Args:
            name (string): the name of the <your resource name>s you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
