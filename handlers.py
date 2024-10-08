import telebot
from telebot import formatting
import requests
from config import API_URL

def handle_start(message, bot):
    """Обрабатывает команду /start."""
    bot.send_message(
        message.chat.id,
        "Привет! Вы можете войти с помощью /login, зарегистрироваться с помощью /register или обновить данные с помощью /update."
    )

def handle_registration_or_update(message, bot, user_manager):
    """Начало регистрации пользователя или обновления данных."""
    chat_id = message.chat.id

    if message.text.startswith("/register"):
        bot.send_message(chat_id, "Введите своё имя:")
        user_manager.set_user_status(chat_id, "register")  # Устанавливаем статус регистрации
    elif message.text.startswith("/update"):
        bot.send_message(chat_id, "Введите новое имя:")
        user_manager.set_user_status(chat_id, "update")  # Устанавливаем статус обновления данных

    user_manager.set_user_data(chat_id, {})  # Очищаем данные для нового пользователя или обновления

def collect_user_data(message, bot, user_manager):
    """Сбор данных для регистрации или обновления пользователя."""
    chat_id = message.chat.id
    status = user_manager.get_user_status(chat_id)  # Проверяем, регистрация или обновление

    if "name" not in user_manager.get_user_data(chat_id):
        user_manager.get_user_data(chat_id)["name"] = message.text
        bot.send_message(chat_id, "Выберите уникальный логин:")
    elif "login" not in user_manager.get_user_data(chat_id):
        user_manager.get_user_data(chat_id)["login"] = message.text
        bot.send_message(chat_id, "Введите пароль:")
    elif "password" not in user_manager.get_user_data(chat_id):
        user_manager.get_user_data(chat_id)["password"] = message.text
        bot.send_message(chat_id, "В какой стране вы живёте?")
    elif "country" not in user_manager.get_user_data(chat_id):
        user_manager.get_user_data(chat_id)["country"] = message.text
        bot.send_message(chat_id, "Сколько вам лет? (пожалуйста, введите целое число)")
    elif "age" not in user_manager.get_user_data(chat_id):
        try:
            user_manager.get_user_data(chat_id)["age"] = int(message.text)
            bot.send_message(chat_id, "Какие у вас вкусовые предпочтения?")
        except ValueError:
            bot.send_message(chat_id, "Неверный формат! Пожалуйста, введите ваш возраст как целое число.")
    elif "preferences" not in user_manager.get_user_data(chat_id):
        user_manager.get_user_data(chat_id)["preferences"] = message.text
        bot.send_message(chat_id, "Есть ли у вас диетические ограничения?")
    elif "diet_restrictions" not in user_manager.get_user_data(chat_id):
        user_manager.get_user_data(chat_id)["diet_restrictions"] = message.text
        bot.send_message(chat_id, "Каков ваш бюджет на блюда? (например, 500)")
    elif "budget" not in user_manager.get_user_data(chat_id):
        try:
            user_manager.get_user_data(chat_id)["budget"] = float(message.text)
            bot.send_message(chat_id, "Укажите ваш пол:")  # Новый вопрос
        except ValueError:
            bot.send_message(chat_id, "Неверный формат! Пожалуйста, введите ваш бюджет как число (например, 500).")
    elif "gender" not in user_manager.get_user_data(chat_id):  # Добавлено поле "gender"
        user_manager.get_user_data(chat_id)["gender"] = message.text
        # Все данные собраны, теперь отправляем их на сервер
        if status == "register":
            response = requests.post(f"{API_URL}/users/", json=user_manager.get_user_data(chat_id))
            if response.status_code == 200:
                bot.send_message(chat_id, f"Регистрация завершена, {user_manager.get_user_data(chat_id)['name']}! Теперь вы можете войти с помощью /login.")
            else:
                bot.send_message(chat_id, "Ошибка регистрации: логин уже существует или другая ошибка.")
        elif status == "update":
            # Отправляем PUT-запрос для обновления данных
            response = requests.put(f"{API_URL}/users/{user_manager.get_user_data(chat_id)['login']}", json=user_manager.get_user_data(chat_id))
            if response.status_code == 200:
                bot.send_message(chat_id, f"Ваши данные успешно обновлены, {user_manager.get_user_data(chat_id)['name']}!")
            else:
                bot.send_message(chat_id, "Ошибка при обновлении данных. Попробуйте позже.")
        # Очищаем данные
        user_manager.clear_user_data(chat_id)

