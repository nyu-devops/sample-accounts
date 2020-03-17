# sample-accounts

This repository contains sample code for Customer accounts for an e-commerce web site. This shows how to create a REST API with subordinate resources like accounts that have addresses:

**Note:** This repo has a `Vagrantfile` so the easiest way to play with it is to:

```bash
vagrant up
vagrant ssh
cd /vagrant
nosetests
flask run -h 0.0.0.0
```

These are the RESTful routes for `accounts` and `addresses`
```
Endpoint          Methods  Rule
----------------  -------  -----------------------------------------------------
index             GET      /
list_accounts     GET      /accounts

create_accounts   POST     /accounts
get_accounts      GET      /accounts/<account_id>
update_accounts   PUT      /accounts/<account_id>
delete_accounts   DELETE   /accounts/<account_id>

create_addresses  POST     /accounts/<account_id>/addresses
get_addresses     GET      /accounts/<account_id>/addresses/<address_id>
update_addresses  PUT      /accounts/<account_id>/addresses/<address_id>
delete_addresses  DELETE   /accounts/<account_id>/addresses/<address_id>
```

The test cases have 95% test coverage and can be run with `nosetests`
