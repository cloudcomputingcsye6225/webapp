#!/bin/bash
MYSQL_HOST=$(sudo curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/MYSQL_HOST)
MYSQL_USER=$(sudo curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/MYSQL_USER)
MYSQL_ROOT_PASSWORD=$(sudo curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/MYSQL_ROOT_PASSWORD)
MYSQL_DATABASE=$(sudo curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/MYSQL_DATABASE)
MYSQL_PASSWORD=$(sudo curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/MYSQL_PASSWORD)
MYSQL_PORT=$(sudo curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/attributes/MYSQL_PORT)

echo "MYSQL_HOST=$MYSQL_HOST" | sudo tee /home/csye6225/environmentfile.env > /dev/null
echo "MYSQL_USER=$MYSQL_USER" | sudo tee -a /home/csye6225/environmentfile.env > /dev/null
echo "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" | sudo tee -a /home/csye6225/environmentfile.env > /dev/null
echo "MYSQL_DATABASE=$MYSQL_DATABASE" | sudo tee -a /home/csye6225/environmentfile.env > /dev/null
echo "MYSQL_PASSWORD=$MYSQL_PASSWORD" | sudo tee -a /home/csye6225/environmentfile.env > /dev/null
echo "MYSQL_PORT=$MYSQL_PORT" | sudo tee -a /home/csye6225/environmentfile.env > /dev/null


sudo systemctl stop csye6225 >> /home/csye6225/log.txt
sudo systemctl daemon-reload >> /home/csye6225/log.txt
sudo systemctl reenable csye6225 >> /home/csye6225/log.txt
sudo systemctl start csye6225 >> /home/csye6225/log.txt
