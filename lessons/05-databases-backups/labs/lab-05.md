# Лабораторная работа 5: MySQL и система бэкапов

## Установка MySQL
```bash
# Обновляем пакеты
sudo apt update

# Устанавливаем MySQL Server
sudo apt install mysql-server -y

# Запускаем службу
sudo systemctl start mysql
sudo systemctl enable mysql

# Настраиваем безопасность
sudo mysql_secure_installation

# Входим в MySQL
sudo mysql -u root -p

-- Создаем базу данных для колледжа
CREATE DATABASE college_db;
USE college_db;

-- Создаем таблицу студентов
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    group_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Добавляем тестовые данные
INSERT INTO students (name, group_name) VALUES 
('Иванов Иван', 'ИТ-21'),
('Петров Петр', 'ИТ-21'),
('Сидорова Анна', 'ИТ-22');

-- Проверяем данные
SELECT * FROM students;

# Создаем скрипт для бэкапа
sudo nano /usr/local/bin/backup-mysql.sh

#!/bin/bash
# Скрипт автоматического бэкапа MySQL

BACKUP_DIR="/var/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="college_db"

# Создаем директорию для бэкапов
mkdir -p $BACKUP_DIR

# Создаем бэкап
mysqldump -u root -p $DB_NAME > $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# Архивируем
gzip $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# Удаляем старые бэкапы (старше 7 дней)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Бэкап создан: ${BACKUP_DIR}/${DB_NAME}_${DATE}.sql.gz"

# Редактируем cron
sudo crontab -e

# Добавляем задание для ежедневного бэкапа в 2:00
0 2 * * * /usr/local/bin/backup-mysql.sh

# Разархивируем бэкап
gzip -d backup_file.sql.gz

# Восстанавливаем базу
mysql -u root -p college_db < backup_file.sql