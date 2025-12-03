# Лабораторная работа 5: MySQL и система бэкапов

# Лабораторная работа 5: PostgreSQL и система бэкапов

## 📋 Задание
Установить PostgreSQL, создать базу данных для колледжа, настроить автоматические бэкапы и освоить восстановление данных.

## 🛠️ Инструкция

### Часть 1: Установка и настройка PostgreSQL

#### Установка PostgreSQL
```bash
# Обновляем пакеты
sudo apt update

# Устанавливаем PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Запускаем службу
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Проверяем статус
sudo systemctl status postgresql

# Переключаемся на пользователя postgres
sudo -u postgres psql

-- Сменим пароль для пользователя postgres
\password postgres

-- Выйдем из psql
\q

# Редактируем конфигурационный файл
sudo nano /etc/postgresql/14/main/postgresql.conf

# Раскомментируем и изменяем строку:
listen_addresses = 'localhost,127.0.0.1'

# Настраиваем аутентификацию
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Добавляем строку для доступа по сети:
host    all             all             192.168.1.0/24          md5

# Перезапускаем PostgreSQL
sudo systemctl restart postgresql

# Входим в PostgreSQL
sudo -u postgres psql

-- Создаем базу данных для колледжа
CREATE DATABASE college_db;

-- Подключаемся к базе данных
\c college_db

-- Создаем таблицу студентов
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    group_name VARCHAR(20),
    enrollment_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создаем таблицу курсов
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    description TEXT,
    credits INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создаем таблицу оценок
CREATE TABLE grades (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    grade INTEGER CHECK (grade >= 1 AND grade <= 5),
    exam_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создаем индекс для ускорения поиска
CREATE INDEX idx_students_group ON students(group_name);
CREATE INDEX idx_grades_student ON grades(student_id);

-- Добавляем студентов
INSERT INTO students (first_name, last_name, email, group_name) VALUES 
('Иван', 'Иванов', 'ivanov@college.edu', 'ИТ-21'),
('Петр', 'Петров', 'petrov@college.edu', 'ИТ-21'),
('Анна', 'Сидорова', 'sidorova@college.edu', 'ИТ-22'),
('Мария', 'Козлова', 'kozlovа@college.edu', 'КС-23'),
('Алексей', 'Николаев', 'nikolaev@college.edu', 'ПИ-20');

-- Добавляем курсы
INSERT INTO courses (course_name, description, credits) VALUES 
('Администрирование Linux', 'Основы работы с Linux серверами', 4),
('Базы данных', 'Проектирование и работа с СУБД', 5),
('Веб-разработка', 'Создание веб-приложений', 4),
('Сетевые технологии', 'Основы компьютерных сетей', 3);

-- Добавляем оценки
INSERT INTO grades (student_id, course_id, grade) VALUES 
(1, 1, 5), (1, 2, 4), (1, 3, 5),
(2, 1, 4), (2, 2, 3), (2, 4, 5),
(3, 1, 5), (3, 3, 4), (3, 4, 4);

-- Просмотр всех студентов
SELECT * FROM students;

-- Студенты конкретной группы
SELECT first_name, last_name, email 
FROM students 
WHERE group_name = 'ИТ-21';

-- Средний балл по студентам
SELECT 
    s.first_name,
    s.last_name,
    ROUND(AVG(g.grade), 2) as average_grade
FROM students s
JOIN grades g ON s.id = g.student_id
GROUP BY s.id, s.first_name, s.last_name
ORDER BY average_grade DESC;

-- Количество студентов в группах
SELECT group_name, COUNT(*) as student_count
FROM students
GROUP BY group_name
ORDER BY student_count DESC;

# Создаем скрипт бэкапа
sudo nano /usr/local/bin/backup-postgresql.sh

#!/bin/bash
# Скрипт автоматического бэкапа PostgreSQL

# Настройки
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="college_db"
RETENTION_DAYS=7

# Создаем директорию для бэкапов
sudo mkdir -p $BACKUP_DIR
sudo chown postgres:postgres $BACKUP_DIR

# Создаем бэкап
echo "Создание бэкапа базы данных $DB_NAME..."
sudo -u postgres pg_dump $DB_NAME > $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# Архивируем
echo "Архивация бэкапа..."
sudo -u postgres gzip $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# Проверяем что бэкап создан
if [ $? -eq 0 ]; then
    echo "✅ Бэкап успешно создан: $BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz"
    
    # Удаляем старые бэкапы (старше 7 дней)
    sudo -u postgres find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete
    echo "🗑️ Удалены бэкапы старше $RETENTION_DAYS дней"
else
    echo "❌ Ошибка при создании бэкапа!"
    exit 1
fi

# Даем права на выполнение
sudo chmod +x /usr/local/bin/backup-postgresql.sh

# Тестируем скрипт
sudo /usr/local/bin/backup-postgresql.sh

# Редактируем cron для пользователя postgres
sudo crontab -u postgres -e

# Добавляем задание для ежедневного бэкапа в 2:00
0 2 * * * /usr/local/bin/backup-postgresql.sh

# Добавляем задание для еженедельного полного бэкапа в воскресенье в 3:00
0 3 * * 0 /usr/local/bin/backup-postgresql.sh

# Останавливаем приложения, использующие БД (если есть)
sudo systemctl stop nginx

# Восстанавливаем из бэкапа
sudo -u postgres psql -d college_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Разархивируем и восстанавливаем
sudo -u postgres gunzip -c /var/backups/postgresql/college_db_20231220_020000.sql.gz | sudo -u postgres psql college_db

# Запускаем приложения обратно
sudo systemctl start nginx

echo "✅ База данных успешно восстановлена из бэкапа"

# Создаем скрипт восстановления
sudo nano /usr/local/bin/restore-postgresql.sh

#!/bin/bash
# Скрипт восстановления PostgreSQL из бэкапа

BACKUP_DIR="/var/backups/postgresql"
DB_NAME="college_db"

# Проверяем наличие последнего бэкапа
LATEST_BACKUP=$(sudo -u postgres ls -t $BACKUP_DIR/*.gz | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ Бэкапы не найдены!"
    exit 1
fi

echo "Восстановление из бэкапа: $LATEST_BACKUP"

# Останавливаем зависимости (если нужно)
# sudo systemctl stop nginx

# Восстанавливаем базу
echo "Восстановление базы данных..."
sudo -u postgres gunzip -c $LATEST_BACKUP | sudo -u postgres psql $DB_NAME

if [ $? -eq 0 ]; then
    echo "✅ База данных успешно восстановлена"
    # sudo systemctl start nginx
else
    echo "❌ Ошибка при восстановлении"
    exit 1
fi

-- Размер базы данных
SELECT pg_size_pretty(pg_database_size('college_db'));

-- Размер таблиц
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size(table_name)) as size
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size(table_name) DESC;

-- Активные подключения
SELECT count(*) FROM pg_stat_activity;

-- Статистика по таблицам
SELECT 
    schemaname,
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables;

# Автовакуум (настроен по умолчанию)
sudo -u postgres psql -d college_db -c "VACUUM ANALYZE;"

# Резервное копирование конфигурации
sudo tar -czf /var/backups/postgresql-config-$(date +%Y%m%d).tar.gz /etc/postgresql/

📊 Проверка работы
Тест 1: Проверка установки PostgreSQL
bash
# Проверяем что служба работает
sudo systemctl status postgresql

# Проверяем подключение к БД
sudo -u postgres psql -c "\l"
Тест 2: Проверка базы данных
sql
-- Проверяем что таблицы созданы
\dt

-- Проверяем данные
SELECT COUNT(*) FROM students;
SELECT COUNT(*) FROM courses;
SELECT COUNT(*) FROM grades;
Тест 3: Проверка бэкапов
bash
# Проверяем что бэкапы создаются
sudo ls -la /var/backups/postgresql/

# Проверяем cron задачи
sudo crontab -u postgres -l

🐛 Решение проблем
Проблема: "Connection refused"
Решение: Проверьте что PostgreSQL слушает правильный адрес в postgresql.conf

Проблема: "Permission denied" при бэкапе
Решение: Убедитесь что скрипт выполняется от пользователя postgres

Проблема: Недостаточно места для бэкапа
Решение: Настройте очистку старых бэкапов или увеличьте место