# Software Development Guide - Fall 2021

The Fall of 2021 was the last semester we used **Vagrant** and **VirtualBox**. If you are taking my class after that semester please see the [Software Development Guide - Spring 2022](vscode-docker.md)

If you do not want to use Visual Studio Code and Docker then these are the setup instructions for you.

## Prerequisite Software Installation

This project uses Vagrant and VirtualBox to provide a consistent repeatable disposable development environment for all of the labs in this course. If you don't have this software the first step is down download and install it.

You will need the following software installed:

- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/)

All of these can be installed manually by clicking on the links above or you can use a package manager like **Homebrew** on Mac of **Chocolatey** on Windows.

You can read more about creating these environments in my article: [Creating Reproducible Development Environments](https://johnrofrano.medium.com/creating-reproducible-development-environments-fac8d6471f35)

## Bring up the development environment

To bring up the development environment you should clone this repo, change into the repo directory:

```bash
git clone https://github.com/nyu-devops/sample-accounts.git
cd sample-accounts
```

Then bring up a virtual machine (VM) using Vagrant with the `vagrant up` command. Then `ssh` into the VM with `vagrant ssh`. And finally change into the `/vagrant` folder like this:

```bash
vagrant up
vagrant ssh
cd /vagrant
```

This will place you in the virtual machine in the `/vagrant` folder which has been shared with your computer so that your source files can be edited outside of the VM and run inside of the VM.

## Shutdown development environment

Using Vagrant and VirtualBox, when you are done, you can exit and shut down the vm with:

```shell
exit
vagrant halt
```

If the VM is no longer needed you can remove it with:

```shell
vagrant destroy
```
