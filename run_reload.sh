sudo systemctl stop csye6225 >> /home/csye6225/log.txt
sudo echo "stopped" >> /home/csye6225/log.txt
sudo systemctl daemon-reload
sudo echo "daemon-reloaded" >> /home/csye6225/log.txt
sudo systemctl reenable csye6225
sudo echo "reenabled" >> /home/csye6225/log.txt
sudo systemctl start csye6225
sudo echo "restarted" >> /home/csye6225/log.txt