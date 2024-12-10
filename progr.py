import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QMessageBox, \
    QLabel, QComboBox, QListWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Онлайн система обучения")  # установка заголовка окна
        self.resize(600, 400)  # установка размера окна

        # создание центрального виджета и установка его для главного окна
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()  # создание вертикального layout
        self.create_navigation_buttons()  # кнопки навигации
        self.create_auth_fields()  # поля для авторизации
        self.create_registration_fields()  # поля для регистрации
        self.central_widget.setLayout(self.layout)  # для центрального виджета
        self.search_window = SearchWindow()  # создание окна поиска
        self.hide_fields()  # скрыть все поля при старте
        self.initialize_database()  # инициализация базы данных

    def create_navigation_buttons(self):
        # кнопка для перехода к форме авторизации
        self.show_login_button = QPushButton("Авторизуйтесь")
        self.show_login_button.clicked.connect(self.show_login_fields)  # подключение к методу
        self.layout.addWidget(self.show_login_button)  # добавление кнопки в layout

        # кнопка для перехода к форме регистрации
        self.show_register_button = QPushButton("Зарегистрируйтесь")
        self.show_register_button.clicked.connect(self.show_registration_fields)  # подключение к методу
        self.layout.addWidget(self.show_register_button)  # добавление кнопки в layout

    def create_auth_fields(self):
        # подпись для авторизации
        self.login_label = QLabel("Авторизация", self)
        self.layout.addWidget(self.login_label)

        # поле для ввода электронной почты
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Введите email для входа")  # подсказка для ввода
        self.layout.addWidget(self.email_input)

        # поле для ввода пароля
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль для входа")  # подсказка для ввода
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  # скрыть ввод пароля
        self.layout.addWidget(self.password_input)

        # кнопка для входа
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login_user)  # подключение к методу
        self.layout.addWidget(self.login_button)

    def create_registration_fields(self):
        # подпись для регистрации
        self.register_label = QLabel("Регистрация", self)
        self.layout.addWidget(self.register_label)

        # создание полей ввода для имени, фамилии и email
        self.name_input, self.surname_input, self.register_email_input = self.create_input_fields(
            ["Введите имя", "Введите фамилию", "Введите email"], False)
        # создание поля ввода для пароля
        self.register_password_input = self.create_input_fields(["Введите пароль"], True)[0]

        # кнопка для регистрации
        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.register_user)  # подключение к методу
        self.layout.addWidget(self.register_button)

    def create_input_fields(self, placeholders, password=False):
        inputs = []  # список для хранения созданных полей ввода
        for placeholder in placeholders:
            input_field = QLineEdit(self)  # создание поля ввода
            input_field.setPlaceholderText(placeholder)  # установка подсказки
            if password:
                input_field.setEchoMode(QLineEdit.EchoMode.Password)  # установка скрытого ввода для пароля
            self.layout.addWidget(input_field)  # добавление поля
            inputs.append(input_field)  # добавление поля в список
        return inputs  # возврат списка полей ввода

    def initialize_database(self):
        # SQL-запросы для создания таблиц в базе данных
        tables = [
            '''CREATE TABLE IF NOT EXISTS Пользователь (ID INTEGER PRIMARY KEY AUTOINCREMENT, Имя TEXT NOT NULL, Фамилия TEXT NOT NULL, Email TEXT UNIQUE NOT NULL, Пароль TEXT NOT NULL, Роль TEXT CHECK(Роль IN ('студент', 'преподаватель', 'администратор')) NOT NULL, Дата_регистрации DATETIME DEFAULT CURRENT_TIMESTAMP);''',
            '''CREATE TABLE IF NOT EXISTS Курс (ID INTEGER PRIMARY KEY AUTOINCREMENT, Название TEXT NOT NULL, Описание TEXT, Дата_начала DATE, Дата_окончания DATE, Статус TEXT CHECK(Статус IN ('активный', 'завершенный')) NOT NULL, ID_преподавателя INTEGER, FOREIGN KEY (ID_преподавателя) REFERENCES Пользователь(ID));''',
            '''CREATE TABLE IF NOT EXISTS Модуль (ID INTEGER PRIMARY KEY AUTOINCREMENT, Название TEXT NOT NULL, Описание TEXT, Порядок INTEGER NOT NULL, ID_курса INTEGER, FOREIGN KEY (ID_курса) REFERENCES Курс(ID));''',
            '''CREATE TABLE IF NOT EXISTS Урок (ID INTEGER PRIMARY KEY AUTOINCREMENT, Название TEXT NOT NULL, Описание TEXT, Дата_создания DATETIME DEFAULT CURRENT_TIMESTAMP, ID_модуля INTEGER, Тип TEXT CHECK(Тип IN ('видео', 'текст', 'тест')) NOT NULL, FOREIGN KEY (ID_модуля) REFERENCES Модуль(ID));''',
            '''CREATE TABLE IF NOT EXISTS Задание (ID INTEGER PRIMARY KEY AUTOINCREMENT, Название TEXT NOT NULL, Описание TEXT, Срок_выполнения DATE, ID_урока INTEGER, Статус TEXT CHECK(Статус IN ('выполнено', 'не выполнено')) NOT NULL, FOREIGN KEY (ID_урока) REFERENCES Урок(ID));''',
            '''CREATE TABLE IF NOT EXISTS Тест (ID INTEGER PRIMARY KEY AUTOINCREMENT, Название TEXT NOT NULL, Описание TEXT, Дата_создания DATETIME DEFAULT CURRENT_TIMESTAMP, ID_урока INTEGER, Количество_вопросов INTEGER, FOREIGN KEY (ID_урока) REFERENCES Урок(ID));'''
        ]
        try:
            # подключение к базе данных и создание таблиц
            with sqlite3.connect("OnlineLearningSystem.db") as connection:
                cursor = connection.cursor()
                for table in tables:
                    cursor.execute(table)  # выполнение SQL-запроса
                connection.commit()  # сохранение изменений
        except Exception as e:
            # обработка ошибок при инициализации базы данных
            QMessageBox.warning(self, "Ошибка", f"Не удалось инициализировать базу данных: {e}")

    def hide_fields(self):
        # скрытие всех полей ввода и кнопок
        for widget in [self.login_label, self.email_input, self.password_input, self.login_button,
                       self.register_label, self.name_input, self.surname_input, self.register_email_input,
                       self.register_password_input, self.register_button]:
            widget.setVisible(False)

    def show_login_fields(self):
        self.hide_fields()  # скрыть все поля
        # показать поля для авторизации
        for widget in [self.login_label, self.email_input, self.password_input, self.login_button]:
            widget.setVisible(True)

    def show_registration_fields(self):
        self.hide_fields()  # скрыть все поля
        # показать поля для регистрации
        for widget in [self.register_label, self.name_input, self.surname_input, self.register_email_input,
                       self.register_password_input, self.register_button]:
            widget.setVisible(True)

    def login_user(self):
        email = self.email_input.text()  # получение введенного email
        password = self.password_input.text()  # получение введенного пароля
        if not email or not password:
            # проверка на заполненность полей
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return
        self.authenticate_user(email, password)  # аутентификация пользователя

    def register_user(self):
        # получение введенных данных для регистрации
        name, surname, email, password = [input_field.text() for input_field in
                                          [self.name_input, self.surname_input, self.register_email_input,
                                           self.register_password_input]]
        if not all([name, surname, email, password]):
            # проверка на заполненность полей
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return
        self.add_user_to_database(name, surname, email, password)  # добавление пользователя в базу данных

    def authenticate_user(self, email, password):
        try:
            # подключение к базе данных для аутентификации
            with sqlite3.connect("OnlineLearningSystem.db") as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT * FROM Пользователь WHERE Email = ? AND Пароль = ?', (email, password))
                user = cursor.fetchone()  # получение данных пользователя
            if user:
                QMessageBox.information(self, "Успех", "Вход выполнен успешно!")  # успешный вход
                self.search_window.populate_courses()  # заполнение курсов перед показом окна поиска
                self.search_window.show()  # показать окно поиска сразу после авторизации
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный email или пароль.")  # ошибка входа
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {e}")  # обработка ошибок

    def add_user_to_database(self, name, surname, email, password):
        try:
            # подключение к базе данных для добавления пользователя
            with sqlite3.connect("OnlineLearningSystem.db") as connection:
                cursor = connection.cursor()
                cursor.execute('INSERT INTO Пользователь (Имя, Фамилия, Email, Пароль, Роль) VALUES (?, ?, ?, ?, ?)',
                               (name, surname, email, password, 'студент'))  # добавление пользователя
                connection.commit()  # сохранение изменений
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")  # успешная регистрация
            self.clear_registration_inputs()  # очистка полей регистрации
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким email уже существует.")  # ошибка уникальности
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {e}")  # обработка ошибок

    def clear_registration_inputs(self):
        # очистка полей ввода для регистрации
        for input_field in [self.name_input, self.surname_input, self.register_email_input,
                            self.register_password_input]:
            input_field.clear()


class SearchWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Поиск")  # установка заголовка окна поиска
        self.resize(500, 400)  # установка размера окна

        self.layout = QVBoxLayout()  # создание вертикального layout
        self.create_search_fields()  # создание полей для поиска
        self.setLayout(self.layout)  # установка layout для окна поиска

    def create_search_fields(self):
        # комбобокс для выбора курса
        self.course_combo = QComboBox(self)
        self.course_combo.setPlaceholderText("Выберите курс")  # подсказка для выбора
        self.course_combo.currentIndexChanged.connect(self.populate_modules)  # рбновляем модули при выборе курса
        self.layout.addWidget(self.course_combo)

        # подпись для модулей
        self.module_label = QLabel("Модули:", self)
        self.layout.addWidget(self.module_label)

        # список для отображения модулей
        self.module_list = QListWidget(self)
        self.layout.addWidget(self.module_list)

        # подпись для уроков
        self.lesson_label = QLabel("Уроки:", self)
        self.layout.addWidget(self.lesson_label)

        # список для отображения уроков
        self.lesson_list = QListWidget(self)
        self.layout.addWidget(self.lesson_list)

        # подпись для заданий
        self.assignment_label = QLabel("Задания:", self)
        self.layout.addWidget(self.assignment_label)

        # список для отображения заданий
        self.assignment_list = QListWidget(self)
        self.layout.addWidget(self.assignment_list)

        # кнопка для выполнения поиска
        self.search_button = QPushButton("Искать")
        self.search_button.clicked.connect(self.perform_search)  # подключение к методу
        self.layout.addWidget(self.search_button)

        # кнопка для возврата
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.close)  # закрытие окна
        self.layout.addWidget(self.back_button)

    def populate_courses(self):
        self.course_combo.clear()  # очищаем предыдущие значения
        try:
            # подключение к базе данных для получения курсов
            with sqlite3.connect("OnlineLearningSystem.db") as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT Название FROM Курс')  # получение названий курсов
                courses = cursor.fetchall()
                for course in courses:
                    self.course_combo.addItem(course[0])  # добавление курса в комбобокс
            self.populate_modules()  # обновляем модули сразу после загрузки курсов
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить курсы: {e}")  # Обработка ошибок

    def populate_modules(self):
        self.module_list.clear()  # очищаем предыдущие значения
        selected_course = self.course_combo.currentText()  # получение выбранного курса
        if selected_course:
            try:
                # подключение к базе данных для получения модулей выбранного курса
                with sqlite3.connect("OnlineLearningSystem.db") as connection:
                    cursor = connection.cursor()
                    cursor.execute('SELECT ID FROM Курс WHERE Название = ?', (selected_course,))
                    course_id = cursor.fetchone()  # получение ID курса
                    if course_id:
                        cursor.execute('SELECT Название FROM Модуль WHERE ID_курса = ?', (course_id[0],))
                        modules = cursor.fetchall()  # получение названий модулей
                        for module in modules:
                            self.module_list.addItem(module[0])  # добавление модуля в список
                        self.module_list.itemClicked.connect(self.populate_lessons)  # Обновляем уроки при выборе модуля
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить модули: {e}")  # Обработка ошибок

    def populate_lessons(self):
        self.lesson_list.clear()  # пчищаем предыдущие значения
        selected_module = self.module_list.currentItem()  # получение выбранного модуля
        if selected_module:
            module_name = selected_module.text()  # получение названия модуля
            try:
                # подключение к базе данных для получения уроков выбранного модуля
                with sqlite3.connect("OnlineLearningSystem.db") as connection:
                    cursor = connection.cursor()
                    cursor.execute('SELECT ID FROM Модуль WHERE Название = ?', (module_name,))
                    module_id = cursor.fetchone()  # получение ID модуля
                    if module_id:
                        cursor.execute('SELECT Название FROM Урок WHERE ID_модуля = ?', (module_id[0],))
                        lessons = cursor.fetchall()  # получение названий уроков
                        for lesson in lessons:
                            self.lesson_list.addItem(lesson[0])  # добавление урока в список
                        self.lesson_list.itemClicked.connect(self.populate_assignments)  # обновляем задания при выборе урока
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить уроки: {e}")  # обработка ошибок

    def populate_assignments(self):
        self.assignment_list.clear()  # очищаем предыдущие значения
        selected_lesson = self.lesson_list.currentItem()  # получение выбранного урока
        if selected_lesson:
            lesson_name = selected_lesson.text()  # получение названия урока
            try:
                # подключение к базе данных для получения заданий выбранного урока
                with sqlite3.connect("OnlineLearningSystem.db") as connection:
                    cursor = connection.cursor()
                    cursor.execute('SELECT ID FROM Урок WHERE Название = ?', (lesson_name,))
                    lesson_id = cursor.fetchone()  # получение ID урока
                    if lesson_id:
                        cursor.execute('SELECT Название FROM Задание WHERE ID_урока = ?', (lesson_id[0],))
                        assignments = cursor.fetchall()  # получение названий заданий
                        for assignment in assignments:
                            self.assignment_list.addItem(assignment[0])  # добавление задания в список
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить задания: {e}")  # Обработка ошибок

    def perform_search(self):
        # получение выбранных значений для поиска
        selected_course = self.course_combo.currentText()
        module_name = self.module_list.currentItem().text() if self.module_list.currentItem() else ""
        lesson_name = self.lesson_list.currentItem().text() if self.lesson_list.currentItem() else ""
        assignment_name = self.assignment_list.currentItem().text() if self.assignment_list.currentItem() else ""

        results = []  # список для хранения результатов поиска

        try:
            # подключение к базе данных для выполнения поиска
            with sqlite3.connect("OnlineLearningSystem.db") as connection:
                cursor = connection.cursor()

                if selected_course:
                    cursor.execute('SELECT * FROM Курс WHERE Название = ?', (selected_course,))
                    results.extend(cursor.fetchall())  # добавление результатов поиска курсов
                if module_name:
                    cursor.execute('SELECT * FROM Модуль WHERE Название LIKE ?', ('%' + module_name + '%',))
                    results.extend(cursor.fetchall())  # добавление результатов поиска модулей
                if lesson_name:
                    cursor.execute('SELECT * FROM Урок WHERE Название LIKE ?', ('%' + lesson_name + '%',))
                    results.extend(cursor.fetchall())  # добавление результатов поиска уроков
                if assignment_name:
                    cursor.execute('SELECT * FROM Задание WHERE Название LIKE ?', ('%' + assignment_name + '%',))
                    results.extend(cursor.fetchall())  # добавление результатов поиска заданий

            if results:
                QMessageBox.information(self, "Результаты поиска", f"Найдено {len(results)} результатов.")  # отображение результатов
            else:
                QMessageBox.information(self, "Результаты поиска", "Ничего не найдено.")  # Сообщение о том, что ничего не найдено
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {e}")  # обработка ошибок

if __name__ == "__main__":
    app = QApplication(sys.argv)  # создание приложения
    window = MainWindow()  # создание главного окна
    window.show()  # отображение главного окна
    sys.exit(app.exec())  # запуск основного цикла приложения
