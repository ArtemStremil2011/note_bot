from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from work_with_db import DataBase
from keyboards import get_main_keyboard, get_cancel_keyboard, get_posts_keyboard, get_delete_posts_keyboard

class Post_adder(StatesGroup):
    post_name = State()
    post_text = State()
    update_old_post = State()
    update_post_name = State()
    update_post_text = State()

class TgBot:
    # инициализация нужных объектов
    def __init__(self, token):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.db = DataBase("usders.db")
        self._register_handlers()
    
    # функция для обработки событий
    def _register_handlers(self):
        # Регистрируем обработчики
        self.dp.message(Command("help"))(self.cmd_help)
        self.dp.message(Command("add_post"))(self.add_post_first)
        self.dp.message(Command("update_post"))(self.update_post_first)
        self.dp.message(Command("delete_post"))(self.delete_post_first)
        self.dp.message(Command("select_post"))(self.select_post_first)
        self.dp.message(CommandStart())(self.cmd_start)
        self.dp.message(Post_adder.post_name)(self.add_post_second)
        self.dp.message(Post_adder.post_text)(self.add_post_three)
        self.dp.message(Post_adder.update_old_post)(self.update_post_second)
        self.dp.message(Post_adder.update_post_name)(self.update_post_third)
        self.dp.message(Post_adder.update_post_text)(self.update_post_fourth)
        
        # Обработчики для текстовых кнопок
        self.dp.message(F.text == "📝 Создать")(self.add_post_first)
        self.dp.message(F.text == "👁️ Прочитать")(self.select_post_first)
        self.dp.message(F.text == "✏️ Изменить")(self.update_post_first)
        self.dp.message(F.text == "🗑️ Удалить")(self.delete_post_first)
        self.dp.message(F.text == "❌ Отмена")(self.cancel_action)
        
        # Обработчики для инлайн кнопок
        self.dp.callback_query(F.data.startswith("read_post:"))(self.handle_read_post)
        self.dp.callback_query(F.data.startswith("update_post:"))(self.handle_update_post)
        self.dp.callback_query(F.data.startswith("delete_post:"))(self.handle_delete_post)
        self.dp.callback_query(F.data == "cancel")(self.handle_cancel)
        
    # обработчик команды "help"
    async def cmd_help(self, message: Message):
        await message.answer("Помощь", reply_markup=get_main_keyboard())

    # обработчик команды "/start"
    async def cmd_start(self, message: Message):
        await message.answer(
            "Привет! Я бот для управления вашими записями.\n\n"
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )

    # обработчик кнопки "Отмена" (для текстовых кнопок)
    async def cancel_action(self, message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Действие отменено", reply_markup=get_main_keyboard())

    # обработчик отмены для инлайн кнопок
    async def handle_cancel(self, callback: CallbackQuery, state: FSMContext):
        await state.clear()
        await callback.message.edit_text("Действие отменено")
        await callback.message.answer("Выберите действие:", reply_markup=get_main_keyboard())

    # обработчик чтения поста из инлайн кнопки
    async def handle_read_post(self, callback: CallbackQuery):
        post_name = callback.data.split(":")[1]
        
        post_data = self.db.get_data(
            "users",
            "user_post_text",
            f"WHERE user_id = {callback.from_user.id} AND user_post_name = '{post_name}'"
        )
        
        if post_data and post_data[0][0]:
            await callback.message.edit_text(f"📖 {post_name}\n\n{post_data[0][0]}")
        else:
            await callback.message.edit_text("Запись не найдена")
        
        await callback.message.answer("Выберите действие:", reply_markup=get_main_keyboard())

    # обработчик выбора поста для редактирования из инлайн кнопки
    async def handle_update_post(self, callback: CallbackQuery, state: FSMContext):
        post_name = callback.data.split(":")[1]
        await state.update_data(old_post_name=post_name)
        await state.set_state(Post_adder.update_post_name)
        
        await callback.message.edit_text(f"Редактирование: {post_name}\nВведите новый заголовок:")
        await callback.message.answer("Или нажмите 'Отмена'", reply_markup=get_cancel_keyboard())

    # обработчик удаления поста из инлайн кнопки
    async def handle_delete_post(self, callback: CallbackQuery):
        post_name = callback.data.split(":")[1]
        
        self.db.delete_data(
            "users", 
            f"WHERE user_id = {callback.from_user.id} AND user_post_name = '{post_name}'"
        )
        
        await callback.message.edit_text(f"✅ Запись '{post_name}' удалена!")
        await callback.message.answer("Выберите действие:", reply_markup=get_main_keyboard())

    async def add_post_first(self, message: Message, state: FSMContext):
        await state.set_state(Post_adder.post_name)
        await message.answer("Введите заголовок записи:", reply_markup=get_cancel_keyboard())

    async def add_post_second(self, message: Message, state: FSMContext):
        if message.text == "❌ Отмена":
            await message.answer("Действие отменено", reply_markup=get_main_keyboard())
            return
        else:
            await state.update_data(post_name=message.text)
            await state.set_state(Post_adder.post_text)
            await message.answer("Введите текст записи:", reply_markup=get_cancel_keyboard())

    async def add_post_three(self, message: Message, state: FSMContext):
        await state.update_data(post_text=message.text)
        data = await state.get_data()
        
        self.db.send_data("users", (
            message.from_user.id, 
            message.from_user.full_name, 
            data.get('post_name'), 
            data.get('post_text')
        ))
        
        await message.answer("История создана", reply_markup=get_main_keyboard())
        await state.clear()

    async def update_post_first(self, message: Message, state: FSMContext):
        # Получаем список записей пользователя
        user_posts = self.db.get_data(
            "users", 
            "user_post_name", 
            f"WHERE user_id = {message.from_user.id}"
        )
        
        if not user_posts:
            await message.answer("У вас пока нет записей", reply_markup=get_main_keyboard())
            return
        
        # Показываем инлайн клавиатуру с записями
        keyboard = get_posts_keyboard(user_posts, "update")
        await message.answer("Выберите запись для редактирования:", reply_markup=keyboard)

    async def update_post_second(self, message: Message, state: FSMContext):
        await state.update_data(old_post_name=message.text)
        await state.set_state(Post_adder.update_post_name)
        await message.answer("Введите новый заголовок записи:", reply_markup=get_cancel_keyboard())

    async def update_post_third(self, message: Message, state: FSMContext):
        await state.update_data(new_post_name=message.text)
        await state.set_state(Post_adder.update_post_text)
        await message.answer("Введите новый текст записи:", reply_markup=get_cancel_keyboard())

    async def update_post_fourth(self, message: Message, state: FSMContext):
        await state.update_data(new_post_text=message.text)
        data = await state.get_data()

        self.db.update_data(
            "users", 
            "user_post_name", 
            data.get('new_post_name'), 
            f"WHERE user_id={message.from_user.id} AND user_post_name='{data.get('old_post_name')}'"
        )
        
        self.db.update_data(
            "users", 
            "user_post_text", 
            data.get('new_post_text'), 
            f"WHERE user_id={message.from_user.id} AND user_post_name='{data.get('new_post_name')}'"
        )
        
        await message.answer("Запись обновлена", reply_markup=get_main_keyboard())
        await state.clear()

    async def delete_post_first(self, message: Message):
        # Получаем список записей пользователя
        user_posts = self.db.get_data(
            "users", 
            "user_post_name", 
            f"WHERE user_id = {message.from_user.id}"
        )
        
        if not user_posts:
            await message.answer("У вас пока нет записей", reply_markup=get_main_keyboard())
            return
        
        # Показываем инлайн клавиатуру для удаления
        keyboard = get_delete_posts_keyboard(user_posts)
        await message.answer("Выберите запись для удаления:", reply_markup=keyboard)

    async def select_post_first(self, message: Message):
        # Получаем список записей пользователя
        user_posts = self.db.get_data(
            "users", 
            "user_post_name", 
            f"WHERE user_id = {message.from_user.id}"
        )
        
        if not user_posts:
            await message.answer("У вас пока нет записей", reply_markup=get_main_keyboard())
            return
        
        # Показываем инлайн клавиатуру для чтения
        keyboard = get_posts_keyboard(user_posts, "read")
        await message.answer("Выберите запись для чтения:", reply_markup=keyboard)

    # основная функция
    async def start_bot(self):
        await self.dp.start_polling(self.bot)