def handle_login(message, bot, user_manager): 
    """Обрабатывает команду /login."""
    try:
        _, login, password = message.text.split()
        user_login_data = {"login": login, "password": password}
        response = requests.post(f"{API_URL}/login/", json=user_login_data)

        if response.status_code == 200:
            user_info = response.json()
            bot.send_message(
                message.chat.id,
                f"Вы успешно вошли в систему, {user_info['name']}! Теперь вы можете запросить рецепт с помощью команды /recipe."
            )
            user_manager.set_bot_user_data(message.chat.id, {"login": login, "name": user_info["name"]})
        else:
            bot.send_message(message.chat.id, "Неверный логин или пароль.")
    except ValueError:
        bot.send_message(message.chat.id, "Используйте формат: /login <логин> <пароль>")

def format_recipe_output(recipe):
    """Форматирует рецепт для удобного вывода в Telegram."""
    title = formatting.hbold(recipe.get('recipe_name', 'Не указано'))
    ingredients = "\n".join([f"🔹 {item['name']} ({item['quantity']})" for item in recipe.get('ingredients', [])])
    instructions = "\n".join([f"❇️ <b>{step['step_title']}</b>: {step['description']}" for step in recipe.get('instructions', [])])
    comments = recipe.get("comments", "Нет комментариев")
    cuisine = recipe.get("cuisine", "Не указано")
    calories = recipe.get("calories", "Не указано")
    health_benefits = recipe.get("health_benefits", "Информация отсутствует")
    rating = recipe.get("rating", "Не оценено")

    formatted_output = (
        f"<b>{title}</b>\n\n"  # Заголовок
        f"<b>Ингредиенты:</b>\n{ingredients}\n\n"  # Ингредиенты
        f"<b>Инструкции:</b>\n{instructions}\n\n"  # Инструкции
        f"<b>🍽️ Кухня:</b> {cuisine}\n"
        f"<b>🔥 Калорийность:</b> {calories}\n"
        f"<b>💪 Польза/вред:</b> {health_benefits}\n"
        f"<b>✨ Комментарий:</b> {comments}\n"
        f"<b>⭐ Рейтинг:</b> {rating}\n"
    )

    return formatted_output

def send_recipe_with_image(bot, chat_id, recipe):
    """Отправляет рецепт с изображением в чате Telegram."""
    
    image_url = recipe.get("image_url")
    formatted_output = format_recipe_output(recipe)

    if image_url:
        image_url = image_url.replace('https', 'http')
        bot.send_photo(chat_id, image_url, caption="", parse_mode='HTML')
    else:
        bot.send_message(chat_id, "Картинка отсутствует, но рецепт готов!")
    bot.send_message(chat_id, formatted_output, parse_mode='HTML')  # Отправляем текст рецепта

def handle_recipe_request(message, bot, user_manager):
    """Обрабатывает запросы на блюда через команду /recipe."""
    chat_id = message.chat.id
    user_info = user_manager.get_bot_user_data(chat_id)

    if not user_info:
        bot.send_message(chat_id, "Сначала войдите в систему с помощью /login")
        return

    # Убираем команду /recipe из текста, оставляем только запрос пользователя
    user_request = message.text[len("/recipe"):].strip()

    if not user_request:
        bot.send_message(chat_id, f"{user_info['name']}, введите запрос после команды /recipe, например: /recipe Хочу пиццу.")
        return

    recipe_request = {
        "login": user_info["login"],
        "request": user_request  # Произвольный запрос пользователя
    }

    response = requests.post(f"{API_URL}/recipes/", json=recipe_request)

    if response.status_code == 200:
        recipe_response = response.json().get('recipe')

        # Проверяем, что получили рецепт
        if recipe_response:
            send_recipe_with_image(bot, chat_id, recipe_response)
        else:
            bot.send_message(chat_id, f"{user_info['name']}, не удалось получить рецепт. Попробуйте позже.")
    else:
        bot.send_message(chat_id, f"{user_info['name']}, произошла ошибка при получении рецепта. Код ошибки: {response.status_code}. Попробуйте позже.")
