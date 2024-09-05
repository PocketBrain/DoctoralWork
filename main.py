import streamlit as st
import g4f


# Функция для получения ответа от модели GPT-3.5-turbo
def get_answer(request: str) -> str:
    response = g4f.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system",
                   "content": "Ты – качественный и полезный ассистент, который отвечает только на русском языке."},
                  {"role": "user", "content": request}],
    )
    return response


# Функция для первой страницы
def input_page():
    st.title("Ввод данных о проекте и компетенциях")

    with st.form("project_form"):
        # Поля ввода для проекта
        st.header("Информация о проекте")
        project_name = st.text_input("Название проекта", value=st.session_state.get("project_name", ""))
        project_description = st.text_area("Описание проекта", value=st.session_state.get("project_description", ""))

        st.header("Информация о людях")

        # Поле для ввода количества людей
        num_people = st.number_input("Количество людей", min_value=1, max_value=10,
                                     value=st.session_state.get("num_people", 1), step=1, key="num_people")

        # Создание полей ввода для каждого человека в зависимости от количества людей
        people_data = []
        for i in range(num_people):
            st.subheader(f"Человек {i + 1}")
            name = st.text_input(f"Имя человека {i + 1}", key=f"name_{i}", value=st.session_state.get(f"name_{i}", ""))
            role = st.text_input(f"Роль человека {i + 1}", key=f"role_{i}", value=st.session_state.get(f"role_{i}", ""))
            skills = st.text_area(f"Компетенции человека {i + 1}", key=f"skills_{i}",
                                  value=st.session_state.get(f"skills_{i}", ""))
            moral = st.text_area(f"Личные качества человека {i + 1}", key=f"moral{i}",
                                 value=st.session_state.get(f"moral_{i}", ""))
            people_data.append({"name": name, "role": role, "skills": skills, "moral": moral})

        request = st.text_area("Дополнительная информация (опционально)", height=150,
                               value=st.session_state.get("request", ""))

        submitted = st.form_submit_button("Сформировать строку")

        if submitted:
            # Сохранение данных для последующего использования
            st.session_state["project_name"] = project_name
            st.session_state["project_description"] = project_description
            st.session_state["request"] = request
            for i in range(num_people):
                st.session_state[f"name_{i}"] = people_data[i]['name']
                st.session_state[f"role_{i}"] = people_data[i]['role']
                st.session_state[f"skills_{i}"] = people_data[i]['skills']
                st.session_state[f"moral_{i}"] = people_data[i]['moral']

            system_prompt = "Отвечай только на русском языке. Ты сервис для формирования компетентного профиля на основе компетенций пользователя..."
            project_info = f"Название проекта: {project_name}. Описание проекта: {project_description}.\n"
            people_info = " ".join([
                                       f"Человек {i + 1}: Имя: {person['name']}, Роль: {person['role']}, Компетенции: {person['skills']}, Моральные качества: {person['moral']}."
                                       for i, person in enumerate(people_data)])
            full_info = system_prompt + f"{project_info} {people_info} {request}"

            st.session_state["full_info"] = full_info
            answer = get_answer(full_info)
            st.session_state["answer"] = answer
            st.success("Строка успешно сформирована! Перейдите на страницу 'Результат' для просмотра.")


# Функция для страницы с результатом
def result_page():
    st.title("Результат")

    if "full_info" in st.session_state:
        st.write("Сформированная строка для нейросети:")
        st.text_area("Входные данные", st.session_state["full_info"], height=200)

        if "answer" in st.session_state:
            st.write("Ответ модели:")
            st.text_area("Ответ", st.session_state["answer"], height=100)
    else:
        st.warning("Сначала заполните форму на странице 'Ввод данных'.")


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
        "container": {"padding": "0!important", "background-color": "#f9f9f9"},
        "icon": {"color": "#2C3E50", "font-size": "25px"},
        "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#2980b9"},
    }
)

if page == "Ввод данных":
    input_page()
elif page == "Результат":
    result_page()
