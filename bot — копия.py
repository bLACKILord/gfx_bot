import telebot
from telebot import types
import os
from datetime import datetime

TOKEN = "7633787635:AAEoRpWKCjCt0RUpwoYB8tqoqEeDddUMJuM"
bot = telebot.TeleBot(TOKEN)

# База данных
admins = {5679626874: {"name": "Владелец", "added_at": datetime.now().strftime("%d.%m.%Y %H:%M")}}
orders = {}
password = "s1kauzb"
app_file = r"C:\Users\PC\Downloads\GFX Tool for Standoff 2_2.0_APKPure.rar"
admin_history = []

# Проверка файла
if not os.path.exists(app_file):
    print("❌ Ошибка: Файл APK не найден!")
    exit()

# ======================
# КОМАНДЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
# ======================

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("📲 Получить GFX Tool")
    markup.add(btn)
    
    bot.send_message(
        message.chat.id,
        "🔹 <b>GFX Tool для Standoff 2</b> 🔹\n"
        "Повышение FPS | Улучшение графики\n\n"
        "Нажмите кнопку ниже для получения:",
        reply_markup=markup,
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda m: m.text == "📲 Получить GFX Tool")
def request_gfx(message):
    user = message.from_user
    user_name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    user_tag = f"@{user.username}" if user.username else f"ID:{user.id}"
    
    orders[user.id] = {
        'status': 'ожидает',
        'username': user_tag,
        'name': user_name,
        'date': datetime.now().strftime("%d.%m.%Y %H:%M")
    }
    
    # Уведомление админам
    for admin_id in admins:
        bot.send_message(
            admin_id,
            f"🆕 <b>Новая заявка от {user_name} ({user_tag})</b>\n"
            f"📅 Дата: {orders[user.id]['date']}\n"
            f"🆔 ID: <code>{user.id}</code>\n\n"
            f"✅ Одобрить: /approve_{user.id}\n"
            f"❌ Отклонить: /reject_{user.id}",
            parse_mode='HTML'
        )
    
    bot.reply_to(message, "✅ Заявка принята! Ожидайте одобрения администратора.")

# ======================
# АДМИН-СИСТЕМА
# ======================

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id not in admins:
        bot.reply_to(message, "🚫 Доступ запрещен!")
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("📜 Список заявок", callback_data="show_requests"),
        types.InlineKeyboardButton("📊 История админов", callback_data="admin_history")
    )
    
    admin_list = "\n".join(
        f"{data['name']} (ID: {admin_id}) - {data['added_at']}"
        for admin_id, data in admins.items()
    )
    
    bot.send_message(
        message.chat.id,
        f"⚙️ <b>Админ-панель</b>\n\n"
        f"👑 Текущие админы:\n{admin_list}\n\n"
        f"Последние изменения:\n" + "\n".join(admin_history[-3:]) if admin_history else "Нет истории",
        reply_markup=markup,
        parse_mode='HTML'
    )

# Добавление админа
@bot.message_handler(commands=['addadmin'])
def add_admin_command(message):
    if message.from_user.id not in admins:
        bot.reply_to(message, "🚫 Только админы могут добавлять других админов!")
        return
    
    try:
        if message.reply_to_message:
            new_admin = message.reply_to_message.from_user
            new_admin_id = new_admin.id
            new_admin_name = f"{new_admin.first_name} {new_admin.last_name}" if new_admin.last_name else new_admin.first_name
        else:
            args = message.text.split()
            if len(args) < 3:
                raise ValueError
            new_admin_id = int(args[1])
            new_admin_name = " ".join(args[2:])
        
        if new_admin_id in admins:
            bot.reply_to(message, "⚠️ Этот пользователь уже админ!")
            return
            
        admins[new_admin_id] = {
            "name": new_admin_name,
            "added_at": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        
        history_entry = f"{datetime.now().strftime('%d.%m %H:%M')} - Добавлен {new_admin_name} (ID: {new_admin_id})"
        admin_history.append(history_entry)
        
        # Уведомление новому админу
        try:
            bot.send_message(
                new_admin_id,
                f"🎉 Вы стали администратором!\n\n"
                f"Доступные команды:\n"
                f"/admin - панель управления\n"
                f"/addadmin [ID] [Имя] - добавить админа\n"
                f"/approve_[ID] - одобрить заявку"
            )
        except:
            pass
            
        bot.reply_to(message, f"✅ {new_admin_name} добавлен как админ!\nИстория: {history_entry}")
        
    except ValueError:
        bot.reply_to(message, "ℹ️ Формат:\n1. Ответьте на сообщение пользователя\n2. Или: /addadmin [ID] [Имя Фамилия]")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

# Одобрение заявки
@bot.message_handler(func=lambda m: m.text.startswith('/approve_'))
def approve_request(message):
    if message.from_user.id not in admins:
        return
    
    try:
        user_id = int(message.text.split('_')[1])
        if orders[user_id]['status'] == 'ожидает':
            orders[user_id]['status'] = 'одобрено'
            
            with open(app_file, 'rb') as f:
                bot.send_document(
                    user_id,
                    f,
                    caption=f"🎮 <b>Ваша заявка одобрена администратором {admins[message.from_user.id]['name']}!</b>\n\n"
                           "📌 Инструкция:\n"
                           "1. Скачайте файл\n"
                           "2. Включите 'Неизвестные источники'\n"
                           "3. Установите приложение",
                    parse_mode='HTML'
                )
            
            bot.reply_to(
                message,
                f"✅ Файл отправлен {orders[user_id]['name']} ({orders[user_id]['username']})"
            )
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

print("🟢 Бот запущен!")
print(f"👑 Админы: {admins}")
bot.polling()