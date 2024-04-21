######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
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
######################################################################
# cspell:ignore userid postalcode
"""
Test Factory to make fake objects for testing
"""
from datetime import date
from factory import Factory, SubFactory, Sequence, Faker, post_generation
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Account, Address


class AccountFactory(Factory):
    """Creates fake Accounts"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Account

    id = Sequence(lambda n: n)
    name = Faker("name")
    userid = Sequence(lambda n: f"User{n:04d}")
    email = Faker("email")
    phone_number = Faker("phone_number")
    date_joined = FuzzyDate(date(2008, 1, 1))
    # the many side of relationships can be a little wonky in factory boy:
    # https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship

    @post_generation
    def addresses(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the addresses list"""
        if not create:
            return

        if extracted:
            self.addresses = extracted


class AddressFactory(Factory):
    """Creates fake Addresses"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Address

    id = Sequence(lambda n: n)
    account_id = None
    name = FuzzyChoice(choices=["home", "work", "other"])
    street = Faker("street_address")
    city = Faker("city")
    state = Faker("state_abbr")
    postal_code = Faker("postalcode")
    account = SubFactory(AccountFactory)
