import telebot
from telebot import types
import os

API_TOKEN = '8240574797:AAEg40Vtww20_XJh1Hu3OEeNgXu6iLjzH6c'
bot = telebot.TeleBot(API_TOKEN)

class CalorieRecord:
    def __init__(self, name, value):
        self._name = name        
        self.__value = value     

    @property 
    def value(self):
        return self.__value

    def get_change(self):
        return self.__value

    def __str__(self): 
        return f"{self._name}: {self.__value} ккал"

class FoodRecord(CalorieRecord):
    def get_change(self):
        return self.value        

class ExerciseRecord(CalorieRecord):
    def get_change(self):
        return -self.value       

user_data = {}

FAQ_RESPONSES = {
    "огурец": "🥒 Огурец свежий: ~15 ккал на 100г. Отличный диетический продукт!",
    "помидор": "🍅 Помидор: ~18 ккал на 100г. Богат ликопином.",
    "банан": "🍌 Банан: ~89 ккал на 100г. Хороший источник калия.",
    "курица": "🍗 Куриное филе (вареное): ~170 ккал на 100г. Чистый белок!",
    "яблоко": "🍏 Яблоко: ~52 ккал на 100г. Много клетчатки.",
    "яйцо": "🥚 Яйцо вареное (1 шт): ~75 ккал. Содержит полезные жиры.",
    "бег": "🏃 Бег трусцой: сжигает около 600 ккал за 1 час.",
    "ходьба": "🚶 Шаги/Ходьба: сжигает около 250-300 ккал за 1 час.",
    "плавание": "🏊 Плавание: сжигает около 500 ккал за 1 час тренировки.",
    "велосипед": "🚴 Велосипед: сжигает около 450 ккал за 1 час средней езды.",
    "вода": "💧 Вода содержит 0 ккал. Рекомендуется пить 1.5-2 литра в день.",
    "сон": "😴 Во время сна человек сжигает около 60-70 ккал за один час."
}

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_food = types.KeyboardButton("🍏 Добавить еду")
    btn_burn = types.KeyboardButton("🏃 Добавить тренировку")
    btn_status = types.KeyboardButton("📊 Баланс калорий")
    btn_clear = types.KeyboardButton("🗑 Очистить дневник")
    markup.row(btn_food, btn_burn)
    markup.row(btn_status, btn_clear)
    return markup

def save_to_file(user_id, text):
    with open("history.txt", "a", encoding="utf-8") as f:
        f.write(f"User {user_id}: {text}\n")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    uid = message.from_user.id
    if uid not in user_data:
        user_data[uid] = [] 
    save_to_file(uid, "Запустил бота")
    bot.send_message(
        message.chat.id, 
        "🍏 Привет! Я твой счетчик калорий.\nИспользуй кнопки ниже или пиши продукты (например: банан, огурец, бег):",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "🍏 Добавить еду" or msg.text.startswith('/food'))
def add_food_handler(message):
    if message.text.startswith('/food '):
        process_food_step(message, from_command=True)
        return
    msg = bot.reply_to(message, "Введите название еды и калории через пробел.\nПример: `Банан 90`", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_food_step)

def process_food_step(message, from_command=False):
    uid = message.from_user.id
    try:
        text = message.text
        if from_command:
            text = text.replace('/food ', '')
        args = text.split()
        if len(args) < 2: raise ValueError()
        
        # ✅ Исправлено здесь: берем 0-й элемент для имени и 1-й для калорий
        name = args[0]
        calories = int(args[1])
        if calories <= 0: raise ValueError()
        
        record = FoodRecord(name, calories)
        user_data.setdefault(uid, []).append(record)
        save_to_file(uid, f"Добавил еду {record}")
        bot.reply_to(message, f"✅ Добавлено в еду: {record}", reply_markup=get_main_keyboard())
    except:
        bot.reply_to(message, "❌ Ошибка формата! Напишите через пробел: `Яблоко 50`", reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "🏃 Добавить тренировку" or msg.text.startswith('/burn'))
def add_burn_handler(message):
    if message.text.startswith('/burn '):
        process_burn_step(message, from_command=True)
        return
    msg = bot.reply_to(message, "Введите вид активности и калории через пробел.\nПример: `Бег 300`", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_burn_step)

def process_burn_step(message, from_command=False):
    uid = message.from_user.id
    try:
        text = message.text
        if from_command:
            text = text.replace('/burn ', '')
        args = text.split()
        if len(args) < 2: raise ValueError()
        
        # ✅ Исправлено здесь: берем 0-й элемент для имени и 1-й для калорий
        name = args[0]
        calories = int(args[1])
        if calories <= 0: raise ValueError()
        
        record = ExerciseRecord(name, calories)
        user_data.setdefault(uid, []).append(record)
        save_to_file(uid, f"Добавил тренировку {record}")
        bot.reply_to(message, f"🔥 Записано в тренировки: Сгорело {record}", reply_markup=get_main_keyboard())
    except:
        bot.reply_to(message, "❌ Ошибка формата! Напишите через пробел: `Бег 300`", reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "📊 Баланс калорий" or msg.text == '/status')
def show_status_handler(message):
    uid = message.from_user.id
    records = user_data.get(uid, [])
    save_to_file(uid, "Запросил баланс калорий")
    if not records:
        bot.reply_to(message, "📊 Твой дневник пока пуст.", reply_markup=get_main_keyboard())
        return
    total_eat = 0
    total_burn = 0
    balance = 0
    for r in records:
        balance += r.get_change() 
        if isinstance(r, FoodRecord):
            total_eat += r.value
        else:
            total_burn += r.value
    bot.reply_to(
        message, 
        f"📊 **Итоги текущего дня:**\n\n📥 Получено с едой: {total_eat} ккал\n🏃 Сгорело при тренировках: {total_burn} ккал\n⚖️ Итоговый баланс: **{balance} ккал**",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda msg: msg.text == "🗑 Очистить дневник" or msg.text == '/clear')
def clear_data_handler(message):
    uid = message.from_user.id
    user_data[uid] = []
    save_to_file(uid, "Очистил дневник")
    bot.reply_to(message, "🗑 Все записи дневника успешно удалены!", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda msg: True)
def handle_unknown_text(message):
    uid = message.from_user.id
    word = message.text.lower().strip()
    if word in FAQ_RESPONSES:
        save_to_file(uid, f"Запросил FAQ: {word}")
        bot.reply_to(message, FAQ_RESPONSES[word], reply_markup=get_main_keyboard())
    else:
        save_to_file(uid, f"Неизвестный ввод: {message.text}")
        bot.reply_to(message, "🤔 Я не распознал команду и этого нет в справочнике. Пожалуйста, используйте кнопки или напишите базовый продукт (огурец, яблоко, бег).", reply_markup=get_main_keyboard())

if __name__ == '__main__':
    try:
        bot.set_my_commands([
            telebot.types.BotCommand("start", "Запустить бота"),
            telebot.types.BotCommand("food", "Добавить еду"),
            telebot.types.BotCommand("burn", "Добавить тренировку"),
            telebot.types.BotCommand("status", "Показать баланс"),
            telebot.types.BotCommand("clear", "Очистить дневник"),
            telebot.types.BotCommand("help", "Справка")
        ])
    except:
        pass
    bot.infinity_polling()
