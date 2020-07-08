nickname = "nikesnkrs_admin"

words = {
    "ru": {
        "name": "🇷🇺 Russian (Русский) 🇷🇺",
        "language": 'Сейчас вы используете "🇷🇺 Русский 🇷🇺" язык\n🌐 Выберите Язык: 🌐',
        "help": 'Просто пришлите/перешлите текст, содержащий ссылку, в сообщении.\n',
        "folder": {
            "choose": 'Выберите подборку, в которую вы хотите сохранить ссылку {}\nНажмите на кнопку ">", чтобы увидеть следующие 3 подборки\nНажмите на кнопку "<", чтобы увидеть предыдущие 3 подборки\nЕсли вы не хотите сохранять данную ссылку, просто отправьте новую.'
        },
        "links": {
            "error": {
                "no_links": "Вы ещё не добавили ни одну ссылку.\n",
                "no_message_links": "В вашем сообщении не обнаружено ни одной ссылки.",
                "no_folder": "Вы пока ещё не создали ни одной подборки. Нажмите на кнопку ниже, чтобы перейти к странице создания подборки.",
                "incorrect_api_key": "Неправильный API-ключ.",
                "send_key": 'Отправьте боту полученный API-ключ',
                "already_saved": 'Ссылка {} уже сохранена в подборке "{}".\nВыберите подборку повторно',
            },
            "saved": 'Ссылка {} сохранена в подборку "{}"',
        },
        "keyboard": {
            "create": "Создать",
            "get": "Получить"
        },
        "logout": {
            "not_auth": "Вы не авторизованы.",
            "success": "Вы успешны вышли из аккаунта!",
            "help": 'Для авторизации отправьте боту полученный API-ключ',
        },
        "hello": "Здравствуйте, [{}]({}{})\n",
        "success": 'Ваш язык был изменён на "🇷🇺 РУССКИЙ 🇷🇺", чтобы изменить выбор используйте команду: /lang'
    },
    "en": {
        "name": "🇺🇸 English 🇺🇸",
        "language": 'You are currently using "🇺🇸 English 🇺🇸" language.\n🌐 Choose Language: 🌐',
        "help": 'Just Send/Forward me a text, containing the url.\n',
        "folder": {
            "choose": 'Choose the Folder in which you want to save link {}\nClick the button ">" to see 3 next folders\nClick the button "<" to see 3 previous folders\nIf you don\'t want to save the link, just send me the other one.'
        },
        "links": {
            "error": {
                "no_links": "You haven't added any links yet.\n",
                "no_message_links": "There is no url in your message",
                "no_folder": "You haven't created any folder yet. Click the link below, to go to the page, where you can create it.",
                "incorrect_api_key": "Incorrect API-key.",
                "send_key": 'Send the obtained API-key to me.',
                "already_saved": 'Link {} is already saved in folder "{}".\nChoose the folder again.',
            },
            "saved": 'Link {} has been successfully saved to folder "{}"',
        },
        "keyboard": {
            "create": "Create",
            "get": "Get"
        },
        "logout": {
            "not_auth": "You are not authorized.",
            "success": "You have successfully logged out!",
            "help": 'To authorize send the API-key to me.',
        },
        "hello": "Hello, [{}]({}{})\n",
        "success": 'Your language has been successfully changed to "🇺🇸 ENGLISH 🇺🇸". To choose another language use command: /lang'
    }
}
languages = []
for i, k in words.items():
    languages.append(i)
DEVELOPER_CHAT_ID = 447219049
