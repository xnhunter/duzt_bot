# UkrDUZT Bot Utils for Telegram
# Copyright ⓒ 2020 Valentyn Bondarenko. All rights reserved.

from telegram import ChatAction
from functools import wraps

bot_user_number = 0

def send_action(action):
    """Sends `action` while processing func command."""
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator

# Simplified version of the function that counts bot's users.
# Place it into the start func.
def user_counter():
    global bot_user_number
    bot_user_number += 1

    return bot_user_number

# Send 'typing...' from the bot's side in chat
send_typing_action = send_action(ChatAction.TYPING)