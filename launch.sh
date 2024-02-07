pip3 install -r r.txt
sudo systemctl restart mysqld
gunicorn --bind 0.0.0.0:8888 gunicorn_interface:app &


