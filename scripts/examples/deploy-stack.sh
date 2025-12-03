#!/bin/bash

# Скрипт развертывания стека приложения колледжа

set -e

echo "🚀 Starting College App Deployment..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

# Создание сети если не существует
if ! docker network ls | grep -q "college_network"; then
    echo "🌐 Creating college_network..."
    docker network create college_network
fi

# Запуск/перезапуск сервисов
echo "📦 Building and starting services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Ожидание запуска сервисов
echo "⏳ Waiting for services to start..."
sleep 30

# Проверка здоровья сервисов
echo "🔍 Checking services health..."

# Проверка базы данных
if docker exec college_db pg_isready -U college_user -d college; then
    echo "✅ Database is healthy"
else
    echo "❌ Database health check failed"
    exit 1
fi

# Проверка веб-приложения
if curl -f http://localhost/health &> /dev/null; then
    echo "✅ Web application is healthy"
else
    echo "❌ Web application health check failed"
    exit 1
fi

# Проверка nginx
if curl -f http://localhost &> /dev/null; then
    echo "✅ Nginx is healthy"
else
    echo "❌ Nginx health check failed"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo "📊 Application is available at: http://localhost"
echo "👥 Students API: http://localhost/students"
echo "📚 Courses API: http://localhost/courses"

# Показать информацию о контейнерах
echo ""
echo "📋 Running containers:"
docker-compose ps