# UkrDUZT Bot for Telegram
# Copyright ⓒ 2020 Valentyn Bondarenko. All rights reserved.

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction, ReplyKeyboardMarkup, InlineQueryResultArticle,  \
    InputTextMessageContent, ParseMode, InlineQueryResultContact, InputContactMessageContent, InlineQueryResultVenue, InputMediaPhoto
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler, ConversationHandler, InlineQueryHandler
from telegram.utils.helpers import escape_markdown

from duzt_bot_utils import send_typing_action, user_counter

from uuid import uuid4
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename="log.txt")

bot_version = '0.8.5 Beta'
bot_token = 'Token'

CHOOSING, TYPING_REPLY = range(2)

@send_typing_action
def start(update, context):
    #NOTE: In Debug mode, the emoji below causes dozens of warnings. 
    #      Using emoji module doesn't change a thing, so simply delete
    #      this emojie to debug surely or reduce debug level to logging.INFO.
    update.message.reply_text(("Привет, {}😌 \n\nИногда нужно быстро связатся с преподавателем чтобы предупредить об отсутствии или узнать что-либо у студента из другой группы. \n\nНапиши @duztbot + имя фамилию студента или преподавателя.\
      \nБаза постоянно пополняется. Для подробностей отправьте мне /help или /feeedback, чтобы оставить отзыв."
                               .format(update.message.from_user.first_name)))

    # simplified version of user counter
    print(user_counter())

    return CHOOSING

@send_typing_action
def help(update, context):
    update.message.reply_text("Больше нет необходимости искать  одного одногруппника в списках десятков групп. \
     \n\nПомогу тебе быстро найти твоих одногруппников и преподавателей со всего УкрДУЗТ😉")

    return CHOOSING

@send_typing_action
def feedback(update, context):
    update.message.reply_text("Как тебе мой аватар? Напишите все, что тебе понравилось или не понравилось моей работе.")
    
    return TYPING_REPLY

@send_typing_action
def feedback_thank(update, context):
    with open('feedback_list.txt', 'a') as file_handler:
        file_handler.writelines(update.message.text + '\n')

    update.message.reply_text("Спасибо за оставленный отзыв. Отзывы помагают нам писать более функциональные программы.😌")

    return CHOOSING

@send_typing_action
def version(update, context):
    update.message.reply_text('Версия бота: {}.'.format(bot_version))
    
    return CHOOSING

# Tool function for load_database() 
# From the perspective of privacy, it's imprudent to return InlineQueryResultAccount here
# which repsesents actual Telegram account, because it requires user's phone number. 
def create_account_template(fullname, username):
    return InlineQueryResultArticle(
            id=uuid4(),
            title=fullname,
            input_message_content=InputTextMessageContent(username)
            )

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
    logger.warning(f"Update {update} caused error {context.error}.")

def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('version', version))
    updater.dispatcher.add_handler(CommandHandler('help', help))

    dp.add_handler(InlineQueryHandler(inlinequery))

    conv_handler = ConversationHandler(
            entry_points=[CommandHandler('feedback', feedback)],

            states={
                TYPING_REPLY: [MessageHandler(Filters.text,
                                            feedback_thank)]
            },

            fallbacks=[MessageHandler(Filters.text, end_conv_handler)]
        )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()