import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from data_test import utils_db, config

app = Client(
    "my_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

@app.on_message(filters.command("start"))
def start(client, message):
    user_id = message.from_user.id
    if utils_db.user_id_in_db(user_id):
        keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("Мои задачи"), KeyboardButton("Мой профиль")]
            ],
            resize_keyboard=True
        )
        message.reply_text("Привет! Я ваш новый бот. 🤖", reply_markup=keyboard)
    else:
        utils_db.add_user(user_id)
        utils_db.update_stage(user_id, "get_name")
        message.reply_text("Добро пожаловать! Пожалуйста, введите ваше имя.")

# profile info
def my_profile(client, message):
    user_id = message.from_user.id
    result = utils_db.get_profile_info(user_id)
    if result:
        name = result['name']
        username = result['user_name']
        message.reply_text(f"Ваш профиль:\nИмя: {name}\nЛогин: {username}")
    else:
        message.reply_text("Профиль не найден.")

# Text handler & registration info

@app.on_message(filters.text & ~filters.command(["start", "help", "add", "list"]))
def handle_message(client, message):
    user_id = message.from_user.id
    stage = utils_db.get_stage(user_id)
    if stage == "get_name":
        name = message.text
        utils_db.add_name(user_id, name)
        utils_db.update_stage(user_id, "get_username")
        message.reply_text("Спасибо! Теперь введите ваш уникальный логин.")
    elif stage == "get_username":
        username = message.text
        if utils_db.username_exists(username):
            message.reply_text("Этот логин уже занят. Пожалуйста, введите другой логин.")
        else:
            utils_db.add_username(user_id, username)
            utils_db.update_stage(user_id, None)

            # Постоянное меню
            keyboard = ReplyKeyboardMarkup(
                [
                    [KeyboardButton("Мои задачи"), KeyboardButton("Мой профиль")]
                ],
                resize_keyboard=True
            )
            message.reply_text(f"Регистрация завершена! Добро пожаловать, {username}! 🎉", reply_markup=keyboard)
    elif stage == "get_task_title":
        task_title = message.text
        utils_db.update_temp_task(user_id, task_title=task_title)
        utils_db.update_stage(user_id, "get_task_description")
        message.reply_text("Введите описание задачи.")
    elif stage == "get_task_description":
        task_description = message.text
        temp_task = utils_db.get_temp_task(user_id)
        if temp_task:
            unique_id = temp_task['unique_id']
            utils_db.add_task(user_id, temp_task['task_title'], task_description, unique_id)
            utils_db.update_stage(user_id, None)
            utils_db.clear_temp_task(user_id)
            message.reply_text("Задача успешно создана!")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Ваши задачи", callback_data="tasks_page:1")]])
            message.reply_text("Для просмотра списка задач нажмите кнопку ниже.", reply_markup=keyboard)
        else:
            message.reply_text("Произошла ошибка при создании задачи. Пожалуйста, начните заново.")
    else:
        # Если пользователь не на этапе регистрации или создания задачи, проверяем сообщения "Мои задачи" и "Мой профиль"
        if message.text == "Мои задачи":
            my_tasks(client, message)
        elif message.text == "Мой профиль":
            my_profile(client, message)
        else:
            message.reply_text("Неизвестная команда. Пожалуйста, используйте кнопки для взаимодействия.")

# pagination_count
TASKS_PER_PAGE = 5

@app.on_message(filters.text & filters.regex("Мои задачи"))
def my_tasks(client, message, page=1,user_id=None):
    if user_id==None:
        user_id = message.from_user.id
    offset = (page - 1) * TASKS_PER_PAGE
    tasks,total_tasks=utils_db.get_tasks(user_id,offset,TASKS_PER_PAGE)
    total_pages = (total_tasks + TASKS_PER_PAGE - 1) // TASKS_PER_PAGE
    if tasks:
        buttons = []
        for task in tasks:
            task_title = task['task_title']
            if task.get('done', False):  # Проверяем, есть ли у задачи статус "done"
                task_title += " ✅"  # Если да, добавляем смайлик ✅ к названию задачи
            buttons.append([InlineKeyboardButton(task_title, callback_data=f"view_task:{task['unique_id']}")])
        if page > 1:
            buttons.append([InlineKeyboardButton("<<Назад", callback_data=f"tasks_page:{page-1}")])
        if page < total_pages:
            buttons.append([InlineKeyboardButton("Вперед>>", callback_data=f"tasks_page:{page+1}")])
        buttons.append([InlineKeyboardButton("Создать задачу",
                                             callback_data="create_task")])  # Добавляем кнопку "Создать задачу"
        keyboard = InlineKeyboardMarkup(buttons)
        message.reply_text("Ваши задачи:", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Создать задачу", callback_data="create_task")]
            ]
        )
        message.reply_text("Задач нет.", reply_markup=keyboard)


# pagination

@app.on_callback_query(filters.regex(r"tasks_page:(\d+)"))
def paginate_tasks(client, callback_query):
    page = int(re.match(r"tasks_page:(\d+)", callback_query.data).group(1))
    callback_query.message.delete()
    user_id = callback_query.from_user.id
    my_tasks(client, callback_query.message, page,user_id)

# Open task
@app.on_callback_query(filters.regex(r"view_task:(.+)"))
def view_task(client, callback_query):
    unique_id = re.match(r"view_task:(.+)", callback_query.data).group(1)
    user_id = callback_query.from_user.id
    task=utils_db.view_task(user_id,unique_id)
    if task:
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Удалить задачу", callback_data=f"delete_task:{unique_id}")],
                [InlineKeyboardButton("Выполнена✅", callback_data=f"done_task:{unique_id}")],
                [InlineKeyboardButton("Назад к задачам", callback_data=f"tasks_page:1")]
            ]
        )
        callback_query.message.edit_text(f"Задача: {task['task_title']}\nОписание: {task['task_description']}", reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"delete_task:(.+)"))
def delete_task(client, callback_query):
    unique_id = re.match(r"delete_task:(.+)", callback_query.data).group(1)
    user_id = callback_query.from_user.id
    utils_db.delete_task(user_id,unique_id)
    callback_query.message.edit_text("Задача удалена.")
    my_tasks(client, callback_query.message, page=1,user_id=user_id)

@app.on_callback_query(filters.regex(r"done_task:(.+)"))
def delete_task(client, callback_query):
    unique_id = re.match(r"done_task:(.+)", callback_query.data).group(1)
    user_id = callback_query.from_user.id
    utils_db.task_done(unique_id)
    callback_query.message.edit_text("Задача обновлена")
    my_tasks(client, callback_query.message, page=1, user_id=user_id)

@app.on_callback_query(filters.regex("create_task"))
def create_task_button(client, callback_query):
    import uuid
    user_id = callback_query.from_user.id
    unique_id = str(uuid.uuid4())  # Генерируем уникальный идентификатор
    utils_db.update_temp_task(user_id, unique_id=unique_id)
    utils_db.update_stage(user_id, "get_task_title")
    callback_query.message.edit_text("Введите название задачи")

if __name__ == "__main__":
    app.run()
