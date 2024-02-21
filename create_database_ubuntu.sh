# Start MySQL service
sudo systemctl start mysql

# Create MySQL database and user
sudo mysql -e "CREATE DATABASE $MYSQL_DATABASE;"
sudo mysql -e "CREATE USER '$MYSQL_USER'@'$MYSQL_HOST' IDENTIFIED BY '$MYSQL_PASSWORD';"
sudo mysql -e "GRANT ALL PRIVILEGES ON $MYSQL_DATABASE.* TO '$MYSQL_USER'@'$MYSQL_HOST';"
sudo mysql -e "FLUSH PRIVILEGES;"
