from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TOKEN = "8052426936:AAE7RyPRibGoEub6fLliFHMbyqOaqhMEczM"

async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id  # Obtén el ID del chat
    await update.message.reply_text(f"Tu ID de chat es: {chat_id}")

def main():
    # Crea la aplicación con el token
    app = Application.builder().token(TOKEN).build()

    # Añade un manejador para el comando '/start'
    app.add_handler(CommandHandler("start", start))

    # Ejecuta el bot
    app.run_polling()

if __name__ == "__main__":
    main()
