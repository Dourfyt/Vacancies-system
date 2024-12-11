import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,QDialog, QPushButton, QVBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, QHBoxLayout, QHeaderView
)
from database import create_connection,create_tables

create_tables()

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.resize(300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поля для логина и пароля
        self.login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Кнопки авторизации и регистрации
        self.login_button = QPushButton("Войти")
        self.register_button = QPushButton("Зарегистрироваться")

        # Подключение кнопок к функциям
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

        # Добавление элементов на форму
        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        """Авторизация пользователя."""
        login = self.login_input.text()
        password = self.password_input.text()

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM users WHERE login = ? AND password = ?", (login, password)
        )
        user = cursor.fetchone()

        if user:
            role = user[0]
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {login}!")
            self.open_main_window(role, login)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

        conn.close()

    def register(self):
        """Регистрация нового пользователя."""
        login = self.login_input.text()
        password = self.password_input.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()



        role = "operator" if password == "123" else "user"

        try:
            cursor.execute(
                "INSERT INTO users (login, password, role) VALUES (?, ?, ?)",
                (login, password, role),
            )
            conn.commit()
            QMessageBox.information(
                self, "Успех", f"Регистрация успешна! Ваша роль: {role}."
            )
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует!")
        finally:
            conn.close()

    def open_main_window(self, role, username):
        """Открыть главное окно с учетом роли пользователя."""
        self.hide()
        if role == "operator":
            self.main_window = OperatorWindow()
        else:
            self.main_window = UserWindow(username)
        self.main_window.show()


