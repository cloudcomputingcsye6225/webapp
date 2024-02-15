pip install -r requirements.txt
sudo systemctl restart mysqld
gunicorn --bind 0.0.0.0:8888 gunicorn_interface:app &


