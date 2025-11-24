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
