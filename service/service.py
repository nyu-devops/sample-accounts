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
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return "Reminder: return some useful information in json format about the service here", status.HTTP_200_OK

######################################################################
# RETRIEVE A PET
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):
    """
    Retrieve a single Account

    This endpoint will return an Account based on it's id
    """
    app.logger.info("Request for Account with id: %s", account_id)
    account = Account.find(account_id)
    if not account:
        raise NotFound("Account with id '{}' was not found.".format(account_id))
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
# ADD AN ADDRESS TO AN ACCOUNT
######################################################################
@app.route('/accounts/<int:account_id>/addresses', methods=['POST'])
def add_address_to_account(account_id):
    app.logger.info("Request to add an address to an account")
    account = Account.find(account_id)
    if not account:
        abort(404, "Account not found")

    address = Address()
    address.deserialize(request.get_json())
    account.address.append(address)
    account.save()
    message = address.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED)



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