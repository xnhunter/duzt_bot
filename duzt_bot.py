# UkrDUZT Bot for Telegram
# Copyright ⓒ 2020-2021 Valentyn Bondarenko. All rights reserved.

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction, ReplyKeyboardMarkup, InlineQueryResultArticle,  \
    InputTextMessageContent, ParseMode, InlineQueryResultContact, InputContactMessageContent, InlineQueryResultVenue, InputMediaPhoto
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler
from telegram.utils.helpers import escape_markdown

from duzt_bot_utils import send_typing_action, user_counter

from uuid import uuid4

import logging
import os.path
import json

logger = logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename="log.txt")
logger = logging.getLogger('duzt.kernel')


bot_version = '1.0.0 Alpha'
bot_token = 'your_token'

CHOOSING, TYPING_REPLY, SHUTDOWN = range(3)

# Language-specific messages used by bot.
start_message = ""
help_message = ""
language_changed_message = ""
language_choose_message = ""
feedback_message = ""
feedback_thanks_message = ""
version_message = ''

lang_codes = ['ua', 'ru', 'en' ]

keyboard = [[InlineKeyboardButton('Українська', callback_data='ua')],
                [InlineKeyboardButton('Русский', callback_data='ru')],
                [InlineKeyboardButton('English', callback_data='en')]]

@send_typing_action
def start(update, context):
    global keyboard

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Мова', # the only way to make it simple. don't detect user's language before, before it is chosen.
        reply_markup=reply_markup
    )

    global logger
    logger.info("UkrDUZT Bot startup.")
    logger.info("Version: {}".format(bot_version))

    # simplified version of user counter,
    # use it, when this bot is released.
    # user_counter()

    return CHOOSING

# loads json language file.
def load_language(update, context):
    query = update.callback_query
    variant = query.data # callback data

    # `CallbackQueries` requires answer.
    # see https://core.telegram.org/bots/api#callbackquery.
    query.answer()
    
    user_lang = ''
    for lang_code in lang_codes: # oddly, 'update.message.from_user.language_code' doens't work
        if(variant == lang_code):
            user_lang = lang_code
    
    data = []
    file_dir = '.\\language\\' + user_lang + '.json'
    assert os.path.isfile(file_dir), 'Cannot find ' + file_dir

    with open(file_dir, 'r', encoding='utf-8') as f:
        data = json.load(f)
        global logger
        logger.info(file_dir + " loaded.")
        
    global start_message
    global help_message
    global language_changed_message
    global language_choose_message
    global feedback_message
    global feedback_thanks_message
    global version_message

    for key, value in data.items():
        # It might be refractored.
        if(key == "start"):
            start_message = value
        if (key == "help"):
            help_message = value
        if(key == "language"):
            language_changed_message = value
        if(key == "language_choose"):
            language_choose_message = value
        if(key == "feedback"):
            feedback_message = value
        if(key == "feedback_thanks"):
            feedback_thanks_message = value
        if(key == "version"):
            version_message = value

    query.edit_message_text(language_changed_message)

    return CHOOSING
    
@send_typing_action
def help(update, context):
    update.message.reply_text(help_message)

    return CHOOSING

@send_typing_action
def feedback(update, context):
    update.message.reply_text(feedback_message)
    
    return TYPING_REPLY

@send_typing_action
def feedback_thank(update, context):
    with open('feedback_list.txt', 'a') as file_handler:
        file_handler.writelines(update.message.text + '\n')

    update.message.reply_text(feedback_thanks_message)

    return CHOOSING

@send_typing_action
def version(update, context):
    update.message.reply_text(version_message + bot_version)
    
    return CHOOSING

# Select language message.
@send_typing_action
def language(update, context):
    
    global keyboard

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        language_choose_message,
        reply_markup=reply_markup
    )

    return CHOOSING

# Select language post-message.
@send_typing_action
def language_choose(update, context):
    query = update.callback_query
    variant = query.data

    # `CallbackQueries` requires answer.
    # see https://core.telegram.org/bots/api#callbackquery.
    query.answer()
    
    query.edit_message_text(language_changed_message)

    return CHOOSING

def display_start_message(update, context):
    update.message.reply_text(start_message)

    return CHOOSING

# stops the bot
def stop(update, context):
    global logger
    logger.info("UkrDUZT Bot shutdown")

    return SHUTDOWN

# Tool function for load_database() 
# From the perspective of privacy, it's imprudent to return InlineQueryResultAccount here
# which repsesents actual Telegram account, because it requires user's phone number. 
def create_account_template(fullname, username):
    return InlineQueryResultArticle(
            id=uuid4(),
            title=fullname,
            input_message_content=InputTextMessageContent(username)
            )

# Loads a database of teachers and students.
def load_database():
    accounts = []
    with open('student_teacher_list.txt', 'r') as file_handler:
        #splitlines deletes '\n' chars
        lines = file_handler.read().splitlines()

        # as much as there are lines in a file
        for i in lines:
            # divide lines into words, i.g. first is name, second is surname and third is nickname 
            word = i.split(' ')
            # create actual acticle
            accounts.append(create_account_template(word[0] + ' ' + word[1], word[2]))

    return accounts

def end_conv_handler(update, context):
    return ConversationHandler.END

# Load phofiles once for better performance
list_of_acticles = load_database()

def inlinequery(update, context):
    update.inline_query.answer(list_of_acticles)

def error(update, context):
    logger.error(f"Update {update} caused error {context.error}.")

def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    updater.dispatcher.add_handler(CallbackQueryHandler(load_language))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('language', language))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('version', version))
    updater.dispatcher.add_handler(CommandHandler('stop', stop))


    dp.add_handler(InlineQueryHandler(inlinequery))

    conv_handler = ConversationHandler(
            entry_points = [CommandHandler('feedback', feedback)],

            states = {
                TYPING_REPLY: [MessageHandler(Filters.text,
                                            feedback_thank)]
            },

            fallbacks=[MessageHandler(Filters.text, end_conv_handler)]
        )

    conv_handler2 = ConversationHandler(
            entry_points = [CommandHandler('language', language)],

            states = {
                CHOOSING: [MessageHandler(Filters.text,
                                            language_choose)]
            },

            fallbacks=[MessageHandler(Filters.text, start)]
        )


    conv_handler3 = ConversationHandler(
            entry_points = [CommandHandler('stop', stop)],

            states = {
                SHUTDOWN: [MessageHandler(Filters.text,
                                            ConversationHandler.WAITING)]
            },

            fallbacks=[MessageHandler(Filters.text, end_conv_handler)]
        )

    dp.add_handler(conv_handler)
    dp.add_handler(conv_handler2)
    dp.add_handler(conv_handler3)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()
    
if __name__ == '__main__':
    main()