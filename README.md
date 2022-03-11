# Accounts Service

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This repository contains sample code for Customer accounts for an e-commerce web site. This shows how to create a REST API with subordinate resources like accounts that have addresses:

**Note:** This repo has a both a `.devcontainer` folder and a `Vagrantfile` for two ways to bring up a development environment.

## Development environment setup

Select the appropriate development environment setup. Most students should choose the first one using Docker and Visual Studio Code.

### For Spring 2022 forward

If you are taking this course in the Spring of 2022 or later, follow these instructions: [Software Development Guide - Spring 2022](docs/vscode-docker.md)

### For Fall 2021 and earlier

If you are took this course in the Fall of 2021 or earlier, follow these instructions: [Software Development Guide - Fall 2021](docs/vagrant-virtualbox.md)

## Information about this repo

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

list_addresses    GET      /accounts/<int:account_id>/addresses
create_addresses  POST     /accounts/<account_id>/addresses
get_addresses     GET      /accounts/<account_id>/addresses/<address_id>
update_addresses  PUT      /accounts/<account_id>/addresses/<address_id>
delete_addresses  DELETE   /accounts/<account_id>/addresses/<address_id>
```

The test cases have 95% test coverage and can be run with `nosetests`

## Running the service

The project uses *honcho* which gets it's commands from the `Procfile`. To start the service simply use:

```shell
$ honcho start
```

You should be able to reach the service at: http://localhost:8000. The port that is used is controlled by an environment variable defined in the `.flaskenv` file which Flask uses to load it's configuration from the environment by default.

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repo is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** conceived, created and taught by *John Rofrano*
