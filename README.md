
## Run the Flask App
To demonstrate, go to the directory where app.py is located (make sure sentiment.pkl is there too) and start Flask by typing:
```shell
flask run

```

Output :
```
FLASK_APP = app.py
FLASK_ENV = development
FLASK_DEBUG = 0
In folder /Users/mudassers/Documents/MLFlaskSpammer
/Users/mudassers/Documents/MLFlaskSpammer/venv/bin/python -m flask run 
 * Serving Flask app 'app.py'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit

```


## MySQL 
1. Start the MySQL server
```shell
docker-compose up -d 
```
2. Verify the mysql installation by
```shell
docker-compose ps 
```

3. Check the existing database
```shell
docker exec mysql mysql -u user1 -pS0meVeryHardPassword -e "show databases;"
```

4. Run mysql commands 
```shell
docker exec -it mysql /bin/bash
```
```shell
docker exec -i mysql sh -c 'exec mysql -u root -ppassword' < classicmodels.sql
```

Database Connection enter the following details -
```
Hostname : 0.0.0.0
Port: 3036
UserName : root / password

mysql://root:password@0.0.0.0:3036/classicmodels
```

If you have trouble installing `flask-mysqldb` 
```shell
brew install mysql pkg-config
```

Output :
```
==> mysql
We've installed your MySQL database without a root password. To secure it run:
mysql_secure_installation

MySQL is configured to only allow connections from localhost by default

To connect run:
mysql -u root

To start mysql now and restart at login:
brew services start mysql
Or, if you don't want/need a background service you can just run:
/usr/local/opt/mysql/bin/mysqld_safe --datadir\=/usr/local/var/mysql
```