# Crumhorn

Crumhorn is a codification of my manual cloud instance management.

## Features

Crumhorn aims to support the following:
* Launching environments (e.g. "Spin up a Fedora 23 machine")
* Provisioning new environment setups that can be launched (e.g. "Set up a Fedora 23 box with sensible security defaults, user accounts, ...")
* Managing previously created setups / running environments

It aims to do so on the following platforms:
* Digital Ocean
  * Launch environment = start vm
  * Provision new setup = start vm, configure, take a snapshot
  * Management = list / remove snapshots / running VMs

## Installation

Not recommended. This is just a personal project to codify some of my day-to-day cloud admin tasks

Currently I do:

    virtualenv --python=python3 . 
    . bin/activate 
    pip install -U pip setuptools wheel 
    pip install -E .


