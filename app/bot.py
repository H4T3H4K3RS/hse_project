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

start_msg = f'Пришлите в сообщении API\-ключ, полученный по [ссылке]({settings.HOST}{reverse("api_account_key")})'
help_msg = '1\. Просто пришлите текст, содержащий ссылки, в сообщении\. \(Все ссылки из него будут сохранены\)\.\n2\. ' \
           'Перешлите сообщение, содержащее ссылки, боту\. \(Все ссылки из него будут сохранены\)\. '


def escape(text):
    symbols = [".", "(", ")", "-"]
    for symbol in symbols:
        text = text.replace(symbol, "\\" + symbol)
    return text


def start(update, context):
    update.message.reply_text(start_msg, parse_mode=telegram.ParseMode.MARKDOWN_V2)


def links(update, context):
    chat_id = str(update.message.from_user.id)
    try:
        bot_key = BotKey.objects.get(chat_id=chat_id)
        all_links = Link.objects.filter(folder__user=bot_key.user).order_by("-rating")
        answer = ""
        cnt = 1
        for link in all_links:
            answer += f"{cnt}\. [{link.rating}] [{escape(link.link)}]({link.link})\n"
            cnt += 1
        if answer == "":
            answer = "Вы ещё не добавили ни одну ссылку\.\n" + help_msg
        update.message.reply_text(answer, parse_mode=telegram.ParseMode.MARKDOWN_V2)
    except BotKey.DoesNotExist:
        update.message.reply_text("Вы не авторизованы\.")


def logout(update, context):
    chat_id = str(update.message.from_user.id)
    try:
        bot_key = BotKey.objects.get(chat_id=chat_id)
        bot_key.chat_id = ""
        bot_key.save()
        update.message.reply_text("Вы успешны вышли из аккаунта\!", parse_mode=telegram.ParseMode.MARKDOWN_V2)
    except BotKey.DoesNotExist:
        update.message.reply_text("Вы не авторизованы\.", parse_mode=telegram.ParseMode.MARKDOWN_V2)


def help(update, context):
    update.message.reply_text(help_msg, parse_mode=telegram.ParseMode.MARKDOWN_V2)


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
                answer += f'{cnt}\. {escape(link.link)} \- уже существует в подборке\n'
            except Link.DoesNotExist:
                link = Link(folder=folder, link=i)
                link.save()
                answer += f'{cnt}\. {escape(link.link)} \- успешно сохранена\n'
            cnt += 1
        if answer == "":
            answer = "В вашем сообщении не обнаружено ни одной ссылки."
        update.message.reply_text(answer, parse_mode=telegram.ParseMode.MARKDOWN_V2)
    except BotKey.DoesNotExist:
        bot_keys = BotKey.objects.filter(key=update.message.text)
        if len(bot_keys) != 0:
            flag = False
            for i in range(len(bot_keys)):
                if bot_keys[i].chat_id == "":
                    bot_keys[i].chat_id = chat_id
                    flag = True
                elif len(bot_keys) == i - 1:
                    bot_keys[i] = BotKey(key=update.message.text, chat_id=chat_id, user=bot_keys[i].user)
                    flag = True
                bot_keys[i].save()
                if flag:
                    update.message.reply_text(f"Здравствуйте, {bot_keys[i].user.username}\n" + help_msg,
                                              parse_mode=telegram.ParseMode.MARKDOWN_V2)
        else:
            update.message.reply_text("Неправильный API-ключ.", parse_mode=telegram.ParseMode.MARKDOWN_V2)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(api_key, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("links", links))
    dp.add_handler(CommandHandler('logout', logout))
    dp.add_handler(MessageHandler(Filters.text, add_link))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
