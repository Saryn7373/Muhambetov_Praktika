import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# вопросы-ответы
QUESTIONS = [
    {
        "question": "Какой у вас характер?",
        "options": [
            ("Яркий и харизматичный", "trumpet"),
            ("Спокойный и надежный", "trombone"),
            ("Душа компании, но немного странный", "saxophone"),
            ("Серьезный и основательный", "tuba"),
        ],
    },
    {
        "question": "Какой жанр музыки вам ближе?",
        "options": [
            ("Джаз", "trumpet"),
            ("Классика", "french_horn"),
            ("Фанк/Соул", "trombone"),
            ("Военные марши", "sousaphone"),
        ],
    },
    {
        "question": "Какой ваш любимый напиток?",
        "options": [
            ("Энергетик", "trumpet"),
            ("Кофе", "clarinet"),
            ("Коктейль", "saxophone"),
            ("Пиво", "tuba"),
        ],
    },
    {
        "question": "Как вы проводите свободное время?",
        "options": [
            ("Выступаю на публике", "trumpet"),
            ("Читаю книги", "french_horn"),
            ("Общаюсь с друзьями", "trombone"),
            ("Отдыхаю в одиночестве", "bassoon"),
        ],
    },
]

INSTRUMENTS = {
    "trumpet": {
        "name": "Труба",
        "description": "Вы - труба! Яркий, громкий и всегда в центре внимания. "
        "Как и труба, вы любите быть на первом плане и заряжаете энергией всех вокруг.",
        "image": "https://brassbook.ru/images/trumpet.jpg",
    },
    "trombone": {
        "name": "Тромбон",
        "description": "Вы - тромбон! Душа компании с необычным характером. "
        "Как и тромбон, вы можете быть разным - то веселым и задорным, то глубоким и меланхоличным.",
        "image": "https://brassbook.ru/images/trombone.jpg",
    },
    "saxophone": {
        "name": "Саксофон",
        "description": "Вы - саксофон! Элегантный, стильный и немного загадочный. "
        "Как и саксофон, вы умеете подстраиваться под любую ситуацию, но всегда сохраняете свою индивидуальность.",
        "image": "https://brassbook.ru/images/saxophone.jpg",
    },
    "tuba": {
        "name": "Туба",
        "description": "Вы - туба! Надежный, основательный и немного философ. "
        "Как и туба, вы - фундамент любой компании, на вас можно положиться в любой ситуации.",
        "image": "https://brassbook.ru/images/tuba.jpg",
    },
    "french_horn": {
        "name": "Валторна",
        "description": "Вы - валторна! Утонченный и благородный. "
        "Как и валторна, вы цените красоту и гармонию во всем.",
        "image": "https://brassbook.ru/images/french_horn.jpg",
    },
    "sousaphone": {
        "name": "Сузафон",
        "description": "Вы - сузафон! Яркий, необычный и запоминающийся. "
        "Как и сузафон, вы не боитесь выделяться из толпы и идти своим путем.",
        "image": "https://brassbook.ru/images/sousaphone.jpg",
    },
    "clarinet": {
        "name": "Кларнет",
        "description": "Вы - кларнет! Умный, проницательный и немного загадочный. "
        "Как и кларнет, вы умеете находить нестандартные решения и видеть то, что скрыто от других.",
        "image": "https://brassbook.ru/images/clarinet.jpg",
    },
    "bassoon": {
        "name": "Фагот",
        "description": "Вы - фагот! Необычный, с чувством юмора и глубоким внутренним миром. "
        "Как и фагот, вы умеете удивлять и радовать окружающих своим нестандартным подходом к жизни.",
        "image": "https://brassbook.ru/images/bassoon.jpg",
    },
}


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! ✨\n"
        "Ответь на несколько вопросов, и я скажу, какой музыкальный инструмент из BrassBook тебе подходит!\n\n"
        "Нажми /test чтобы начать тест!"
    )


# /test
async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["test_answers"] = []
    context.user_data["current_question"] = 0
    await ask_question(update, context)


# вопрос
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question_data = QUESTIONS[context.user_data["current_question"]]
    keyboard = []

    for text, instrument in question_data["options"]:
        keyboard.append([InlineKeyboardButton(text, callback_data=instrument)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=f"Вопрос {context.user_data['current_question'] + 1}/{len(QUESTIONS)}:\n\n{question_data['question']}",
            reply_markup=reply_markup,
        )
    else:
        await update.message.reply_text(
            text=f"Вопрос {context.user_data['current_question'] + 1}/{len(QUESTIONS)}:\n\n{question_data['question']}",
            reply_markup=reply_markup,
        )


# ответ
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Сохраняем ответ
    context.user_data["test_answers"].append(query.data)

    # Переходим к следующему вопросу или завершаем тест
    context.user_data["current_question"] += 1
    if context.user_data["current_question"] < len(QUESTIONS):
        await ask_question(update, context)
    else:
        await finish_test(update, context)


# результат
async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # определение результата по самому частому значению
    answers = context.user_data["test_answers"]
    result = max(set(answers), key=answers.count)

    instrument = INSTRUMENTS[result]

    await update.callback_query.edit_message_text(
        text=f"🎉 Тест завершен! 🎉\n\n"
        f"Твой инструмент: <b>{instrument['name']}</b>\n\n"
        f"{instrument['description']}\n\n"
        f"Хочешь научиться играть на {instrument['name']} или другом инструменте? "
        f"Заходи на <a href='#'>BrassBook</a> - платформу музыкального образования! 🎵",
        parse_mode="HTML",
    )


# обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text="Что-то пошло не так 😢 Попробуйте начать тест заново с помощью /test"
        )
    else:
        await update.message.reply_text(
            text="Что-то пошло не так 😢 Попробуйте начать тест заново с помощью /test"
        )


def main() -> None:
    # Application по токену
    application = Application.builder().token("7845233409:AAE1lR2YFnj4b5e8DZUKp7bHchvWHoXn_1U").build()

    # создание обработок
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", start_test))
    application.add_handler(CallbackQueryHandler(button))

    # обработка ошибок
    application.add_error_handler(error_handler)

    # запуск
    application.run_polling()


if __name__ == "__main__":
    main()