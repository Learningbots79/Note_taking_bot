from pyrogram import Client, filters
from pyrogram.types import Message
from config import BOT_TOKEN, API_ID, API_HASH
from database import load_notes, save_notes, delete_notes, add_notes, get_user_notes, edit_notes

note_states = {}
user_states = {}


app = Client(
    "notes_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
    )

# == START COMMAND == 
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text(
        "Hey! This is a Notes Taking bot 📒\n\n"
        "Use the following commands:\n"
        "/add <your note> - to save a note\n"
        "/show - to view your notes\n"
        "/delete - to delete a note\n"
        "/edit - to edit a note\n"
        "/cancel - to cancel current action"

    )

# == SHOW COMMAND ==
@app.on_message(filters.command("show"))
async def show(client, message: Message):
    user_id = message.from_user.id
    data = get_user_notes(user_id)

    if not data:
        await message.reply_text("📁 You have no saved notes yet")
        return
    
    text = "Your Notes 📄\n\n"
    for idx, notes in enumerate(data, 1):
        text += f"{idx}. {notes}\n"
        
    await message.reply_text(text)

# == ADD COMMAND ==
@app.on_message(filters.command("add"))
async def add_comand(client, message: Message):
    note_text = message.text.split(" ", 1)
    if len(note_text) < 2:
        return await message.reply_text("⚒️ Please write note after /add command.\n\n Example : /add Buy a laptop")
    
    user_id = message.from_user.id
    note = note_text[1]

    add_notes(user_id, note)
    await message.reply_text("✅ Note saved")

# == DELETE NOTES ==
@app.on_message(filters.command("delete"))
async def delete_command(client, message: Message):
    user_id = message.from_user.id
    data = get_user_notes(user_id)

    if not data:
        await message.reply_text("You didn't saved any note ❌")
        return
    
    text = f"Your Notes 📁\n\n"
    for idx, note in enumerate(data, 1):
        text += f"{idx}. {note}\n"
    
    text += "\nSend number which note you want to delete 🗑️"
    await message.reply_text(text)

    user_states[user_id] = "delete_awaiting"

# == EDIT COMMAND ==
@app.on_message(filters.command("edit"))
async def edit_command(client, message: Message):
    user_id = message.from_user.id
    data = get_user_notes(user_id)

    if not data:
        await message.reply_text("You didn't saved note to edit ⚠️")
        return

    text = "Your Notes 📁\n\n"
    for idx, note in enumerate(data, 1):
        text += f"{idx}. {note}"
    
    text += "\n\n send number which note you want to edit 📃"
    await message.reply_text(text)

    user_states[user_id] = "editing_awaiting"

# == MESSAGE HANDLER ==
@app.on_message(filters.text & ~filters.command(["start", "add", "edit", "delete", "cancel", "show"]))
async def message_handler(client, message: Message):
    user_id = message.from_user.id
    states = user_states.get(user_id)

    if states == "delete_awaiting":
        data = get_user_notes(user_id)
        if not data:
            return

        try:
            index = int(message.text.strip()) - 1
        except ValueError:
            await message.reply_text("❌ Please send a valid number.")
            return

        if 0 <= index < len(data):
            delete_notes(user_id, index)
            await message.reply_text("🗑️ Note deleted.")
        else:
            await message.reply_text("❌ Invalid note number.")

        user_states.pop(user_id, None)

    elif states == "editing_awaiting":
        try:
            index = int(message.text.strip()) - 1
        except ValueError:
            await message.reply_text("❌ Please send a valid note number.")
            return

        notes = get_user_notes(user_id)
        if 0 <= index < len(notes):
            note_states[user_id] = index
            user_states[user_id] = "editing_context"
            await message.reply_text(f"✏️ Send the new content for note {index + 1}:")
        else:
            await message.reply_text("❌ Invalid note number.")

    elif states == "editing_context":
        new_text = message.text.strip()
        index = note_states.get(user_id)
        
        if index is not None:
            edit_notes(user_id, index, new_text)
            await message.reply_text("✅ Note updated successfully.")

        user_states.pop(user_id, None)
        note_states.pop(user_id, None)

# == CANCEL COMMAND ==
@app.on_message(filters.command("cancel"))
async def cancel(client, message: Message):
    user_id = message.from_user.id
    if user_id in note_states or user_id in user_states:
        user_states.pop(user_id, None)
        note_states.pop(user_id, None)
        await message.reply_text("✅ Action cancelled.")
    else:
        await message.reply_text("ℹ️ Nothing to cancel.")


app.run()