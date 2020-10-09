import html
import json
import logging
import os
import traceback
import django
from django.urls import reverse
from urlextract import URLExtract
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackQueryHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "links.settings")
django.setup()

from links import settings
from app.models import BotKey, Folder, Link, BotUnsavedLinks, BotKeyLanguage
from app.config import DEVELOPER_CHAT_ID, nickname, words
from app.utils import get_lang

extractor = URLExtract()
TOKEN = settings.BOT_KEY


def links(update, context):
    lang = get_lang(update)
    chat_id = str(update.message.from_user.id)
    try:
        bot_key = BotKey.objects.get(chat_id=chat_id)
        all_links = Link.objects.filter(folder__user=bot_key.user).order_by("-rating")
        answer = ""
        cnt = 1
        for link in all_links:
            answer += f"{cnt}. {link.rating} 🌟 {link.link}\n"
            cnt += 1
        if answer == "":
            answer = words['ru'] + words[lang]['help']
        update.message.reply_text(answer)
    except BotKey.DoesNotExist:
        update.message.reply_text(words[lang]["logout"]['not_auth'])


def get_keyboard(chat_id, start_num, update):
    lang = get_lang(update)
    folders = Folder.objects.filter(user=BotKey.objects.get(chat_id=chat_id).user).order_by("-rating")
    next = False
    prev = True
    if start_num == 0:
        prev = False
    elif start_num >= len(folders):
        return None
    else:
        if start_num + 3 >= len(folders):
            prev = True
            folders = folders[start_num:len(folders)]
        else:
            folders = folders[start_num:start_num + 3]
            next = True
    keyboard = []
    if len(folders) != 0:
        tmp = start_num
        for folder in folders:
            keyboard.append(
                [InlineKeyboardButton(f"{tmp + 1}. {folder.name}", callback_data=f"folder_choose_{folder.id}")])
            tmp += 1
        if next:
            keyboard.append([InlineKeyboardButton(">", callback_data=f"folder_next_{tmp}")])
        if prev:
            keyboard.append([InlineKeyboardButton("<", callback_data=f"folder_next_{start_num - 3}")])
    else:
        keyboard.append(
            [InlineKeyboardButton(words[lang]['keyboard']['create'], url=f"{settings.HOST}{reverse('folder_add')}")])
    keyboard = InlineKeyboardMarkup(keyboard)
    return keyboard


