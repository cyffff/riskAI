#!/bin/bash

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
  echo "MySQL is not installed. Please install MySQL and try again."
  exit 1
fi

# Check if MySQL is running
if ! pgrep -x "mysqld" > /dev/null; then
  echo "MySQL is not running. Please start MySQL and try again."
  exit 1
fi

echo "Setting up MySQL database for Credit Risk AI Assistant..."

# Create database and user
mysql -u root -p << EOF
CREATE DATABASE IF NOT EXISTS risk_ai;
CREATE USER IF NOT EXISTS 'risk_user'@'localhost' IDENTIFIED BY 'risk_password';
GRANT ALL PRIVILEGES ON risk_ai.* TO 'risk_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "Database setup complete!"
echo "Database: risk_ai"
echo "User: risk_user"
echo "Password: risk_password" 