from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Основная клавиатура с основными действиями
def get_main_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(text="📝 Создать"),
        KeyboardButton(text="👁️ Прочитать"),
        KeyboardButton(text="✏️ Изменить"),
        KeyboardButton(text="🗑️ Удалить")
    )
    keyboard.adjust(2)  # 2 кнопки в ряд
    return keyboard.as_markup(resize_keyboard=True)

# Клавиатура для отмены действия
def get_cancel_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="❌ Отмена"))
    return keyboard.as_markup(resize_keyboard=True)

# Инлайн клавиатура со списком статей пользователя
def get_posts_keyboard(posts, action_type="read"):
    """
    Создает инлайн клавиатуру со списком статей
    
    :param posts: список статей из БД [(post_name1,), (post_name2,), ...]
    :param action_type: тип действия - 'read' или 'update'
    """
    keyboard = InlineKeyboardBuilder()
    
    for post in posts:
        post_name = post[0]  # Извлекаем название статьи из кортежа
        if action_type == "read":
            callback_data = f"read_post:{post_name}"
            button_text = f"📖 {post_name}"
        else:  # update
            callback_data = f"update_post:{post_name}"
            button_text = f"✏️ {post_name}"
        
        keyboard.add(InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        ))
    
    keyboard.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel"
    ))
    
    keyboard.adjust(1)  # По одной кнопке в ряд
    return keyboard.as_markup()

# Инлайн клавиатура для выбора статьи для удаления
def get_delete_posts_keyboard(posts):
    """
    Создает инлайн клавиатуру для удаления статей
    """
    keyboard = InlineKeyboardBuilder()
    
    for post in posts:
        post_name = post[0]
        keyboard.add(InlineKeyboardButton(
            text=f"🗑️ {post_name}",
            callback_data=f"delete_post:{post_name}"
        ))
    
    keyboard.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel"
    ))
    
    keyboard.adjust(1)
    return keyboard.as_markup()