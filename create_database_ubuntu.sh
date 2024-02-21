# Start MySQL service
sudo systemctl start mysql

# Create MySQL database and user
sudo mysql -u root --skip-password -e "CREATE DATABASE $MYSQL_DATABASE;"
sudo mysql -u root --skip-password -e "CREATE USER '$MYSQL_USER'@'$MYSQL_HOST' IDENTIFIED BY '$MYSQL_PASSWORD';"
sudo mysql -u root --skip-password -e "GRANT ALL PRIVILEGES ON $MYSQL_DATABASE.* TO '$MYSQL_USER'@'$MYSQL_HOST';"
sudo mysql -u root --skip-password -e "FLUSH PRIVILEGES;"
