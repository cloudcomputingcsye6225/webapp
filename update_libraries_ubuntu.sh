#!/bin/bash

# Update system packages
sudo apt update -y

# Upgrade system packages
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 mysql-server python3-pip virtualenv unzip gcc libmysqlclient-dev
