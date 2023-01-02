USE mysql;
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost';
ALTER USER 'root'@'%' identified WITH mysql_native_password BY 'root';
CREATE USER 'stock'@'localhost' identified BY 'stock';
CREATE USER 'stock'@'%' identified BY 'stock';
GRANT ALL PRIVILEGES ON *.* TO 'stock'@'localhost';
GRANT ALL PRIVILEGES ON *.* TO 'stock'@'%';
FLUSH PRIVILEGES;