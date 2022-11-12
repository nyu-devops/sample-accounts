# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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
Test Factory to make fake objects for testing
"""
from datetime import date
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Account, Address


class AccountFactory(factory.Factory):
    """Creates fake Accounts"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""
        model = Account

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    email = factory.Faker("email")
    phone_number = factory.Faker("phone_number")
    date_joined = FuzzyDate(date(2008, 1, 1))
    # the many side of relationships can be a little wonky in factory boy:
    # https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship

    @factory.post_generation
    def addresses(self, create, extracted, **kwargs):   # pylint: disable=method-hidden, unused-argument
        """Creates the addresses list"""
        if not create:
            return

        if extracted:
            self.addresses = extracted


class AddressFactory(factory.Factory):
    """Creates fake Addresses"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""
        model = Address

    id = factory.Sequence(lambda n: n)
    account_id = None
    name = FuzzyChoice(choices=["home", "work", "other"])
    street = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state_abbr")
    postal_code = factory.Faker("postalcode")
    account = factory.SubFactory(AccountFactory)
