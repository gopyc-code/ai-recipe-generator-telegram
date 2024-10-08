import telebot
from config import TOKEN
from handlers import (
    handle_start,
    handle_registration_or_update,
    collect_user_data,
    handle_login,
    handle_recipe_request
)
from user_manager import UserManager

bot = telebot.TeleBot(TOKEN)
user_manager = UserManager()

# Регистрация обработчиков
@bot.message_handler(commands=["start"])
def start_handler(message):
    handle_start(message, bot)

@bot.message_handler(commands=["register", "update"])
def registration_or_update_handler(message):
    handle_registration_or_update(message, bot, user_manager)

@bot.message_handler(func=lambda message: message.chat.id in user_manager.user_status)
def user_data_handler(message):
    collect_user_data(message, bot, user_manager)

@bot.message_handler(commands=["login"])
def login_handler(message):
    handle_login(message, bot, user_manager)

@bot.message_handler(commands=["recipe"])
def recipe_handler(message):
    handle_recipe_request(message, bot, user_manager)

bot.polling()
