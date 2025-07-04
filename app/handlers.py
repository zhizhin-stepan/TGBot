from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.types.web_app_info import WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import tempfile, os

from database import get_teacher_schedule, get_teacher_consultations

import app.keyboards as kb
from app.client import get_chat_response_async, get_ocr_response_async, analyze_image_and_format
import sqlite3


router = Router()


class Form(StatesGroup):
    waiting_teacher_name = State()
    waiting_subject = State() 
    ai_chat_answers = State()
    agination_consult = State()
    pagination_schedule = State()
    

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        'Привет! 👋\n'
        'Я бот-помощник для студентов. \n'\
        'Помогу тебе разобраться, как закрыть долги по предметам: подскажу, что делать, куда идти и к кому обращаться. \n'\
        'Если что-то непонятно — просто задай вопрос, я на связи 💬',
        reply_markup = kb.start)


@router.message(F.text == 'Задать вопрос')
async def debts_algorithm(message: Message, state: FSMContext):
    await state.set_state(Form.ai_chat_answers)
    await message.answer(
        '✏️ Напиши свой вопрос о подготовке — я постараюсь помочь его решить!\n'
        '\nЕще лучше, если ты отправишь скриншот предмета из БРС, '\
        'тогда я сразу сообщу тебе причину долга и что с этим делать!',
        #Точка входа для вопросов ИИ
        reply_markup = kb.webAppPageFirst)
    

full_name_prompts = {}

def load_full_name_prompts(db_path="schedule.db"):
    global full_name_prompts
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, questions FROM schedule WHERE questions IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    # Создаем словарь, где ключ — фио в нижнем регистре
    full_name_prompts = {
        full_name.lower(): questions.strip() for full_name, questions in rows
    }

    
@router.message(Form.ai_chat_answers, F.text)
async def handle_text_message(message: Message, state: FSMContext):
    if not full_name_prompts:
        load_full_name_prompts()
    messageCheck = message.text.strip()
    if messageCheck in 'Вернуться к началу':
        await message.answer(
            'Подтверди возвращение к началу ▶️',
            reply_markup = kb.webAppPageFirst
        )
        await state.clear()
    else:
        status = await message.answer("🤖 Думаю над ответом...")

        try:
            user_text = message.text.lower()
            matched_prompt = None
            matched_name = None

            for full_name in full_name_prompts:
                if full_name in user_text:
                    print(full_name)
                    matched_prompt = full_name_prompts[full_name]
                    print(matched_prompt)
                    matched_name = full_name
                    break

            if matched_prompt:
                # Удалим ФИО из текста и сформируем промт
                user_query = user_text.replace(matched_name, "", 1).strip()
                full_prompt = f"{matched_prompt}\n\nВопрос на который нужен ответ: {user_query}"
            else:
                full_prompt = message.text

            response = await get_chat_response_async(full_prompt)

        except Exception as e:
            response = f"❌ Ошибка: {e}"

        await status.edit_text(response)
        await message.answer(
            "Можешь спросить что-то еще",
            reply_markup=kb.webAppPageFirst
        )

@router.message(Form.ai_chat_answers, F.photo)
async def handle_photo_message(message: Message, state: FSMContext):
    status = await message.answer("🖼 Распознаю баллы...")

    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_path = file.file_path

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        await message.bot.download_file(file_path, destination=tmp_file)
        temp_path = tmp_file.name

    try:
        result = await analyze_image_and_format(temp_path)  # здесь уже вернётся форматированный текст!
        # result — это уже готовый текст, красиво для Telegram!
        result_text = result
    except Exception as e:
        result_text = f"❌ Ошибка при распознавании: {e}"
    finally:
        os.remove(temp_path)

    await status.edit_text(result_text, parse_mode="HTML")

        



@router.message(F.text == 'Алгоритм закрытия долгов')
async def debts_algorithm(message: Message):
    await message.answer(
        'Чтобы я мог тебе помочь, пожалуйста, укажи форму реализации предмета — как именно ты его проходил.', 
        reply_markup = kb.debtsAlgorithm)

