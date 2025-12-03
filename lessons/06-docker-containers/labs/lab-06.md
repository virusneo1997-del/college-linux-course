# Лабораторная работа #6: Docker и контейнеризация приложений

## 📋 Задание
Развернуть полноценное веб-приложение колледжа с использованием Docker контейнеров.

## 🎯 Цели
- Установить Docker и Docker Compose
- Создать многоконтейнерное приложение
- Настроить сетевую коммуникацию между контейнерами
- Реализовать сохранение данных с помощью volumes
- Настроить оркестрацию с Docker Compose

## ⚙️ Подготовка

### Необходимое ПО
- Ubuntu 20.04+
- Docker Engine
- Docker Compose

## 🚀 Выполнение

### Часть 1: Установка Docker

```bash
# Обновляем пакеты
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые пакеты
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release -y

# Добавляем официальный GPG ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавляем репозиторий Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Устанавливаем Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io -y

# Добавляем текущего пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагружаемся или выходим/входим в систему
sudo reboot

# Проверяем установку
docker --version
docker ps

# Скачиваем актуальную версию Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Даем права на выполнение
sudo chmod +x /usr/local/bin/docker-compose

# Проверяем установку
docker-compose --version

mkdir college-app
cd college-app
mkdir app nginx

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import asyncpg
import os

app = FastAPI(title="College API", version="1.0.0")

# Модели данных
class Student(BaseModel):
    id: int = None
    first_name: str
    last_name: str
    email: str
    group_name: str = None

class Course(BaseModel):
    id: int = None
    title: str
    description: str = None

# Подключение к базе данных
async def get_db_connection():
    return await asyncpg.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'college'),
        user=os.getenv('DB_USER', 'college_user'),
        password=os.getenv('DB_PASSWORD', 'college_password')
    )

@app.get("/")
async def root():
    return {"message": "College Management System API", "version": "1.0.0"}

@app.get("/students", response_model=List[Student])
async def get_students():
    conn = await get_db_connection()
    try:
        students = await conn.fetch("SELECT * FROM students ORDER BY id")
        return [dict(student) for student in students]
    finally:
        await conn.close()

@app.post("/students", response_model=Student)
async def create_student(student: Student):
    conn = await get_db_connection()
    try:
        student_id = await conn.fetchval(
            "INSERT INTO students (first_name, last_name, email, group_name) VALUES ($1, $2, $3, $4) RETURNING id",
            student.first_name, student.last_name, student.email, student.group_name
        )
        student.id = student_id
        return student
    finally:
        await conn.close()

@app.get("/courses", response_model=List[Course])
async def get_courses():
    conn = await get_db_connection()
    try:
        courses = await conn.fetch("SELECT * FROM courses ORDER BY id")
        return [dict(course) for course in courses]
    finally:
        await conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

  
  
##Создаем файл зависимостей: app/requirements.txt

txt
fastapi==0.104.1
uvicorn==0.24.0
asyncpg==0.29.0
python-multipart==0.0.6

#Создание Dockerfile
app/Dockerfile

dockerfile
FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash app
USER app

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Настройка Nginx
nginx/nginx.conf

nginx
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /app/static/;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
nginx/Dockerfile

dockerfile
FROM nginx:1.25-alpine

# Копируем конфигурацию
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Создаем директорию для статики
RUN mkdir -p /app/static

EXPOSE 80
Часть 6: Создание docker-compose.yml
docker-compose.yml

yaml
version: '3.8'

services:
  # База данных PostgreSQL
  db:
    image: postgres:15-alpine
    container_name: college_db
    environment:
      POSTGRES_DB: college
      POSTGRES_USER: college_user
      POSTGRES_PASSWORD: college_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - college_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U college_user -d college"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Веб-приложение
  web:
    build: ./app
    container_name: college_web
    environment:
      DB_HOST: db
      DB_NAME: college
      DB_USER: college_user
      DB_PASSWORD: college_password
    volumes:
      - ./app:/app
    depends_on:
      db:
        condition: service_healthy
    networks:
      - college_network
    restart: unless-stopped

  # Nginx прокси
  nginx:
    build: ./nginx
    container_name: college_nginx
    ports:
      - "80:80"
    depends_on:
      - web
    networks:
      - college_network
    restart: unless-stopped

# Сети
networks:
  college_network:
    driver: bridge

# Тома для данных
volumes:
  postgres_data:

# Создание скрипта инициализации БД
init.sql

sql
-- Создание таблиц для колледжа
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    group_name VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    credits INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставка тестовых данных
INSERT INTO students (first_name, last_name, email, group_name) VALUES
('Алексей', 'Иванов', 'a.ivanov@college.edu', 'CS-101'),
('Елена', 'Кузнецова', 'e.kuznetsova@college.edu', 'CS-101'),
('Дмитрий', 'Смирнов', 'd.smirnov@college.edu', 'MATH-201')
ON CONFLICT (email) DO NOTHING;

INSERT INTO courses (title, description, credits) VALUES
('Базы данных', 'Основы PostgreSQL и SQL', 4),
('Математический анализ', 'Дифференциальное исчисление', 5),
('Веб-разработка', 'Современные фреймворки', 3)
ON CONFLICT DO NOTHING;
Часть 8: Запуск приложения
bash
# Собираем и запускаем контейнеры
docker-compose up --build -d

# Проверяем статус
docker-compose ps

# Смотрим логи
docker-compose logs -f web

# Тестируем API
curl http://localhost/
curl http://localhost/students
curl http://localhost/courses

# Работа с контейнерами
bash
# Просмотр запущенных контейнеров
docker ps

# Просмотр логов конкретного контейнера
docker logs college_web

# Выполнение команд в контейнере
docker exec -it college_web bash

# Остановка приложения
docker-compose down

# Остановка с удалением томов
docker-compose down -v

✅ Проверка работы
Тест API endpoints
bash
# Создаем нового студента
curl -X POST http://localhost/students \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Тест","last_name":"Студент","email":"test@college.edu","group_name":"TEST-001"}'

# Получаем список студентов
curl http://localhost/students

# Получаем список курсов
curl http://localhost/courses
Проверка базы данных
bash
# Подключаемся к базе данных в контейнере
docker exec -it college_db psql -U college_user -d college -c "SELECT * FROM students;"

🎓 Дополнительные задания

Добавьте Redis для кэширования

Настройте health checks для всех сервисов

Добавьте мониторинг с Prometheus

Создайте .env файл для конфигурации

Настройте сборку образа в Docker Hub

📊 Ожидаемые результаты

Работающее веб-приложение колледжа на FastAPI

База данных PostgreSQL в контейнере

Nginx в качестве reverse proxy

Сетевые взаимодействия между контейнерами

Сохранение данных в volumes