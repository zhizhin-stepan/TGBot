from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo


start = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Задать вопрос')],
                                      [KeyboardButton(text='Алгоритм закрытия долгов')]],
                                      resize_keyboard = True,
                                      input_field_placeholder = 'Выберите опцию...')

debtsAlgorithm = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Как узнать форму реализации предмета?', callback_data='formInstruction')],
                                                [InlineKeyboardButton(text='Традиционная', callback_data='traditionalForm')],
                                                [InlineKeyboardButton(text='Онлайн', callback_data='onlineForm')],
                                                [InlineKeyboardButton(text='Смешенная', callback_data='mixedForm')]])


traditionalCheck = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='➡️ Верно', callback_data='traditionalCheckTrue')],
                                                         [InlineKeyboardButton(text='⬅️ Назад', callback_data='traditionalCheckBack')]])

traditionalDescriprion = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='НТК', callback_data='traditionalNTK')],
                                                               [InlineKeyboardButton(text='Добор баллов', callback_data='traditionalCurrent')],
                                                               [InlineKeyboardButton(text='Экзамен с преподавателем', callback_data='traditionalExam')]])

traditionalTable = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Узнать расписание', callback_data='traditionalSchedule')]],
                                      input_field_placeholder = 'Выберите опцию...')


mixedCheck = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='➡️ Верно', callback_data='mixedCheckTrue')],
                                                         [InlineKeyboardButton(text='⬅️ Назад', callback_data='mixedCheckBack')]])

mixedlDescription = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Практики', callback_data='mixedPractice')],
                                                         [InlineKeyboardButton(text='Лекции', callback_data='mixedLectures')]])


onlineCheck = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='➡️ Верно', callback_data='onlineCheckTrue')],
                                                         [InlineKeyboardButton(text='⬅️ Назад', callback_data='onlineCheckBack')]])

onlineDescriprion = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='➡️ Да', callback_data='onlineYes')],
                                                          [InlineKeyboardButton(text='⬅️ Нет', callback_data='onlineNo')]])


nextPage = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Продолжить ➡️')]],
                                      resize_keyboard = True,
                                      input_field_placeholder = 'Выберите опцию...')

exitPage = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Вернуться к началу', callback_data='startBack')]])


webAppPageFirst = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Открыть часто задаваемые вопросы", web_app=WebAppInfo(url='https://zhizhin-stepan.github.io/TEST-TGbot/'))],
                                                [KeyboardButton(text="Открыть таблицу преподавателей", web_app=WebAppInfo(url='https://zhizhin-stepan.github.io/SHIFT-TGBot/'))],
                                                [KeyboardButton(text='Вернуться к началу')]],
                                            resize_keyboard=True)