def add_link(update, context):
    lang = get_lang(update)
    chat_id = str(update.message.from_user.id)
    try:
        bot_key = BotKey.objects.get(chat_id=chat_id)
        answer = ""
        cnt = 1
        url = extractor.find_urls(update.message.text)
        if len(url) == 0:
            answer = words[lang]['links']['error']['no_message_links']
            folder_keyboard = None
        else:
            if len(Folder.objects.filter(user=bot_key.user)) != 0:
                answer = words[lang]['folder']["choose"].format(url[0])
            else:
                answer = words[lang]['links']['error']['no_folder']
            try:
                unsaved_link = BotUnsavedLinks.objects.get(chat_id=chat_id)
                unsaved_link.link = url[0]
            except BotUnsavedLinks.DoesNotExist:
                unsaved_link = BotUnsavedLinks(chat_id=chat_id, link=url[0])
            unsaved_link.save()
            folder_keyboard = get_keyboard(chat_id, 0, update)
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
                    update.message.reply_text(words[lang]["hello"].format(escape(bot_keys[i].user.username), settings.HOST,
                                                                          reverse('account:view_my')),
                                              parse_mode=telegram.ParseMode.MARKDOWN_V2)
                    update.message.reply_text(words[lang]['help'])
        else:
            update.message.reply_text(words[lang]["links"]["error"]["incorrect_api_key"])
            keyboard = [[InlineKeyboardButton(words[lang]["keyboard"]["get"],
                                              url=f'{settings.HOST}{reverse("account:view_my")[:-1]}#api_key')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(words[lang]["links"]["error"]["send_key"], reply_markup=reply_markup)


def escape(text):
    symbols = [".", "(", ")", "-", "_", ":", "/"]
    for symbol in symbols:
        text = text.replace(symbol, "\\" + symbol)
    return text


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    lang = get_lang(update)
    chat_id = str(update.message.from_user.id)
    args = " ".join(context.args)
    try:
        bot_key = BotKey.objects.get(chat_id=chat_id)
        update.message.reply_text(words[lang]["hello"].format(escape(bot_key.user.username), settings.HOST,
                                                              reverse('account:view_my')),
                                  parse_mode=telegram.ParseMode.MARKDOWN_V2)
    except BotKey.DoesNotExist:
        if args != "":
            bot_keys = BotKey.objects.filter(key=args.lower())
            if len(bot_keys) != 0:
                flag = False
                for i in range(len(bot_keys)):
                    if bot_keys[i].chat_id == "":
                        bot_keys[i].chat_id = chat_id
                        flag = True
                        bot_keys[i].save()
                    elif len(bot_keys) == i + 1:
                        bot_key = BotKey(key=args.lower(), chat_id=chat_id, user=bot_keys[i].user)
                        flag = True
                        bot_key.save()
                    if flag:
                        update.message.reply_text(words[lang]["hello"].format(escape(bot_keys[i].user.username), settings.HOST,
                                                                              reverse('account:view_my')),
                                                  parse_mode=telegram.ParseMode.MARKDOWN_V2)
                        update.message.reply_text(words[lang]['help'])
            else:
                update.message.reply_text(words[lang]["links"]["error"]["incorrect_api_key"])
                keyboard = [[InlineKeyboardButton(words[lang]["keyboard"]["get"],
                                                  url=f'{settings.HOST}{reverse("account:view_my")[:-1]}#api_key')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(words[lang]["links"]["error"]["send_key"], reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton(words[lang]["keyboard"]["get"],
                                      url=f'{settings.HOST}{reverse("account:view_my")[:-1]}#api_key')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(words[lang]["links"]["error"]["send_key"], reply_markup=reply_markup)


def logout(update, context):
    lang = get_lang(update)
    chat_id = str(update.message.from_user.id)
    try:
        bot_key = BotKey.objects.get(chat_id=chat_id)
        bot_key.chat_id = ""
        bot_key.save()
        update.message.reply_text(words[lang]["logout"]["success"])
    except BotKey.DoesNotExist:
        update.message.reply_text(words[lang]["logout"]['not_auth'])
    keyboard = [
        [InlineKeyboardButton(words[lang]["keyboard"]["get"], url=f'{settings.HOST}{reverse("account:view_my")[:-1]}#api_key')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(words[lang]["logout"]["help"], reply_markup=reply_markup)


def help(update, context):
    lang = get_lang(update)
    update.message.reply_text(words[lang]['help'])


def language(update, context):
    lang = get_lang(update)
    keyboard = []
    for i, k in words.items():
        keyboard.append([InlineKeyboardButton(k['name'], callback_data=f"setlanguage_{i}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(words[lang]['language'].format(nickname), reply_markup=reply_markup)


def error(update, context):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        'An exception was raised while handling an update\n'
        '<pre>update = {}</pre>\n\n'
        '<pre>context.chat_data = {}</pre>\n\n'
        '<pre>context.user_data = {}</pre>\n\n'
        '<pre>{}</pre>'
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(str(context.chat_data)),
        html.escape(str(context.user_data)),
        html.escape(tb)
    )
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def callback_handler(update, context):
    lang = get_lang(update.callback_query, query=True)
    query = update.callback_query
    chat_id = str(query.from_user.id)
    keyboard = None
    try:
        unsaved_link = BotUnsavedLinks.objects.get(chat_id=chat_id)
    except BotUnsavedLinks.DoesNotExist:
        query.answer("ХА-ХА-ХА")
        return
    if query.data.startswith("folder_next_"):
        keyboard = get_keyboard(chat_id, int(query.data.replace("folder_next_", "")), query)
        answer = words[lang]['folder']["choose"].format(unsaved_link.link)
    elif query.data.startswith("folder_choose_"):
        user = BotKey.objects.get(chat_id=chat_id).user
        try:
            folder = Folder.objects.get(id=int(query.data.replace("folder_choose_", "")), user=user)
        except Folder.DoesNotExist:
            query.answer("ХМММММММ")
            return
        links = Link.objects.filter(folder=folder)
        is_saved = False
        for link in links:
            if link.link == unsaved_link.link:
                answer = words[lang]["links"]["error"]["already_saved"].format(link.link, folder.name)
                keyboard = get_keyboard(chat_id, 0, query)
                is_saved = True
        if not is_saved:
            link = Link(folder=folder, link=unsaved_link.link)
            answer = words[lang]["links"]["saved"].format(link.link, link.folder.name)
            link.save()
    elif query.data.startswith("setlanguage_"):
        language = query.data.replace("setlanguage_", "")
        profile = BotKeyLanguage.objects.get(chat_id=chat_id)
        profile.lang = language
        profile.save()
        answer = words[get_lang(query, True)]['success']
    query.edit_message_text(answer, reply_markup=keyboard)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    updater.dispatcher.add_handler(CommandHandler("links", links))
    updater.dispatcher.add_handler(CommandHandler('logout', logout))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('lang', language))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, add_link))
    updater.dispatcher.add_error_handler(error)
    PORT = int(os.environ.get('PORT', '8443'))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook(f"{settings.BOT_HOST}/" + TOKEN)
    # updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
