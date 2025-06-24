import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command

API_TOKEN = os.getenv("7414576699:AAHP4eU4XQ0GkcwbmuFSFQzYVHyZOpISuBg")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

tracked_words = set()
stats = {}
ADMIN_IDS = {123456789}  # заміни на свій ID

def is_admin(user_id):
    return user_id in ADMIN_IDS

@dp.message_handler(commands=['addword'])
async def add_word(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.reply("Тільки адміністратори можуть додавати слова.")
        return
    word = message.get_args().strip().lower()
    if not word:
        await message.reply("Вкажи слово, яке потрібно додати.")
        return
    tracked_words.add(word)
    await message.reply(f"Слово '{word}' додано до списку відстеження.")

@dp.message_handler(commands=['removeword'])
async def remove_word(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.reply("Тільки адміністратори можуть видаляти слова.")
        return
    word = message.get_args().strip().lower()
    if not word:
        await message.reply("Вкажи слово, яке потрібно видалити.")
        return
    if word in tracked_words:
        tracked_words.remove(word)
        await message.reply(f"Слово '{word}' видалено зі списку.")
    else:
        await message.reply(f"Слова '{word}' у списку немає.")

@dp.message_handler(commands=['listwords'])
async def list_words(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.reply("Тільки адміністратори можуть бачити список слів.")
        return
    if not tracked_words:
        await message.reply("Список відстежуваних слів порожній.")
        return
    await message.reply("Відстежувані слова:\n" + ", ".join(sorted(tracked_words)))

@dp.message_handler()
async def count_words(message: types.Message):
    text = (message.text or "").lower()
    user_id = message.from_user.id

    for word in tracked_words:
        count = text.count(word)
        if count > 0:
            if user_id not in stats:
                stats[user_id] = {}
            if word not in stats[user_id]:
                stats[user_id][word] = 0
            stats[user_id][word] += count

@dp.message_handler(commands=['stats'])
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.reply("Тільки адміністратори можуть дивитися статистику.")
        return
    if not stats:
        await message.reply("Статистика поки відсутня.")
        return

    lines = []
    for user_id_key, words in stats.items():
        try:
            user = await bot.get_chat(user_id_key)
            name = user.full_name
        except:
            name = str(user_id_key)
        for word, count in words.items():
            lines.append(f"{name}: '{word}' вжито {count} разів")

    if not lines:
        await message.reply("Статистика поки відсутня.")
        return

    chunk_size = 3500
    text = "\n".join(lines)
    for i in range(0, len(text), chunk_size):
        await message.reply(text[i:i+chunk_size])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
