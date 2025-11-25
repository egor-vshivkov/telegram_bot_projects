from config import TOKEN
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, MessageHandler, CommandHandler, ContextTypes,
    filters, CallbackQueryHandler, ConversationHandler
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет. Как тебя зовут?')
    return 1


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f'Привет, {user_text}')

    keyboard = [
        [
            InlineKeyboardButton("Помощь", callback_data="help"),
            InlineKeyboardButton("Угадай число", callback_data="guess")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выбери команду кнопками ниже:",
        reply_markup=markup
    )
    return ConversationHandler.END


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await help_command(query, context)
    elif query.data == "guess":
        await guess_start(query, context)


async def help_command(update_or_query, context):
    message = update_or_query.message if hasattr(update_or_query, "message") else update_or_query
    await message.reply_text(
        "Список команд:\n"
        "/start – начать общение\n"
        "/guess – игра 'Угадай число'\n"
        "/help – помощь"
    )


async def guess_start(update_or_query, context):
    number = random.randint(1, 10)
    context.user_data["guess_number"] = number
    context.user_data["guess_state"] = True

    message = update_or_query.message if hasattr(update_or_query, "message") else update_or_query
    await message.reply_text("Я загадал число от 1 до 10. Попробуй угадать!")


async def guess_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("guess_state"):
        return

    try:
        user_num = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Нужно ввести число 😄")
        return

    correct = context.user_data["guess_number"]

    if user_num == correct:
        await update.message.reply_text("Угадал! Красавчик 😎")
        context.user_data["guess_state"] = False
    else:
        await update.message.reply_text("Нет, попробуй ещё!")


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, hello)]},
    fallbacks=[]
)

application = Application.builder().token(TOKEN).build()
application.add_handler(conv_handler)
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("guess", guess_start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess_process))
application.run_polling()
