#!/bin/bash

# Update system packages
sudo apt update -y

# Upgrade system packages
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y

# Install required packages
sudo DEBIAN_FRONTEND=noninteractive apt install -y python3 mysql-server python3-pip virtualenv unzip gcc libmysqlclient-dev
