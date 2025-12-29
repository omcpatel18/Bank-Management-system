# 🏦 Bank Management System (Python + MySQL)

A simple yet practical **Bank Management System** built using **Python** and **MySQL**, designed to simulate real-world banking operations such as account creation, deposits, withdrawals, balance checks, and transaction tracking.

This project focuses on **core Python concepts**, **database integration**, and **clean logic**, making it ideal for learning, interviews, and backend fundamentals.

---

## 📌 Project Overview

Managing bank operations manually is inefficient and error-prone.  
This project demonstrates how a basic banking system can be automated using Python with a structured database backend.

The system allows users to:
- Create and manage bank accounts
- Perform secure transactions
- Store and retrieve data from a relational database
- Maintain transaction history accurately

---

## ✨ Features

- 🔐 **Account Creation**
- 💰 **Deposit & Withdrawal Operations**
- 📊 **Balance Enquiry**
- 🧾 **Transaction History Tracking**
- 🗄️ **MySQL Database Integration**
- ❌ **Input Validation & Error Handling**

---

## 🛠️ Technologies Used

- **Programming Language:** Python  
- **Database:** MySQL  
- **Libraries / Modules:**
  - `mysql.connector`
  - `datetime`
- **Tools:**
  - VS Code
  - MySQL Workbench

---

## 🗂️ Database Design

### Tables Used:
- **accounts**
  - account_number
  - name
  - balance
  - account_type
- **transactions**
  - transaction_id
  - account_number
  - transaction_type
  - amount
  - date_time

Relational integrity is maintained using primary and foreign keys.

---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository
git clone https://github.com/your-username/bank-management-system.git

### 2️⃣ Install Required Library
pip install mysql-connector-python

3️⃣ Setup MySQL Database

Create a database (e.g., bank_db)

Create required tables using provided SQL schema

Update database credentials in the Python file

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="bank_db"
)

4️⃣ Run the Application
python main.py




