class UserManager:
    def __init__(self):
        self.user_data = {}
        self.user_status = {}
        self.bot_user_data = {}

    def get_user_data(self, chat_id):
        return self.user_data.get(chat_id, {})

    def set_user_data(self, chat_id, data):
        self.user_data[chat_id] = data

    def get_user_status(self, chat_id):
        return self.user_status.get(chat_id)

    def set_user_status(self, chat_id, status):
        self.user_status[chat_id] = status

    def get_bot_user_data(self, chat_id):
        return self.bot_user_data.get(chat_id)

    def set_bot_user_data(self, chat_id, data):
        self.bot_user_data[chat_id] = data

    def clear_user_data(self, chat_id):
        self.user_data.pop(chat_id, None)
        self.user_status.pop(chat_id, None)
