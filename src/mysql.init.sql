CREATE USER IF NOT EXISTS 'data' IDENTIFIED BY 'password';
CREATE USER IF NOT EXISTS 'data'@'localhost' IDENTIFIED BY 'password';
flush privileges;
GRANT ALL privileges ON stock.* TO 'data'@'%';
GRANT ALL privileges ON stock.* TO 'data'@'localhost';
flush privileges;

CREATE DATABASE IF NOT EXISTS stock;