-- DATABASE: campus_exchange
CREATE DATABASE IF NOT EXISTS campus_exchange;
USE campus_exchange;

-- STUDENT table
CREATE TABLE IF NOT EXISTS Student (
  StudentID INT AUTO_INCREMENT PRIMARY KEY,
  Name VARCHAR(100) NOT NULL,
  Email VARCHAR(100) UNIQUE,
  Phone VARCHAR(20),
  Department VARCHAR(50),
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ITEM table
CREATE TABLE IF NOT EXISTS Item (
  ItemID INT AUTO_INCREMENT PRIMARY KEY,
  OwnerID INT NOT NULL,
  ItemName VARCHAR(100) NOT NULL,
  Category VARCHAR(50),
  Description VARCHAR(255),
  `Condition` VARCHAR(50),
  Status ENUM('Available','Requested','Not Available','Exchanged') DEFAULT 'Available',
  CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (OwnerID) REFERENCES Student(StudentID) ON DELETE CASCADE
);

-- REQUEST table
CREATE TABLE IF NOT EXISTS Request (
  RequestID INT AUTO_INCREMENT PRIMARY KEY,
  ItemID INT NOT NULL,
  RequesterID INT NOT NULL,
  RequestDate DATE DEFAULT (CURRENT_DATE),
  Status ENUM('Pending','Approved','Rejected','Cancelled') DEFAULT 'Pending',
  Message VARCHAR(255),
  FOREIGN KEY (ItemID) REFERENCES Item(ItemID) ON DELETE CASCADE,
  FOREIGN KEY (RequesterID) REFERENCES Student(StudentID) ON DELETE CASCADE
);

-- EXCHANGE table
CREATE TABLE IF NOT EXISTS Exchange (
  ExchangeID INT AUTO_INCREMENT PRIMARY KEY,
  RequestID INT UNIQUE NOT NULL,
  ExchangeDate DATE DEFAULT (CURRENT_DATE),
  ReturnDate DATE NULL,
  Notes VARCHAR(255),
  FOREIGN KEY (RequestID) REFERENCES Request(RequestID) ON DELETE CASCADE
);

-- sample data
INSERT INTO Student (Name, Email, Phone, Department) VALUES
('Aditi Sharma', 'aditi@uni.edu', '9876543210', 'CSE'),
('Rahul Singh', 'rahul@uni.edu', '9876501234', 'ECE');

INSERT INTO Item (OwnerID, ItemName, Category, Description, `Condition`) VALUES
(1, 'Scientific Calculator', 'Electronics', 'Casio fx-991', 'Good'),
(2, 'Lab Coat', 'Clothing', 'White lab coat size M', 'Like New');
