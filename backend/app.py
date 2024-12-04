from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG
from flasgger import Swagger
from flask_cors import CORS
import base64
from io import BytesIO

# Инициализация Flask-приложения
app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# Функция для подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# Эндпоинт для получения персональных данных пользователя
@app.route('/users/get/<int:user_id>/personal', methods=['GET'])
def get_user_personal(user_id):
    """
    Get personal details of a user
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user
    responses:
      200:
        description: A user's personal details
        schema:
          id: UserPersonal
          properties:
            id:
              type: integer
              description: The user's ID
            login:
              type: string
              description: The user's login
            name:
              type: string
              description: The user's first name
            patronymic:
              type: string
              description: The user's patronymic
            surname:
              type: string
              description: The user's surname
            birthdate:
              type: string
              description: The user's birthdate
            tg_nickname:
              type: string
              description: The user's Telegram nickname
            phone:
              type: string
              description: The user's phone number
      404:
        description: User not found
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
        SELECT id, login, password, name, patronymic, surname, birthdate, tg_nickname, phone
        FROM users
        WHERE id = %s;
        """
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(user)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Эндпоинт для получения должностей в департаменте по user_id
@app.route('/users/get/<int:user_id>/job_info', methods=['GET'])
def get_user_job_titles_and_departments(user_id):
    """
    Get job titles and departments for a user
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user
    responses:
      200:
        description: A list of job titles and departments
        schema:
          id: JobInfo
          properties:
            user_id:
              type: integer
              description: The user's ID
            job_titles:
              type: array
              items:
                properties:
                  title:
                    type: string
                    description: The job title
                  department:
                    type: string
                    description: The department name
                  role:
                    type: string
                    description: The role name
      404:
        description: No job titles or departments found
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT jt.title, d.department_name, r.role_name
        FROM job_titles jt
        JOIN user_job_titles ujt ON jt.id = ujt.job_title_id
        JOIN user_departments ud ON ujt.user_id = ud.user_id
        JOIN departments d ON ud.department_id = d.id
        JOIN user_roles ur  ON ud.user_id  = ur.user_id 
        join roles r on ur.role_id = r.id
        WHERE ujt.user_id = %s;
        """
        cursor.execute(query, (user_id,))
        job_details = cursor.fetchall()

        if not job_details:
            return jsonify({"message": "No job titles or departments found for this user"}), 404

        result = {
            "user_id": user_id,
            "job_titles": [{"title": job[0], "department": job[1], "role": job[2]} for job in job_details]
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Эндпоинт для получения ncoins и рейтинга пользователя по user_id
@app.route('/users/get/<int:user_id>/details', methods=['GET'])
def get_user_details(user_id):
    """
    Get user details like ncoins, rating, and others
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user
    responses:
      200:
        description: A user's details (ncoins, rating, etc.)
        schema:
          id: UserDetails
          properties:
            user_id:
              type: integer
              description: The user's ID
            ncoins:
              type: integer
              description: The user's ncoins
            rating:
              type: integer
              description: The user's rating
            thanks_count:
              type: integer
              description: The number of times the user has been thanked
            interests:
              type: string
              description: The user's interests
      404:
        description: No details found for this user
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT ud.ncoins, ud.rating, ud.thanks_count, ud.interests
        FROM user_details ud
        WHERE ud.user_id = %s;
        """
        cursor.execute(query, (user_id,))
        details = cursor.fetchone()

        if not details:
            return jsonify({"message": "No details found for this user"}), 404

        return jsonify({
            "user_id": user_id,
            "ncoins": details[0],
            "rating": details[1],
            "thanks_count": details[2],
            "interests": details[3]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Эндпоинт для получения фото пользователя по user_id
@app.route('/users/get/<int:user_id>/photo', methods=['GET'])
def get_user_photo(user_id):
    """
    Get user's photo in base64
    ---
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user
    responses:
      200:
        description: The user's photo in base64
        schema:
          id: UserPhoto
          properties:
            user_id:
              type: integer
              description: The user's ID
            photo:
              type: string
              description: The user's photo in base64 encoding
      404:
        description: No photo found for this user
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT up.photo
        FROM user_photos up
        WHERE up.user_id = %s;
        """
        cursor.execute(query, (user_id,))
        photo = cursor.fetchone()

        if not photo or photo[0] is None:
            photo_value = ''
        else:
            photo_value = photo[0].decode('utf-8')

        return jsonify({
            "user_id": user_id,
            "photo": photo_value
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Эндпоинт для логина
@app.route('/login', methods=['PUT'])
def login():
    """
    Login endpoint
    ---
    parameters:
      - name: login
        in: body
        required: true
        schema:
          type: object
          properties:
            login:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login success
        schema:
          type: object
          properties:
            login_status:
              type: string
              example: success
      401:
        description: Invalid login or password
        schema:
          type: object
          properties:
            login_status:
              type: string
              example: failed
      400:
        description: Missing login or password
        schema:
          type: object
          properties:
            error:
              type: string
              example: Login and password are required
    """
    data = request.get_json()
    login_input = data.get('login')
    password_input = data.get('password')

    if not login_input or not password_input:
        return jsonify({"error": "Login and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        SELECT id FROM users
        WHERE login = %s AND password = %s;
        """
        cursor.execute(query, (login_input, password_input))
        user = cursor.fetchone()

        if user:
            return jsonify({"login_status": "success"}), 200
        else:
            return jsonify({"login_status": "failed"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/users/upload/<int:user_id>/photo', methods=['POST'])
def upload_photo(user_id):
    """
    Upload user photo in base64 format and store it in the database.
    ---
    parameters:
      - name: photo
        in: body
        required: true
        schema:
          type: object
          properties:
            photo:
              type: string
              description: Base64 encoded photo
    responses:
      200:
        description: Photo uploaded successfully
      400:
        description: Missing or invalid photo
      500:
        description: Server error
    """
    data = request.get_json()

    # Получаем фото в формате base64
    photo_base64 = data.get('photo')

    if not photo_base64:
        return jsonify({"error": "Photo is required"}), 400

    try:
        # Декодируем фото из Base64
        photo_data = base64.b64decode(photo_base64)

        # Подключаемся к базе данных
        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Записываем фото в базу данных
        cursor.execute("""
            UPDATE users
            SET photo = %s
            WHERE id = %s;
        """, (photo_data, user_id))

        conn.commit()

        return jsonify({"message": "Photo uploaded successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# Запуск сервера
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
