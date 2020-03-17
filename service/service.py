"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Account, Address, DataValidationError

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=message
        ),
        status.HTTP_400_BAD_REQUEST,
    )


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message=message),
        status.HTTP_404_NOT_FOUND,
    )


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=message,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=message,
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=message,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
# LIST ALL ACCOUNTS
######################################################################
@app.route("/accounts", methods=["GET"])
def list_accounts():
    """ Returns all of the Accounts """
    app.logger.info("Request for Account list")
    accounts = []
    name = request.args.get("name")
    if name:
        accounts = Account.find_by_name(name)
    else:
        accounts = Account.all()

    results = [account.serialize() for account in accounts]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):
    """
    Retrieve a single Account

    This endpoint will return an Account based on it's id
    """
    app.logger.info("Request for Account with id: %s", account_id)
    account = Account.find_or_404(account_id)
    return make_response(jsonify(account.serialize()), status.HTTP_200_OK)


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    location_url = url_for("get_accounts", account_id=account.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_accounts(account_id):
    """
    Update an Account

    This endpoint will update an Account based the body that is posted
    """
    app.logger.info("Request to update account with id: %s", account_id)
    check_content_type("application/json")
    account = Account.find(account_id)
    if not account:
        raise NotFound("Account with id '{}' was not found.".format(account_id))
    account.deserialize(request.get_json())
    account.id = account_id
    account.save()
    return make_response(jsonify(account.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_accounts(account_id):
    """
    Delete an Account

    This endpoint will delete an Account based the id specified in the path
    """
    app.logger.info("Request to delete account with id: %s", account_id)
    account = Account.find(account_id)
    if account:
        account.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)


#---------------------------------------------------------------------
#                A D D R E S S   M E T H O D S
#---------------------------------------------------------------------


######################################################################
# ADD AN ADDRESS TO AN ACCOUNT
######################################################################
@app.route('/accounts/<int:account_id>/addresses', methods=['POST'])
def create_addresses(account_id):
    """
    Create an Address on an Account

    This endpoint will add an address to an account
    """
    app.logger.info("Request to add an address to an account")
    check_content_type("application/json")
    account = Account.find_or_404(account_id)
    address = Address()
    address.deserialize(request.get_json())
    account.addresses.append(address)
    account.save()
    message = address.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED)

######################################################################
# RETRIEVE AN ADDRESS FROM ACCOUNT
######################################################################
@app.route('/accounts/<int:account_id>/addresses/<int:address_id>', methods=['GET'])
def get_addresses(account_id, address_id):
    """
    Get an Address

    This endpoint returns just an address
    """
    app.logger.info("Request to get an address with id: %s", address_id)
    address = Address.find_or_404(address_id)
    return make_response(jsonify(address.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN ADDRESS
######################################################################
@app.route("/accounts/<int:account_id>/addresses/<int:address_id>", methods=["PUT"])
def update_addresses(account_id, address_id):
    """
    Update an Address

    This endpoint will update an Address based the body that is posted
    """
    app.logger.info("Request to update address with id: %s", address_id)
    check_content_type("application/json")
    address = Address.find_or_404(address_id)
    address.deserialize(request.get_json())
    address.id = address_id
    address.save()
    return make_response(jsonify(address.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE AN ADDRESS
######################################################################
@app.route("/accounts/<int:account_id>/addresses/<int:address_id>", methods=["DELETE"])
def delete_addresses(account_id, address_id):
    """
    Delete an Address

    This endpoint will delete an Address based the id specified in the path
    """
    app.logger.info("Request to delete account with id: %s", account_id)
    address = Address.find(address_id)
    if address:
        address.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)



######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Account.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))