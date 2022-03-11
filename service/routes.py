# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Account Service

This microservice handles the lifecycle of Accounts
"""
import os
import sys
import logging
from flask import jsonify, request, url_for, make_response, abort
from service.models import Account, Address, DataValidationError
from . import status  # HTTP Status Codes
from . import app  # Import Flask application


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
    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' could not be found.")

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
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' was not found.")

    account.deserialize(request.get_json())
    account.id = account_id
    account.update()
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
# LIST ADDRESSES
######################################################################
@app.route("/accounts/<int:account_id>/addresses", methods=["GET"])
def list_addresses(account_id):
    """ Returns all of the Addresses for an Account """
    app.logger.info("Request for all Addresses for Account with id: %s", account_id)

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' could not be found.")

    results = [address.serialize() for address in account.addresses]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# ADD AN ADDRESS TO AN ACCOUNT
######################################################################
@app.route('/accounts/<int:account_id>/addresses', methods=['POST'])
def create_addresses(account_id):
    """
    Create an Address on an Account

    This endpoint will add an address to an account
    """
    app.logger.info("Request to create an Address for Account with id: %s", account_id)
    check_content_type("application/json")

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' could not be found.")

    address = Address()
    address.deserialize(request.get_json())
    account.addresses.append(address)
    account.update()
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
    app.logger.info("Request to retrieve Address %s for Account id: %s", (address_id, account_id))

    address = Address.find(address_id)
    if not address:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{address_id}' could not be found.")

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
    app.logger.info("Request to update Address %s for Account id: %s", (address_id, account_id))
    check_content_type("application/json")

    address = Address.find(address_id)
    if not address:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{address_id}' could not be found.")

    address.deserialize(request.get_json())
    address.id = address_id
    address.update()
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
    app.logger.info("Request to delete Address %s for Account id: %s", (address_id, account_id))

    address = Address.find(address_id)
    if address:
        address.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)



######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    Account.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}")