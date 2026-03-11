CREATE DATABASE IF NOT EXISTS gym_management;

USE gym_management;

-- Users table
CREATE TABLE users(
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100),
email VARCHAR(100) UNIQUE,
password VARCHAR(100),
phone VARCHAR(20)
);

-- Admin table
CREATE TABLE admin(
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50),
password VARCHAR(50)
);

INSERT INTO admin(username,password)
VALUES("admin","admin123");

-- Membership plans
CREATE TABLE plans(
id INT AUTO_INCREMENT PRIMARY KEY,
plan_name VARCHAR(50),
price INT,
duration VARCHAR(50)
);

INSERT INTO plans(plan_name,price,duration) VALUES
("Monthly",1000,"1 Month"),
("Quarterly",2500,"3 Months"),
("Half Yearly",4500,"6 Months"),
("Yearly",8000,"12 Months");

-- Membership purchases
CREATE TABLE memberships(
id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT,
plan_id INT,
purchase_date DATE,
FOREIGN KEY(user_id) REFERENCES users(id),
FOREIGN KEY(plan_id) REFERENCES plans(id)
);