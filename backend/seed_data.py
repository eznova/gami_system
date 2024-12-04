import psycopg2
from faker import Faker
from psycopg2.extras import execute_values
import random

# Импорт конфигурации подключения из config.py
from config import DB_CONFIG

# Инициализация Faker
fake = Faker()

# Подключение к базе данных
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Генерация тестовых данных для пользователей
def generate_test_user_data():
    return {
        "login": fake.user_name(),
        "password": fake.password(),
        "name": fake.first_name(),
        "patronymic": fake.first_name(),
        "surname": fake.last_name(),
        "birthdate": fake.date_of_birth(minimum_age=20, maximum_age=60),
        "tg_nickname": f"@{fake.user_name()}",
        "phone": fake.phone_number(),
        "interests": fake.sentence(),
        "ncoins": random.randint(0, 500),
        "rating": round(random.uniform(0, 5), 2),
        "thanks_count": random.randint(0, 100),
        "photo": None  # Можно указать путь к изображению, если нужно
    }

# Вставка данных в таблицы roles, departments и job_titles
def insert_initial_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Вставка ролей
        roles = ["admin", "editor", "viewer"]
        cursor.executemany("INSERT INTO roles (role_name) VALUES (%s) ON CONFLICT DO NOTHING;", [(role,) for role in roles])

        # Вставка департаментов
        departments = ["IT", "HR", "Marketing"]
        cursor.executemany("INSERT INTO departments (department_name) VALUES (%s) ON CONFLICT DO NOTHING;", [(dept,) for dept in departments])

        # Вставка должностей
        job_titles = ["Software Engineer", "HR Manager", "Marketing Specialist"]
        cursor.executemany("INSERT INTO job_titles (title) VALUES (%s) ON CONFLICT DO NOTHING;", [(title,) for title in job_titles])

        # Фиксируем изменения
        conn.commit()
        print("Данные для ролей, департаментов и должностей успешно добавлены.")
    except Exception as e:
        print(f"Ошибка при вставке начальных данных: {e}")
        conn.rollback()
    finally:
        cursor.close()

# Вставка данных в таблицу users и связанные таблицы
def seed_users_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Генерируем и вставляем 3 пользователя
        users = [generate_test_user_data() for _ in range(3)]
        user_values = [
            (
                user["login"], user["password"], user["name"], user["patronymic"], user["surname"],
                user["birthdate"], user["tg_nickname"], user["phone"]
            )
            for user in users
        ]

        # Вставляем пользователей в таблицу users
        query = """
        INSERT INTO users (login, password, name, patronymic, surname, birthdate, tg_nickname, phone) 
        VALUES %s RETURNING id;
        """
        cursor = conn.cursor()
        execute_values(cursor, query, user_values)
        user_ids = [row[0] for row in cursor.fetchall()]

        # Вставка в таблицу user_details
        details_values = [
            (
                user_ids[i], users[i]["interests"], users[i]["ncoins"], users[i]["rating"],
                users[i]["thanks_count"]
            )
            for i in range(3)
        ]
        cursor.executemany("""
        INSERT INTO user_details (user_id, interests, ncoins, rating, thanks_count) 
        VALUES (%s, %s, %s, %s, %s);
        """, details_values)

        # Вставка в таблицу user_photos (если нужно вставить фото)
        photos_values = [(user_ids[i], None) for i in range(3)]  # Здесь можно заменить None на данные фото
        cursor.executemany("""
        INSERT INTO user_photos (user_id, photo) 
        VALUES (%s, %s);
        """, photos_values)

        # Вставка связей user_roles
        role_ids = [1, 2, 3]  # id для ролей (admin, editor, viewer)
        role_values = [(user_ids[i], role_ids[i % 3]) for i in range(3)]
        cursor.executemany("""
        INSERT INTO user_roles (user_id, role_id) 
        VALUES (%s, %s);
        """, role_values)

        # Вставка связей user_departments
        department_ids = [1, 2, 3]  # id для департаментов (IT, HR, Marketing)
        department_values = [(user_ids[i], department_ids[i % 3]) for i in range(3)]
        cursor.executemany("""
        INSERT INTO user_departments (user_id, department_id) 
        VALUES (%s, %s);
        """, department_values)

        # Вставка связей user_job_titles
        job_title_ids = [1, 2, 3]  # id для должностей
        job_title_values = [(user_ids[i], job_title_ids[i % 3]) for i in range(3)]
        cursor.executemany("""
        INSERT INTO user_job_titles (user_id, job_title_id) 
        VALUES (%s, %s);
        """, job_title_values)

        # Фиксируем изменения
        conn.commit()
        print("Тестовые данные успешно добавлены в таблицы users и связанные таблицы.")
    except Exception as e:
        print(f"Ошибка при добавлении тестовых данных: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Основной блок выполнения
if __name__ == "__main__":
    insert_initial_data()  # Вставка начальных данных (роли, департаменты, должности)
    seed_users_data()      # Вставка пользователей и связанных данных
