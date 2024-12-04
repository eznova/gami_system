CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE job_titles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    patronymic VARCHAR(50),
    surname VARCHAR(50) NOT NULL,
    birthdate DATE,
    tg_nickname VARCHAR(50) UNIQUE,
    phone VARCHAR(20) UNIQUE
);

CREATE TABLE user_details (
    user_id INT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    interests TEXT,
    ncoins INT DEFAULT 0,
    rating INT DEFAULT 0,
    thanks_count INT DEFAULT 0,
);

CREATE TABLE user_photos (
    user_id INT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    photo BYTEA
);

CREATE TABLE user_roles (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    role_id INT REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE user_departments (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    department_id INT REFERENCES departments(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, department_id)
);

CREATE TABLE user_job_titles (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    job_title_id INT REFERENCES job_titles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, job_title_id)
);
