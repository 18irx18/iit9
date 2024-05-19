import telebot
import logging
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])
def create_index_if_not_exists(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
        print(f"Index '{index_name}' created successfully.")

def main():

    create_index_if_not_exists('bot_logs')
    bot = telebot.TeleBot('6940370824:AAHs-lLnOONqerS-9z7L7xFX9nZSC6TUDQA')

    class BotLogger:
        def __init__(self, log_file):
            self.logger = logging.getLogger("bot_logger")
            self.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        def log(self, level, message, username):
            if level == 'info':
                self.logger.info(message)
            elif level == 'error':
                self.logger.error(message)
            elif level == 'debug':
                self.logger.debug(message)

            try:
                es.index(index='bot_logs', body={
                    'level': level,
                    'message': message,
                    'username': username
                })
            except Exception as e:
                print(f"Failed to send log to Elasticsearch: {e}")

    logger = BotLogger('bot_logs.log')

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        bot.send_message(message.chat.id, "Hello! I am a login bot. Send me a message and I will log it.")
        username = message.from_user.username or message.from_user.first_name
        logger.log('info', f"Received /start command from user {username}", username)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        bot.send_message(message.chat.id, "The message has been received and logged.")
        username = message.from_user.username or message.from_user.first_name
        logger.log('info', f"Received message from user {username}: {message.text}", username)

    bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    main()
