import streamlit as st
import json
import os
from streamlit_option_menu import option_menu
import g4f

# Путь к файлу для хранения данных пользователей
USER_DATA_FILE = "user_data.json"

# Функция для загрузки данных пользователей
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

# Функция для сохранения данных пользователей
def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Проверка пользователя
def authenticate(username, password, user_data):
    return username in user_data and user_data[username]["password"] == password

# Страница авторизации
def login_page():
    st.title("Авторизация")
    username = st.text_input("Имя пользователя")
    password = st.text_input("Пароль", type="password")
    login_button = st.button("Войти")

    user_data = load_user_data()

    if login_button:
        if authenticate(username, password, user_data):
            st.session_state["username"] = username
            st.success(f"Добро пожаловать, {username}!")
        else:
            st.error("Неправильное имя пользователя или пароль.")

# Страница регистрации
def register_page():
    st.title("Регистрация")
    username = st.text_input("Имя пользователя")
    password = st.text_input("Пароль", type="password")
    register_button = st.button("Зарегистрироваться")

    if register_button:
        user_data = load_user_data()
        if username in user_data:
            st.error("Такое имя пользователя уже существует.")
        else:
            user_data[username] = {"password": password, "projects": []}
            save_user_data(user_data)
            st.success("Регистрация успешна. Теперь вы можете войти.")

# Функция для получения ответа от модели GPT-3.5-turbo
def get_answer(request: str) -> str:
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=[{"role": "system", "content": "Ты – качественный и полезный ассистент, который отвечает только на русском языке."},
                  {"role": "user", "content": request}],
    )
    return response

# Личный кабинет пользователя
def user_dashboard(username):
    st.title(f"Личный кабинет: {username}")

    user_data = load_user_data()

    with st.form("project_form"):
        st.header("Информация о проекте")
        project_name = st.text_input("Название проекта")
        project_description = st.text_area("Описание проекта")

        st.header("Информация о людях")

        num_people = st.number_input("Количество людей", min_value=1, max_value=10, value=1, step=1, key="num_people")

        people_data = []
        for i in range(num_people):
            st.subheader(f"Человек {i + 1}")
            name = st.text_input(f"Имя человека {i + 1}", key=f"name_{i}")
            role = st.text_input(f"Роль человека {i + 1}", key=f"role_{i}")
            skills = st.text_area(f"Компетенции человека {i + 1}", key=f"skills_{i}")
            moral = st.text_area(f"Личные качества человека {i + 1}", key=f"moral{i}")
            people_data.append({"name": name, "role": role, "skills": skills, "moral": moral})

        request = st.text_area("Вставьте весь текст сюда", height=150)

        submitted = st.form_submit_button("Сохранить проект")
        if submitted:
            user_data[username]["projects"].append({
                "project_name": project_name,
                "project_description": project_description,
                "people_data": people_data,
                "request": request
            })
            save_user_data(user_data)
            st.success("Проект сохранен!")

# Страница с результатом для всех пользователей
def result_page():
    st.title("Результат")

    user_data = load_user_data()
    all_projects = []
    
    for user, details in user_data.items():
        for project in details["projects"]:
            project_info = f"Название проекта: {project['project_name']}. Описание проекта: {project['project_description']}.\n"
            people_info = " ".join([f"Человек {i + 1}: Имя: {person['name']}, Роль: {person['role']}, Компетенции: {person['skills']}, Моральные качества: {person['moral']}." for i, person in enumerate(project['people_data'])])
            all_projects.append(project_info + people_info + project['request'])

    if all_projects:
        full_info = " ".join(all_projects)
        answer = get_answer(full_info)
        st.write("Ответ модели:")
        st.text_area("Ответ", answer, height=200)
    else:
        st.warning("Нет данных для обработки.")

# Настройка страниц
st.set_page_config(page_title="Проект и Компетенции", layout="wide")
st.sidebar.title("Навигация")
page = option_menu(
    menu_title="Меню",
    options=["Авторизация", "Регистрация", "Личный кабинет", "Результат"],
    icons=["person-fill", "person-plus-fill", "house-fill", "check-circle-fill"],
    default_index=0,
    orientation="vertical"
)

if page == "Авторизация":
    login_page()
elif page == "Регистрация":
    register_page()
elif page == "Личный кабинет":
    if "username" in st.session_state:
        user_dashboard(st.session_state["username"])
    else:
        st.warning("Сначала авторизуйтесь.")
elif page == "Результат":
    result_page()
