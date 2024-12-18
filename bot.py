from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, filters

# --- Bot Data ---
welcome_message = (
    "*Hey 👋🏻 !*\n\n"
    "~Welcome To Super Raja Predictions From Here You Can Access For the Predictions for Rajaluck Platform.~\n"
    "~If you are new Kindly Connect Your Rajaluck Account With Bot To Proceed~\n\n"
    "*How to Connect 🤔 ?*\n"
    "~🔰 Go To Rajaluck Profile\n🔰 Copy Uid\n🔰 Open This Bot Share Your UID In the Below Format~\n"
    "`/connect {UID}`\n\n"
    "*Then Start Receiving Predictions on Time 👍*"
)

admin_group = None
database_channel = None
users = {}  # Format: {UID: {'telegram_id': ID, 'username': username, 'status': active/blocked}}

# --- Command Handlers ---
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def setwelcome(update: Update, context: CallbackContext):
    global welcome_message
    welcome_message = " ".join(context.args)
    await update.message.reply_text("Welcome message has been updated!")


async def rmwelcome(update: Update, context: CallbackContext):
    global welcome_message
    welcome_message = (
        "*Hey 👋🏻 !*\n\n"
        "~Welcome To Super Raja Predictions From Here You Can Access For the Predictions for Rajaluck Platform.~\n"
        "~If you are new Kindly Connect Your Rajaluck Account With Bot To Proceed~\n\n"
        "*How to Connect 🤔 ?*\n"
        "~🔰 Go To Rajaluck Profile\n🔰 Copy Uid\n🔰 Open This Bot Share Your UID In the Below Format~\n"
        "`/connect {UID}`\n\n"
        "*Then Start Receiving Predictions on Time 👍*"
    )
    await update.message.reply_text("Welcome message has been reset to default!")


async def connect(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Please provide your UID in the correct format: `/connect {UID}`", parse_mode="Markdown")
        return
    
    game_uid = context.args[0]
    user_info = {
        "telegram_id": update.message.chat.id,
        "username": update.message.chat.username,
        "status": "pending"
    }
    users[game_uid] = user_info

    if admin_group:
        buttons = [
            [InlineKeyboardButton("Accept", callback_data=f"accept|{game_uid}"), 
             InlineKeyboardButton("Reject", callback_data=f"reject|{game_uid}")]
        ]
        await context.bot.send_message(
            admin_group,
            f"*New User Connection*\n\nUsername: @{update.message.chat.username}\n"
            f"Profile: [Link](tg://user?id={update.message.chat.id})\nGame UID: `{game_uid}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await update.message.reply_text("Verification under process, please wait patiently.")
    else:
        await update.message.reply_text("Admin panel is not linked. Please contact the admin.")


async def apconnect(update: Update, context: CallbackContext):
    global admin_group
    if len(context.args) != 1:
        await update.message.reply_text("Please provide the group ID in the correct format: `/apconnect {Group ID}`")
        return

    admin_group = context.args[0]
    await update.message.reply_text("Admin panel has been connected!")


async def dbconnect(update: Update, context: CallbackContext):
    global database_channel
    if len(context.args) != 1:
        await update.message.reply_text("Please provide the channel ID in the correct format: `/dbconnect {Channel ID}`")
        return

    database_channel = context.args[0]
    await update.message.reply_text("Database channel has been connected!")


async def broadcast(update: Update, context: CallbackContext):
    message = " ".join(context.args)
    for user in users.values():
        if user["status"] == "active":
            await context.bot.send_message(user["telegram_id"], message)
    await update.message.reply_text("Broadcast sent!")


async def block_user(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Provide UID to block: `/block {UID}`")
        return

    uid = context.args[0]
    if uid in users:
        users[uid]["status"] = "blocked"
        await context.bot.send_message(users[uid]["telegram_id"], "Your account has been blocked. Contact support.")
        await update.message.reply_text(f"User with UID {uid} has been blocked!")
    else:
        await update.message.reply_text(f"No user found with UID {uid}.")


async def unblock_user(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Provide UID to unblock: `/unblock {UID}`")
        return

    uid = context.args[0]
    if uid in users:
        users[uid]["status"] = "active"
        await context.bot.send_message(users[uid]["telegram_id"], "Your account has been unblocked.")
        await update.message.reply_text(f"User with UID {uid} has been unblocked!")
    else:
        await update.message.reply_text(f"No user found with UID {uid}.")


async def callback_query_handler(update: Update, context: CallbackContext):
    query = update.callback_query.data
    action, game_uid = query.split("|")
    if action == "accept":
        users[game_uid]["status"] = "active"
        await context.bot.send_message(users[game_uid]["telegram_id"], "Your Game account has been connected successfully!")
        if database_channel:
            await context.bot.send_message(database_channel, f"Accepted UID: {game_uid}")
    elif action == "reject":
        del users[game_uid]
        await context.bot.send_message(users[game_uid]["telegram_id"], "You are not eligible to receive the service. Contact support.")
    await update.callback_query.answer()


# --- Main Bot Initialization ---
def main():
    application = Application.builder().token("7988928214:AAGywHHBTfy1RYrT1zXTTFCrAOi79S9BqFE").build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setwelcome", setwelcome))
    application.add_handler(CommandHandler("rmwelcome", rmwelcome))
    application.add_handler(CommandHandler("connect", connect))
    application.add_handler(CommandHandler("apconnect", apconnect))
    application.add_handler(CommandHandler("dbconnect", dbconnect))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("block", block_user))
    application.add_handler(CommandHandler("unblock", unblock_user))

    # Callback Query Handler
    application.add_handler(CallbackQueryHandler(callback_query_handler))

    # Run the bot with `run_polling()`
    application.run_polling()

if __name__ == "__main__":
    main()