@router.callback_query(F.data == 'formInstruction')
async def form_instruction(callback: CallbackQuery):
    await callback.message.answer(
        'Посмотри в Modeus — там указано, были ли у тебя: \n'
        '   • лекции и практики с преподавателем, \n'
        '   • лекции в формате онлайн-курса и практики с преподавателем, \n'
        '   • полностью онлайн-курс.')
    #Точка входа для парсинга данных из скриншота 
    await callback.answer('')
    await callback.message.answer(
        'Чтобы я мог тебе помочь, пожалуйста, укажи форму реализации предмета — как именно ты его проходил.', 
        reply_markup = kb.debtsAlgorithm)



@router.callback_query(F.data == 'traditionalForm')
async def traditional_form(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        '👨‍🏫 У тебя в Modeus указаны лекции и практики с преподавателем. Всё верно?', 
        reply_markup = kb.traditionalCheck)

@router.callback_query(F.data == 'traditionalCheckBack')
async def trditional_back(callback: CallbackQuery):
    await callback.message.answer('Возвращаемся назад')
    await callback.answer('')
    await callback.message.answer(
        'Чтобы я мог тебе помочь, пожалуйста, укажи форму реализации предмета — как именно ты его проходил.', 
        reply_markup = kb.debtsAlgorithm)

@router.callback_query(F.data == 'traditionalCheckTrue')
async def traditional_check(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        'Ты получил:\n'
        '   • За НТК менее 40 баллов ИЛИ \n'
        '   • Не хватает баллов за лекции/практики/лабораторные ИЛИ \n'
        '   • Не сдан экзамен с преподавателем', 
        reply_markup = kb.traditionalDescriprion)

@router.callback_query(F.data == 'traditionalNTK')
async def traditional_NTK(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        '🔁 Нужно пересдать НТК. 📌 Чтобы записаться на пересдачу: \n'
        '   1. Перейди на сайт exam1. \n'
        '   2. Найди пункт «Запись на пересдачу». \n'
        '   3. Обязательно прочитай инструкцию перед записью — это важно!',
        reply_markup = kb.nextPage)
    
@router.callback_query(F.data == 'traditionalCurrent')
async def traditional_Current(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        '💬 Обратись к своему преподавателю — он подскажет, как можно добрать баллы. Это можно сделать в дни консультаций.')
    await callback.message.answer(
        '🗓 Чтобы найти расписание консультаций, введи фамилию преподавателя (она указана в Modeus): ',
        #Точка входа для поиска данных о преподавателях
        #Предложение о напоминании 
        reply_markup = kb.traditionalTable)
    
@router.callback_query(F.data == 'traditionalExam')
async def traditional_Exam(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        'Если ты не сдал только экзамен, следи за расписанием пересдач на сайте ИРИТ-РТФ. \n'
        'Либо можешь узнать об этом у своего преподавателя лично')
    await callback.message.answer(
        '📝 Чтобы найти расписание консультаций, введи фамилию преподавателя (она указана в Modeus): ', 
        #Точка входа для поиска данных о датах пересдач
        #Предложение о напоминании
        reply_markup = kb.traditionalTable)
    

@router.callback_query(F.data == 'traditionalSchedule')
async def traditional_schedule(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_teacher_name)
    await callback.message.answer("🔍 Введите ФИО преподавателя:")
    
@router.message(Form.waiting_teacher_name, F.text)
async def handle_teacher_name(message: Message, state: FSMContext):
    full_name = message.text.strip()
    if full_name == 'Продолжить ➡️':
        await message.answer('Подтверди переход к следующему шагу ▶️', reply_markup=kb.nextPage)
        await state.clear()
    else:
        await state.update_data(teacher_name=full_name)
        
        records = get_teacher_consultations(full_name)
        lessons = get_teacher_schedule(full_name)

        if records or lessons:
            response = [
            f"📅 Консультации для {full_name}:",
            "————————————————"]

            for record in records:
                day, time, room, contact = record
                contact_info = f"\n✉️ Контакты: {contact}" if contact != "--" else ""
                
                response.append(
                    f"🗓 День: {day}\n"
                    f"⏰ Время: {time}\n"
                    f"🚪 Аудитория: {room}"
                    f"{contact_info}\n"
                    "————————————————"
                )
            answer = [
            f"📅 Расписание занятий для {full_name}:",
            "————————————————"]
            await message.answer('\n'.join(response), reply_markup=kb.nextPage)

            await state.update_data(
            schedule=lessons,
            schedule_page=0)

            await send_schedule_page(message, lessons, 0, state)
        else:
            await message.answer(
                "❌ Преподаватель не найден! Попробуй ввести его имя еще раз",
                reply_markup = kb.nextPage
            )

