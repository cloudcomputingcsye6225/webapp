#!/bin/bash
sudo systemctl stop csye6225 >> /home/csye6225/log.txt
sudo systemctl daemon-reload >> /home/csye6225/log.txt
sudo systemctl reenable csye6225 >> /home/csye6225/log.txt
sudo systemctl start csye6225 >> /home/csye6225/log.txt