class OperatorWindow(QWidget):
    """Главное окно оператора."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Оператор")
        self.resize(1200, 1000)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поля для добавления вакансий
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Название вакансии")
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Описание вакансии")
        self.salary_input = QLineEdit()
        self.salary_input.setPlaceholderText("Зарплата")

        self.add_vacancy_button = QPushButton("Добавить вакансию")
        self.add_vacancy_button.clicked.connect(self.add_vacancy)

        # Таблица для отображения вакансий
        self.vacancy_table = QTableWidget()
        self.vacancy_table.setColumnCount(4)
        self.vacancy_table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Зарплата"])
        self.vacancy_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vacancy_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.vacancy_table.itemSelectionChanged.connect(self.load_responses)
        self.load_vacancies()

        # Кнопка удаления вакансий
        self.delete_vacancy_button = QPushButton("Удалить вакансию")
        self.delete_vacancy_button.clicked.connect(self.delete_vacancy)

        # Таблица для отображения откликов
        self.response_table = QTableWidget()
        self.response_table.setColumnCount(3)
        self.response_table.setHorizontalHeaderLabels(["Пользователь", "Контакты", "Сопроводительное письмо"])
        self.response_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.response_table.itemSelectionChanged.connect(self.show_cover_letter_button_state)

        # Кнопка для просмотра письма
        self.show_letter_button = QPushButton("Посмотреть письмо")
        self.show_letter_button.setEnabled(False)
        self.show_letter_button.clicked.connect(self.show_cover_letter)


        self.report_button = QPushButton("Посмотреть отчет")
        self.report_button.clicked.connect(self.show_report)

        layout.addWidget(self.title_input)
        layout.addWidget(self.description_input)
        layout.addWidget(self.salary_input)
        layout.addWidget(self.add_vacancy_button)
        layout.addWidget(self.vacancy_table)
        layout.addWidget(self.delete_vacancy_button)
        layout.addWidget(QLabel("Отклики на выбранную вакансию:"))
        layout.addWidget(self.response_table)
        layout.addWidget(self.show_letter_button)
        layout.addWidget(self.report_button)

        self.setLayout(layout)

    def load_vacancies(self):
        """Загрузка вакансий из базы данных и отображение в таблице."""
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vacancies")
        vacancies = cursor.fetchall()
        conn.close()

        self.vacancy_table.setRowCount(0)  # Очистка таблицы

        for row_number, row_data in enumerate(vacancies):
            self.vacancy_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.vacancy_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def load_responses(self):
        """Загрузка откликов на выбранную вакансию."""
        selected_row = self.vacancy_table.currentRow()
        if selected_row == -1:
            return

        vacancy_id = self.vacancy_table.item(selected_row, 0).text()

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user, contact_info, cover_letter FROM responses WHERE vacancy_id = ?",
            (vacancy_id,),
        )
        responses = cursor.fetchall()
        print(vacancy_id)
        print(responses)
        conn.close()

        self.response_table.setRowCount(0)  # Очистка таблицы откликов

        for row_number, row_data in enumerate(responses):
            self.response_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.response_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        self.show_letter_button.setEnabled(False)

    def show_cover_letter_button_state(self):
        """Включение кнопки просмотра письма, если отклик выбран."""
        selected_row = self.response_table.currentRow()
        self.show_letter_button.setEnabled(selected_row != -1)

    def show_cover_letter(self):
        """Отображение сопроводительного письма в отдельном окне."""
        selected_row = self.response_table.currentRow()
        if selected_row == -1:
            return

        cover_letter = self.response_table.item(selected_row, 2).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Сопроводительное письмо")
        dialog.resize(500, 400)

        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(cover_letter)
        layout.addWidget(text_edit)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec()

    def add_vacancy(self):
        """Добавление новой вакансии в базу данных."""
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        salary = self.salary_input.text()

        if not title or not description or not salary:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        try:
            salary = float(salary)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Зарплата должна быть числом!")
            return

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vacancies (title, description, salary) VALUES (?, ?, ?)",
            (title, description, salary),
        )
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Успех", "Вакансия добавлена!")
        self.load_vacancies()

    def delete_vacancy(self):
        """Удаление выбранной вакансии из базы данных."""
        selected_row = self.vacancy_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите вакансию для удаления!")
            return

        vacancy_id = self.vacancy_table.item(selected_row, 0).text()

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vacancies WHERE id = ?", (vacancy_id,))
        cursor.execute("DELETE FROM responses WHERE vacancy_id = ?", (vacancy_id,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Успех", "Вакансия удалена вместе с откликами!")
        self.load_vacancies()
        self.response_table.setRowCount(0)  # Очистить отклики

    def show_report(self):
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        # SQL-запрос для получения списка вакансий с количеством откликов
        cursor.execute(
            """
            SELECT v.title, COUNT(r.id) AS response_count
            FROM vacancies v
            LEFT JOIN responses r ON v.id = r.vacancy_id
            GROUP BY v.id
            ORDER BY response_count DESC
            """
        )
        report_data = cursor.fetchall()
        conn.close()

        # Если данных нет, сообщаем об этом
        if not report_data:
            QMessageBox.information(self, "Отчет", "На данный момент вакансий или откликов нет.")
            return

        # Формируем текст отчета
        report_text = "Отчет о вакансиях и откликах:\n\n"
        for vacancy, response_count in report_data:
            report_text += f"- {vacancy}: {response_count} откликов\n"

        # Отображаем отчет в модальном окне
        QMessageBox.information(self, "Отчет", report_text)

class UserWindow(QWidget):
    """Главное окно пользователя."""

    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Пользователь")
        self.resize(1200, 1000)
        self.init_ui()
        self.username = username

    def init_ui(self):
        layout = QVBoxLayout()

        # Таблица для отображения вакансий
        self.vacancy_table = QTableWidget()
        self.vacancy_table.setColumnCount(4)
        self.vacancy_table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Зарплата"])
        self.vacancy_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vacancy_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.load_vacancies()

        # Поля для отклика
        self.contact_info_input = QLineEdit()
        self.contact_info_input.setPlaceholderText("Контактная информация")
        self.cover_letter_input = QTextEdit()
        self.cover_letter_input.setPlaceholderText("Сопроводительное письмо")

        # Кнопка для отправки отклика
        self.submit_response_button = QPushButton("Оставить отклик")
        self.submit_response_button.clicked.connect(self.submit_response)

        self.responses_button = QPushButton("Посмотреть мои отклики")
        self.responses_button.clicked.connect(self.show_responses)

        layout.addWidget(self.vacancy_table)
        layout.addWidget(QLabel("Контактная информация:"))
        layout.addWidget(self.contact_info_input)
        layout.addWidget(QLabel("Сопроводительное письмо:"))
        layout.addWidget(self.cover_letter_input)
        layout.addWidget(self.submit_response_button)
        layout.addWidget(self.responses_button)

        self.setLayout(layout)

    def load_vacancies(self):
        """Загрузка вакансий из базы данных и отображение в таблице."""
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, description, salary FROM vacancies")
        vacancies = cursor.fetchall()
        conn.close()

        self.vacancy_table.setRowCount(0)  # Очистка таблицы

        for row_number, row_data in enumerate(vacancies):
            self.vacancy_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.vacancy_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def submit_response(self):
        """Отправка отклика на выбранную вакансию."""
        selected_row = self.vacancy_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите вакансию для отклика!")
            return

        vacancy_id = self.vacancy_table.item(selected_row, 0).text()
        contact_info = self.contact_info_input.text()
        cover_letter = self.cover_letter_input.toPlainText()

        if not contact_info or not cover_letter:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO responses (vacancy_id, user, contact_info, cover_letter) VALUES (?, ?, ?, ?)",
            (vacancy_id,self.username , contact_info, cover_letter),
        )
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Успех", "Ваш отклик отправлен!")
        self.contact_info_input.clear()
        self.cover_letter_input.clear()
    
    def show_responses(self):
        # Получение откликов пользователя
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT vacancies.title, responses.contact_info, responses.cover_letter
            FROM responses
            JOIN vacancies ON responses.vacancy_id = vacancies.id
            WHERE user = ?
            """,
            (self.username,)
        )
        responses = cursor.fetchall()
        conn.close()

        # Создание модального окна для отображения откликов
        response_dialog = QDialog(self)
        response_dialog.setWindowTitle("Мои отклики")
        response_dialog.resize(600, 400)

        # Таблица для отображения данных
        table = QTableWidget(response_dialog)
        table.setRowCount(len(responses))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Вакансия", "Контакты", "Сопроводительное письмо"])

        for row, response in enumerate(responses):
            for col, value in enumerate(response):
                table.setItem(row, col, QTableWidgetItem(value))

        # Расположение таблицы в окне
        layout = QVBoxLayout(response_dialog)
        layout.addWidget(table)
        response_dialog.setLayout(layout)

        response_dialog.exec()

def apply_qss(app):
    qss = """
    QWidget {
        font-family: Arial, sans-serif;
        font-size: 14px;
        background-color: #f4f4f4;
        color: #333333;
    }

    QLabel {
        font-size: 16px;
        font-weight: bold;
    }

    QLineEdit {
        border: 1px solid #ccc;
        padding: 5px;
        border-radius: 3px;
        font-size: 14px;
    }

    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 5px;
    }

    QPushButton:hover {
        background-color: #45a049;
    }

    QPushButton:pressed {
        background-color: #3e8e41;
    }
    """
    app.setStyleSheet(qss)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_qss(app)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())
