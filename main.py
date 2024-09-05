import streamlit as st
from streamlit_option_menu import option_menu
import g4f

# Функция для получения ответа от модели GPT-3.5-turbo
def get_answer(request: str) -> str:
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=[ {"role": "system", "content": "Ты – качественный и полезный ассистент, который отвечает только на русском языке."},
            {"role": "user", "content": request}],
        provider = g4f.Provider.Bing
    )
    return response

# Функция для первой страницы
def input_page():
    st.title("Ввод данных о проекте и компетенциях")

    with st.form("project_form"):
        # Поля ввода для проекта
        st.header("Информация о проекте")
        project_name = st.text_input("Название проекта")
        project_description = st.text_area("Описание проекта")

        st.header("Информация о людях")

        # Поле для ввода количества людей
        num_people = st.number_input("Количество людей", min_value=1, max_value=10, value=1, step=1, key="num_people")

        # Создание полей ввода для каждого человека в зависимости от количества людей
        people_data = []
        for i in range(num_people):
            st.subheader(f"Человек {i + 1}")
            name = st.text_input(f"Имя человека {i + 1}", key=f"name_{i}")
            role = st.text_input(f"Роль человека {i + 1}", key=f"role_{i}")
            skills = st.text_area(f"Компетенции человека {i + 1}", key=f"skills_{i}")
            moral = st.text_area(f"Личные качества человека {i + 1}", key=f"moral{i}")
            people_data.append({"name": name, "role": role, "skills": skills, "moral" : moral})

        request = st.text_area("Вставьте весь текст сюда", height=150)

        submitted = st.form_submit_button("Сформировать строку")
        system_prompt = "Отвечай только на русском языке. Ты сервис для формирования компетентного профиля на основе Компетенций пользователя, на вход тебе поступает название проекта, его описание, а также список людей с из компетенция, твоя задача, понять кто именно из людей нужны для реализации проекта, и обосновать это. Отвечай только на русском языке.  Отвечай только на русском языке.Данные: "
        if submitted:
            project_info = f"Название проекта: {project_name}. Описание проекта: {project_description}.\n"
            people_info = " ".join(
                [f"Человек {i + 1}: Имя: {person['name']}, Роль: {person['role']}, Компетенции: {person['skills']}, Моральные качества: {person['moral']}." for
                 i, person in enumerate(people_data)])
            full_info = system_prompt + f"{project_info} {people_info} {request}"
            st.session_state["full_info"] = full_info

            print(full_info)
            answer = get_answer(full_info)
            print(answer)
            st.session_state["answer"] = answer
            st.success("Строка сформирована! Перейдите на страницу 'Результат' для просмотра.")

# Функция для второй страницы
def result_page():
    st.title("Результат")

    if "full_info" in st.session_state:
        st.write("Сформированная строка для нейросети:")
        st.text_area("Результат", st.session_state["full_info"], height=200)

        if "answer" in st.session_state:
            st.write("Ответ модели:")
            print(st.session_state["answer"])
            st.text_area("Ответ", st.session_state["answer"], height=100)
    else:
        st.warning("Сначала перейдите на страницу 'Ввод данных' и заполните форму.")

# Настройка страниц
st.set_page_config(page_title="Проект и Компетенции", layout="wide")
st.sidebar.title("Навигация")
page = option_menu(
    menu_title="Меню",  # required
    options=["Ввод данных", "Результат"],  # required
    icons=["pencil-fill", "check-circle-fill"],  # optional
    menu_icon="cast",  # optional
    default_index=0,  # optional
    orientation="vertical",
    styles={
        "container": {"padding": "0!important", "background-color": "#f0f0f0"},
        "icon": {"color": "orange", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#2C3E50"},
    }
)

if page == "Ввод данных":
    input_page()
elif page == "Результат":
    result_page()
