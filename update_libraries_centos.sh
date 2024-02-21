#!/bin/bash

# Update system packages
sudo yum update -y

# Install required packages
sudo yum install -y python3 mysql-server python3-pip virtualenv unzip gcc mariadb-devel