async def send_schedule_page(message: Message, data: list, page: int, state: FSMContext):
    if not data:
        await message.answer("❌ Расписание занятий не найдено")
        return
    
    items_per_page = 6
    total_pages = (len(data) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min((page + 1) * items_per_page, len(data))
    
    response = [f"📅 Расписание занятий (стр. {page+1}/{total_pages}):", "————————————————"]
    for record in data[start_idx:end_idx]:
        day, time, room, contact = record
        contact_info = f"\n✉️ Контакты: {contact}" if contact != "--" else ""
        response.append(
            f"🗓 День: {day}\n"
            f"⏰ Время: {time}\n"
            f"🚪 Аудитория: {room}"
            f"{contact_info}\n"
            "————————————————"
        )
    
    # Создаем клавиатуру пагинации
    pagination_kb = InlineKeyboardMarkup(inline_keyboard=[])
    if total_pages > 1:
        row = []
        if page > 0:
            row.append(InlineKeyboardButton(
                text="⬅️", 
                callback_data=f"sched_prev:{page}"
            ))
        row.append(InlineKeyboardButton(
            text=f"{page+1}/{total_pages}", 
            callback_data="current_page"
        ))
        if page < total_pages - 1:
            row.append(InlineKeyboardButton(
                text="➡️", 
                callback_data=f"sched_next:{page}"
            ))
        pagination_kb.inline_keyboard.append(row)
    
    # Сохраняем текущую страницу
    await state.update_data(schedule_page=page)
    
    await message.answer('\n'.join(response), reply_markup=pagination_kb)


@router.callback_query(F.data.startswith("sched_"))
async def handle_schedule_pagination(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("schedule_page", 0)
    schedule = data.get("schedule", [])
    
    action, page = callback.data.split(":")
    page = int(page)
    
    if "prev" in action and page > 0:
        new_page = page - 1
    elif "next" in action and page < (len(schedule) // 6):
        new_page = page + 1
    else:
        await callback.answer()
        return
    
    await callback.message.delete()
    await send_schedule_page(callback.message, schedule, new_page, state)
    await callback.answer()

@router.callback_query(F.data == "current_page")
async def handle_current_page(callback: CallbackQuery):
    await callback.answer()



@router.callback_query(F.data == 'mixedForm')
async def mixed_form(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        '🧑‍🏫 В Modeus указаны лекции в виде онлайн-курса, а практики — с преподавателем. Всё верно?', 
        reply_markup = kb.mixedCheck)

@router.callback_query(F.data == 'mixedCheckBack')
async def mixed_back(callback: CallbackQuery):
    await callback.message.answer('Возвращаемся назад')
    await callback.answer('')
    await callback.message.answer(
        'Чтобы я мог тебе помочь, пожалуйста, укажи форму реализации предмета — как именно ты его проходил.', 
        reply_markup = kb.debtsAlgorithm)

@router.callback_query(F.data == 'mixedCheckTrue')
async def mixed_check(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        'Что именно нужно закрыть? \n'
        'Практики или лекции(онлайн-курс)?', 
        reply_markup = kb.mixedlDescription)
    
@router.callback_query(F.data == 'mixedPractice')
async def traditional_check(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        'Ты получил:\n'
        '   • За НТК менее 40 баллов ИЛИ \n'
        '   • Не хватает баллов за лекции/практики/лабораторные ИЛИ \n'
        '   • Не сдан экзамен с преподавателем', 
        reply_markup = kb.traditionalDescriprion)
    
@router.callback_query(F.data == 'mixedLectures')
async def online_check(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        'У Вас набраны минимальные промежуточные ' \
        'баллы за курс?', reply_markup = kb.onlineDescriprion)



@router.callback_query(F.data == 'onlineForm')
async def online_form(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('📘 У тебя был только онлайн-курс. Всё верно?', reply_markup = kb.onlineCheck)

@router.callback_query(F.data == 'onlineCheckBack')
async def online_back(callback: CallbackQuery):
    await callback.message.answer('Возвращаемся назад')
    await callback.answer('')
    await callback.message.answer(
        'Чтобы я мог тебе помочь, пожалуйста, укажи форму реализации предмета — как именно ты его проходил.', 
        reply_markup = kb.debtsAlgorithm)

@router.callback_query(F.data == 'onlineCheckTrue')
async def online_check(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Ты набрал минимальные промежуточные баллы?', reply_markup = kb.onlineDescriprion)
    
@router.callback_query(F.data == 'onlineYes')
async def online_yes(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        'Необходимо подать заявку на открытие доступа для прохождения итогового контроля. \n'  
        '\nСсылка на заявку: https://forms.yandex.ru/u/6319b2afbbb4936cf5e3236d/ \n'
        '\nПроверка заявки занимает несколько рабочих дней. ' \
        'Ответ с дальнейшими инструкциями придёт на вашу корпоративную электронную почту, указанную в заявке.', 
        reply_markup = kb.nextPage)
    
@router.callback_query(F.data == 'onlineNo')
async def online_no(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        'Для того, чтобы получить доступ к заданиям курса вам необходимо: \n'
        '\n📌Проверить, правильно ли указана почта в вашем профиле. '
        'Обратите внимание, что студенты УрФУ могут обучаться исключительно под почтой в домене @urfu.me. \n'
        '\n📌Написать письмо в техническую поддержку по адресу «openedu@urfu.ru» с просьбой добавить вас в группу «УрФУ_Задолженность». '
        'В письме укажите: ФИО, академическую группу, адрес корпоративной почты и ссылку на курс. \n'
        '\n❗️Важно: Запись в группу должников закрывается за НЕДЕЛЮ до наступления крайнего срока сдачи контрольно-оценочных заданий. '
        'Срок закрытия заданий указан на странице «График открытия материалов».',
        reply_markup = kb.nextPage)



@router.message(F.text == 'Продолжить ➡️')
async def exit_page(message: Message):
    await message.answer(
        '💡 Если что-то осталось непонятным — ничего страшного! \n'
        'Вернись в раздел с вопросами, там ты сможешь найти ответ по интересующему вопросу, '
        'узнать наличие у себя долгов и что с этим можно сделать.\n'
        '\n Либо ты можешь обратиться за помощью к тьютору, если не нашел ответа на свой вопрос.'
        '————————————————\n'
        '🔍Список тьюторов:\n'
        '1. Ирина Колмогорцева, Программная инженерия - 45-50 группы, ИВТ - РИ-130914, контакт - https://vk.com/id636684151\n'
        '2. Артем Хрушков, Прикладная информатика, контакт - https://vk.com/id41032121\n'
        '3. Алена Садова, Программная инженерия - 40-44 группы, контакт - https://vk.com/sadova_a_a\n'
        '4. Эльмира Валиева, Направления - 11, 27, 29, контакт - https://vk.com/elmiraw\n'
        '5. Георгий Базаров, ИВТ, Алгоритмы искусственного интелекта, контакт - https://vk.com/georgybazarov\n'
        '————————————————', 
        #Точка входа для вывода данных о тьюторах
        disable_web_page_preview=True,
        reply_markup = kb.exitPage)


@router.callback_query(F.data == 'startBack')
async def traditional_Exam(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        'Привет! 👋\n'
        'Я бот-помощник для студентов. \n'\
        'Помогу тебе разобраться, как закрыть долги по предметам: подскажу, что делать, куда идти и к кому обращаться. \n'\
        'Если что-то непонятно — просто задай вопрос, я на связи 💬', 
        reply_markup = kb.start)
    
@router.message(F.text == 'Вернуться к началу')
async def traditional_Exam(message: Message):
    await message.answer(
        'Привет! 👋\n'
        'Я бот-помощник для студентов. \n'\
        'Помогу тебе разобраться, как закрыть долги по предметам: подскажу, что делать, куда идти и к кому обращаться. \n'\
        'Если что-то непонятно — просто задай вопрос, я на связи 💬', 
        reply_markup = kb.start)