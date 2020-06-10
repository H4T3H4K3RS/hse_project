import logging
import logging
import os
import re
import django
import telegram
from urlextract import URLExtract
from django.urls import reverse
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.utils import helpers
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackQueryHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "links.settings")
django.setup()

from links import settings
from app.models import BotSetup, BotKey, Folder, Link, BotUnsavedLinks

extractor = URLExtract()
api_key = BotSetup.objects.all()[0].key
start_msg = f'Пришлите в сообщении API\-ключ, полученный по [ссылке]({settings.HOST}{reverse("api_account_key")})'
help_msg = 'Просто пришлите\/перешлите текст, содержащий ссылку, в сообщении\.\n'
folder_msg = "Выберите подборку, в которую вы хотите сохранить ссылку {}\n" \
                 'Нажмите на кнопку ">", чтобы увидеть следующие 3 подборки\n' \
                 'Нажмите на кнопку "<", чтобы увидеть предыдущие 3 подборки\n' \
                 'Если вы не хотите сохранять данную ссылку, просто отправьте новую.'


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


def get_keyboard(chat_id, start_num):
    folders = Folder.objects.filter(user=BotKey.objects.get(chat_id=chat_id).user).order_by("-rating")
    next = False
    prev = True
    if start_num == 0:
        prev = False
    elif start_num >= len(folders):
        return None
    if start_num + 3 >= len(folders):
        prev = True
        folders = folders[start_num:len(folders)]
    else:
        folders = folders[start_num:start_num+3]
        next = True
    keyboard = []
    if len(folders) != 0:
        tmp = start_num
        for folder in folders:
            keyboard.append([InlineKeyboardButton(f"{tmp+1}. {escape(folder.name)}", callback_data=f"folder_choose_{folder.id}")])
            tmp += 1
        if next:
            keyboard.append([InlineKeyboardButton(">", callback_data=f"folder_next_{tmp}")])
        if prev:
            keyboard.append([InlineKeyboardButton("<", callback_data=f"folder_next_{start_num-3}")])
    else:
        keyboard.append([InlineKeyboardButton("Создать", url=f"{settings.HOST}{reverse('folder_add')}")])
    keyboard = InlineKeyboardMarkup(keyboard)
    return keyboard


def add_link(update, context):
    chat_id = str(update.message.from_user.id)
    try:
        bot_key = BotKey.objects.get(chat_id=chat_id)
        answer = ""
        cnt = 1
        url = extractor.find_urls(update.message.text)
        if len(url) == 0:
            answer = "В вашем сообщении не обнаружено ни одной ссылки\."
            folder_keyboard = None
        else:
            if len(Folder.objects.filter(user=bot_key.user)) != 0:
                answer = folder_msg.format(url[0])
            else:
                answer = "Вы пока ещё не создали ни одной подборки\. Нажмите на кнопку ниже, чтобы перейти к странице создания подборки\."
            try:
                unsaved_link = BotUnsavedLinks.objects.get(chat_id=chat_id)
                unsaved_link.link = url[0]
            except BotUnsavedLinks.DoesNotExist:
                unsaved_link = BotUnsavedLinks(chat_id=chat_id, link=url[0])
            unsaved_link.save()
            folder_keyboard = get_keyboard(chat_id, 0)
        update.message.reply_text(answer, reply_markup=folder_keyboard)
    except BotKey.DoesNotExist:
        bot_keys = BotKey.objects.filter(key=update.message.text)
        if len(bot_keys) != 0:
            flag = False
            for i in range(len(bot_keys)):
                if bot_keys[i].chat_id == "":
                    bot_keys[i].chat_id = chat_id
                    flag = True
                    bot_keys[i].save()
                elif len(bot_keys) == i + 1:
                    bot_key = BotKey(key=update.message.text, chat_id=chat_id, user=bot_keys[i].user)
                    flag = True
                    bot_key.save()
                if flag:
                    update.message.reply_text(f"Здравствуйте, {bot_keys[i].user.username}\n" + help_msg,
                                              parse_mode=telegram.ParseMode.MARKDOWN_V2)
        else:
            update.message.reply_text("Неправильный API\-ключ\.", parse_mode=telegram.ParseMode.MARKDOWN_V2)


def escape(text):
    symbols = [".", "(", ")", "-", "_", ":", "/"]
    for symbol in symbols:
        text = text.replace(symbol, "\\" + symbol)
    return text


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    # print(f'{settings.HOST}{reverse("api_account_key")}')
    keyboard = [[InlineKeyboardButton("Получить", url=f'{settings.HOST}{reverse("api_account_key")}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Отправьте боту полученный API-ключ', reply_markup=reply_markup)


def callback_handler(update, context):
    query = update.callback_query
    chat_id = str(query.from_user.id)
    user = BotKey.objects.get(chat_id=chat_id).user
    keyboard = None
    try:
        unsaved_link = BotUnsavedLinks.objects.get(chat_id=chat_id)
    except BotUnsavedLinks.DoesNotExist:
        query.answer("ХА-ХА-ХА")
        return
    if query.data.startswith("folder_next_"):
        keyboard = get_keyboard(chat_id, int(query.data.replace("folder_next_", "")))
        answer = folder_msg.format(unsaved_link.link)
    elif query.data.startswith("folder_choose_"):
        try:
            folder = Folder.objects.get(id=int(query.data.replace("folder_choose_", "")), user=user)
        except Folder.DoesNotExist:
            query.answer("ХМММММММ")
            return
        links = Link.objects.filter(folder=folder)
        is_saved = False
        for link in links:
            if link.link == unsaved_link.link:
                answer = f'Ссылка {link.link} уже сохранена в подборке "{folder.name}".\nВыберите подборку повторно'
                keyboard = get_keyboard(chat_id, 0)
                is_saved = True
        if not is_saved:
            link = Link(folder=folder, link=unsaved_link.link)
            answer = 'Ссылка {} сохранена в подборку "{}"'.format(link.link, link.folder.name)
            link.save()
    query.edit_message_text(answer, reply_markup=keyboard)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()


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


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(api_key, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    updater.dispatcher.add_handler(CommandHandler("links", links))
    updater.dispatcher.add_handler(CommandHandler('logout', logout))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, add_link))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
