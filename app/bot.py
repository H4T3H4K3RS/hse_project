import logging
import os
import re
import django
from urlextract import URLExtract
from django.urls import reverse
import telegram
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "links.settings")
django.setup()

from links import settings
from app.models import BotSetup, BotKey, Folder, Link

extractor = URLExtract()
api_key = BotSetup.objects.all()[0].key
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text(f'Пришлите в сообщении API\-ключ, полученный по [ссылке](https://linkit.herokuapp.com)', parse_mode=telegram.ParseMode.MARKDOWN_V2)


def help(update, context):
    update.message.reply_text('Help!')


def add_link(update, context):
    chat_id = str(update.message.from_user.id)
    try:
        bot_key = BotKey.objects.get(chat_id=chat_id)
        try:
            folder = Folder.objects.get(user=bot_key.user, name="Telegram")
        except Folder.DoesNotExist:
            folder = Folder(user=bot_key.user, name="Telegram")
            folder.save()
        answer = ""
        cnt = 1
        for i in extractor.find_urls(update.message.text):
            try:
                link = Link.objects.get(folder=folder, link=i)
                answer += f'{cnt}. {link.link} - уже существует в подборке\n'
            except Link.DoesNotExist:
                link = Link(folder=folder, link=i)
                link.save()
                answer += f'{cnt}. {link.link} - успешно сохранена\n'
            cnt += 1
        if answer == "":
            answer = "В вашем сообщении не обнаружено ни одной ссылки."
        update.message.reply_text(answer)
    except BotKey.DoesNotExist:
        try:
            bot_key = BotKey.objects.get(key=update.message.text)
            bot_key.chat_id = chat_id
            bot_key.save()
            update.message.reply_text(f"Здравствуйте, {bot_key.user.username}")
        except BotKey.DoesNotExist:
            update.message.reply_text("Неправильный API-ключ.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(api_key, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, add_link))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
