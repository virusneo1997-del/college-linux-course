# Lesson 02 — Users & Permissions  
Отчёт студента по выполнению задания

---

## 1. Создание пользователя и группы

### Создал пользователя:
bash
sudo useradd labuser
### Создал группу:

bash
sudo groupadd labgroup

### Добавил пользователя в группу:

bash
sudo usermod -aG labgroup labuser

Проверка:

bash
id labuser

---

## 2. Создание директорий с разными правами

### Создал папку:

bash
mkdir /tmp/lesson02

### Установил владельца:

bash
sudo chown labuser:labgroup /tmp/lesson02

### Установил права 770:

bash
sudo chmod 770 /tmp/lesson02

Проверка:

bash
ls -ld /tmp/lesson02

---

## 3. Sticky-bit и Setgid

### Включил setgid на директорию:

bash
sudo chmod g+s /tmp/lesson02

### Проверка:

bash
ls -ld /tmp/lesson02

---

## 4. Создание файлов с разными правами

bash
sudo -u labuser touch /tmp/lesson02/file1.txt
sudo chmod 640 /tmp/lesson02/file1.txt

Проверка:

bash
ls -l /tmp/lesson02/file1.txt

---

## 5. Ответы на вопросы

### Что такое UID/GID?

UID — уникальный идентификатор пользователя.
GID — идентификатор группы.

### Что делает команда `chmod 770`?

* владелец: все права
* группа: все права
* остальные: нет прав

### Для чего нужен setgid на директории?

Чтобы новые файлы наследовали группу директории.

---