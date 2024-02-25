#!/bin/bash

# Define the file path
selinux_config="/etc/selinux/config"

# Check if the file exists
if [ ! -f "$selinux_config" ]; then
    echo "SELinux configuration file not found: $selinux_config"
    exit 1
fi

# Search for the line containing "SELINUX=enforcing" and replace it with "SELINUX=disabled"
sed -i 's/^SELINUX=enforcing$/SELINUX=disabled/' "$selinux_config"

# Check if the sed command was successful
if [ $? -ne 0 ]; then
    echo "Failed to modify SELinux configuration"
    exit 1
fi

echo "SELinux configuration updated successfully."

