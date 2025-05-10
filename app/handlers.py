from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.types.web_app_info import WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database import get_teacher_schedule

import app.keyboards as kb


router = Router()


class Form(StatesGroup):
    waiting_teacher_name = State()
    waiting_subject = State() 
    

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        'Привет! 👋Я бот-помощник для студентов. '\
        'Помогу тебе разобраться, как закрыть долги по предметам: подскажу, что делать, куда идти и к кому обращаться. '\
        'Если что-то непонятно — просто задай вопрос, я на связи 💬', 
        reply_markup = kb.start)


@router.message(F.text == 'Задать вопрос')
async def debts_algorithm(message: Message):
    await message.answer(
        '✏️ Напиши свой вопрос — я постараюсь помочь его решить!',
        #Точка входа для вопросов ИИ
        reply_markup = kb.webAppPageFirst)


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
        '🗓 Чтобы найти расписание консультаций, введи фамилию преподавателя (она указана в Modeus).',
        #Точка входа для поиска данных о преподавателях
        #Предложение о напоминании 
        reply_markup = kb.traditionalTable)
    
@router.callback_query(F.data == 'traditionalExam')
async def traditional_Exam(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        'Если ты не сдал только экзамен, следи за расписанием пересдач на сайте ИРИТ-РТФ.')
    await callback.message.answer(
        '📝 Введи название предмета (можно посмотреть в Modeus): ', 
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
    if full_name in 'Продолжить ➡️':
        await message.answer(
            'Подтверди переход к следующему шагу ▶️',
            reply_markup = kb.nextPage
        )
        await state.clear()
    else:
        records = get_teacher_schedule(full_name)

        if records:
            response = [f"📅 Расписание для \n{full_name}:"]
            for day, time, room in records:
                response.append(f"\nДень: {day} \nВремя: {time} \nАудитория: {room}")
            await message.answer('\n'.join(response), reply_markup=kb.nextPage)
        else:
            await message.answer(
                "❌ Преподаватель не найден!",
                reply_markup = kb.nextPage
            )



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
        'Ты всегда можешь обратиться за помощью к тьютору.', 
        #Точка входа для вывода данных о тьюторах
        reply_markup = kb.exitPage)


@router.callback_query(F.data == 'startBack')
async def traditional_Exam(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(
        'Привет! 👋Я бот-помощник для студентов. '\
        'Помогу тебе разобраться, как закрыть долги по предметам: подскажу, что делать, куда идти и к кому обращаться. '\
        'Если что-то непонятно — просто задай вопрос, я на связи 💬', 
        reply_markup = kb.start)
    
@router.message(F.text == 'Вернуться к началу')
async def traditional_Exam(message: Message):
    await message.answer(
        'Привет! 👋Я бот-помощник для студентов. '\
        'Помогу тебе разобраться, как закрыть долги по предметам: подскажу, что делать, куда идти и к кому обращаться. '\
        'Если что-то непонятно — просто задай вопрос, я на связи 💬', 
        reply_markup = kb.start)