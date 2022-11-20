USE mysql;
CREATE USER 'stock'@'localhost' identified BY 'stock';
CREATE USER 'stock'@'%' identified BY 'stock';
GRANT ALL PRIVILEGES ON stock.* TO 'stock'@'localhost';
GRANT ALL PRIVILEGES ON *.* TO 'stock'@'localhost';
GRANT ALL PRIVILEGES ON stock.* TO 'stock'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'stock'@'%';
FLUSH PRIVILEGES;