CREATE DATABASE BusinessData;
SHOW DATABASES;
USE BusinessData;
CREATE DATABASE IF NOT EXISTS BusinessData;
CREATE USER 'food_user'@'localhost' IDENTIFIED BY 'food123';
GRANT ALL PRIVILEGES ON BusinessData.* TO 'food_user'@'localhost';
FLUSH PRIVILEGES;
mysql -u food_user -p
SELECT user, host FROM mysql.user;
DROP USER IF EXISTS 'food_user'@'localhost';
CREATE USER 'food_user'@'localhost' IDENTIFIED BY 'food123';
GRANT ALL PRIVILEGES ON BusinessData.* TO 'food_user'@'localhost';
FLUSH PRIVILEGES;
SHOW GRANTS FOR 'food_user'@'localhost';
GRANT ALL PRIVILEGES ON `BusinessData`.* TO 'food_user'@'localhost'
ALTER TABLE cleaned_food_delivery_data
MODIFY Delivery_Rating DECIMAL(3,2);

ALTER TABLE cleaned_food_delivery_data
MODIFY Delivery_Time_Min VARCHAR(50);

ALTER TABLE cleaned_food_delivery_data
MODIFY Delivery_Rating DECIMAL(3,2);

TRUNCATE TABLE cleaned_food_delivery_data;
SELECT Order_ID, Customer_Age, Customer_Gender FROM cleaned_food_delivery_data LIMIT 10;
SELECT COUNT(*) FROM cleaned_food_delivery_data;
CREATE DATABASE BusinessData;
USE BusinessData;
SELECT * FROM cleaned_food_delivery_data LIMIT 5;
SELECT City, COUNT(*) AS total_orders FROM cleaned_food_delivery_data GROUP BY City
ORDER BY total_orders DESC;
SELECT COUNT(*) FROM cleaned_food_delivery_data;
SELECT * FROM cleaned_food_delivery_data LIMIT 5;
SELECT City, COUNT(*) AS total_orders
FROM cleaned_food_delivery_data
WHERE City IS NOT NULL
GROUP BY City
ORDER BY total_orders DESC;
SELECT COALESCE(City, 'Unknown') AS City, COUNT(*) AS total_orders
FROM cleaned_food_delivery_data
GROUP BY City
ORDER BY total_orders DESC;
SELECT City, AVG(Delivery_Time_Min) AS avg_delivery_time
FROM cleaned_food_delivery_data
GROUP BY City;
SELECT City, SUM(Order_Value) AS total_revenue
FROM cleaned_food_delivery_data
GROUP BY City
ORDER BY total_revenue DESC;
SELECT Restaurant_Name, COUNT(*) AS orders
FROM cleaned_food_delivery_data
GROUP BY Restaurant_Name
ORDER BY orders DESC
LIMIT 10;
SELECT City, COUNT(*) AS total_orders
FROM cleaned_food_delivery_data
WHERE City IS NOT NULL
GROUP BY City;

















