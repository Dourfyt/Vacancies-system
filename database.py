import sqlite3

def create_connection():
    """Создание подключения к базе данных SQLite."""
    connection = None
    try:
        connection = sqlite3.connect(DB_NAME)
        return connection
    except sqlite3.Error as e:
        print(f"Ошибка подключения: {e}")
    return connection

def create_tables():
    """Создает таблицы пользователей, вакансий и откликов, если их нет."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            salary REAL NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vacancy_id INTEGER,
            user TEXT,
            contact_info TEXT,
            cover_letter TEXT,
            FOREIGN KEY (vacancy_id) REFERENCES vacancies(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
        """
    )

    conn.commit()
    conn.close()