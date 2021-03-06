import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram import KeyboardButton
from model.Courses import Courses
import pymongo

# Setup database
client = pymongo.MongoClient()
db = client['courses']
# TODO here is test purposes -- DONE
collection = db['courses']

# setup updater, dispatcher, and logging
updater = Updater( token='296973878:AAG8-Gu2ESh8rSbXX0S14R_8uJtC4opjCKY' )
dispatcher = updater.dispatcher
logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.WARNING )

# wrappers
def add_handlers( handlers ):
    for handler in handlers:
        dispatcher.add_handler( handler )



# Globals
CURRENT_MODE = dict()
show_more = KeyboardButton('Показать еще')
popular = KeyboardButton('Популярное')
new = KeyboardButton('Новое')
# tag_search = KeyboardButton('Поиск по тегам')

def gen_data( obj ):
    new_data = []
    try:
        new_data.append(obj['screen_name'])
    except KeyError:
        new_data.append('')
    try:
        new_data.append(obj['description'])
    except KeyError:
        new_data.append('')
    try:
        new_data.append('@' + obj['bot_name'])
    except KeyError:
        new_data.append('')
    try:
        new_data.append(obj['author'])
    except KeyError:
        new_data.append('')
    try:
        new_data.append(obj['connections_count'])
    except KeyError:
        new_data.append('')
    try:
        new_data.append(obj['tags'])
    except KeyError:
        new_data.append('')

    # try:
    #     new_data.append(obj['token'])
    # except KeyError:
    #     new_data.append('')
    return new_data


def on_start_command( bot, update ):

    courses = collection.find().sort( 'connections_count', -1 )
    i = 0
    messages = list()
    messages.append('ПОПУЛЯРНОЕ /')
    data = list(courses)
    for ent in data:
        i += 1
        msg = u"""{0}: {1}
    {2}
    Link: {3}
    By {4}, \U0001F464 ({5})
    Tags: {6}""".format(i,*gen_data(ent))
        messages.append( msg )
        if i == 3:
            break

    chat_id = str(update.message.chat_id)
    CURRENT_MODE[chat_id] = {
        'mode': 'mp',
        'from': i,
        'data': data[i:]
    }
    # print('!!!',CURRENT_MODE, CURRENT_MODE[chat_id], '\n', CURRENT_MODE[chat_id]['data'])

    repl = ReplyKeyboardMarkup([[show_more],[new],
                                [KeyboardButton("Поиск по тегам")]],
                               resize_keyboard=False)

    bot.sendMessage( chat_id=update.message.chat_id,
                     text='\n'.join(messages),
                     reply_markup=repl)


def on_message( bot, update ):
    chat_id = update.message.chat_id
    message = update.message.text
    if message == 'Показать еще':
        i = 0
        messages = []

        for ent in CURRENT_MODE[str(chat_id)]['data']:
            i += 1
            msg = u"""{0}: {1}
        {2}
        Link: {3}
        By {4}, \U0001F464 ({5})
        Tags: {6}""".format(i + CURRENT_MODE[str(chat_id)]['from'], *gen_data(ent))
            messages.append(msg)
            if i == 3:
                break

        if i < 3:
            extra_msg = "\nБольше нету :(, создай свой крутой курс на @SYMPO_CREATE"
        else:
            extra_msg = ''

        CURRENT_MODE[str(chat_id)]['from'] += i
        CURRENT_MODE[str(chat_id)]['data'] = CURRENT_MODE[str(chat_id)]['data'][i:]
        messages.append(extra_msg)
        if CURRENT_MODE[str(chat_id)]['mode'] == 'mp':
            repl = ReplyKeyboardMarkup([[KeyboardButton('Показать еще')],
                                        [KeyboardButton('Новое')],
                                        [KeyboardButton('Поиск по тегам')]],
                                       resize_keyboard=False)
        elif CURRENT_MODE[str(chat_id)]['mode'] == 'new':
            repl = ReplyKeyboardMarkup([[KeyboardButton('Показать еще')],
                                        [KeyboardButton('Популярное')],
                                        [KeyboardButton('Поиск по тегам')]],
                                       resize_keyboard=False)
        else:
            repl = ReplyKeyboardMarkup([[new], [popular]])

        # repl = ReplyKeyboardMarkup([[show_more],
        #                             [but1]]
        #                            )
        bot.sendMessage(chat_id, "\n".join(messages), reply_markup=repl)
    elif message == 'Популярное':
        courses = collection.find().sort('connections_count', -1)
        i = 0
        messages = list()
        data = list(courses)
        for ent in data:
            i += 1
            msg = u"""{0}: {1}
            {2}
            Link: {3}
            By {4}, \U0001F464 ({5})
            Tags: {6}
            """.format(i,*gen_data(ent))
            messages.append(msg)
            if i == 3:
                break

        chat_id = str(update.message.chat_id)
        CURRENT_MODE[chat_id] = {
            'mode': 'mp',
            'from': i,
            'data': data[i:]
        }

        repl = ReplyKeyboardMarkup([[KeyboardButton('Показать еще')],
                                    [KeyboardButton('Новое')],
                                    [KeyboardButton('Поиск по тегам')]],
                                   resize_keyboard=False)
        bot.sendMessage( chat_id=update.message.chat_id,
                         text='\n'.join(messages), reply_markup=repl)

    elif message == 'Новое':
        courses = collection.find().sort('created_at', -1)
        i = 0
        messages = list()
        messages.append("Новое /")
        data = list(courses)
        for ent in data:
            i += 1
            msg = u"""{0}: {1}
            {2}
            Link: {3}
            By {4}, \U0001F464 ({5})
            Tags: {6}""".format(i,*gen_data(ent))
            messages.append(msg)
            if i == 3:
                break

        chat_id = str(update.message.chat_id)
        CURRENT_MODE[chat_id] = {
            'mode': 'new',
            'from': i,
            'data': data[i:]
        }

        repl = ReplyKeyboardMarkup([[KeyboardButton('Показать еще')],
                                    [KeyboardButton('Популярное')],
                                    [KeyboardButton('Поиск по тегам')]],
                                   resize_keyboard=False)

        bot.sendMessage(chat_id=update.message.chat_id,
                        text='\n'.join(messages), reply_markup=repl)
    elif message == "Поиск по тегам":
        CURRENT_MODE[str(chat_id)]['mode'] = 'tg'
        CURRENT_MODE[str(chat_id)]['from'] = 0
        CURRENT_MODE[str(chat_id)]['data'] = list()
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Введите Тег")

    elif CURRENT_MODE[str(chat_id)]['mode'] == 'tg':
        tag = str(update.message.text).lower()
        msg = list()
        msg.append("Результаты поиска")
        courses = collection.find()
        i = 1
        for ent in courses:
            try:
                print(ent['tags'])
                if tag in ent['tags']:
                    msg.append(u"""{0}: {1}
                    {2}
                    Link: {3}
                    By {4}, \U0001F464 ({5})
                    Tags: {6}""".format(i,*gen_data(ent)))
            except (IndexError, KeyError):
                pass

        CURRENT_MODE[str(chat_id)]['mode'] = 'mp'

        repl = ReplyKeyboardMarkup([[KeyboardButton("Популярное")],
                                    [KeyboardButton("Новое")],
                                    [KeyboardButton("Поиск по тегам")]],
                                   resize_keyboard=False)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="\n".join(msg),
                        reply_markup=repl)



# assign handlers
add_handlers( [ CommandHandler( 'start', on_start_command ) , MessageHandler([Filters.text], on_message)])



# start your engines
updater.start_polling()