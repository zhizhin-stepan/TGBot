from database import create_tables
import sqlite3
from config import DATABASE_NAME

data = [
    ('Агафонов Александр Петрович', 'вторник', '17:40-19:10', 'Сп-501', '---'),
    ('Белоусов Иван Николаевич', 'понедельник', '10:15-11:45', 'Р-234', 'i.n.belousov@urfu.ru'),
    ('Белоусова Вероника Игоревна', 'понедельник', '19:15-20:45', 'https://bbb.urfu.ru', 'v.i.belousova@urfu.ru'),
    ('Белоусова Марина Михайловна', 'среда', '16:00-17:30', 'Р-203', 'm.m.mikhaleva@urfu.ru'),
    ('Ботов Михаил Алексеевич', 'понедельник', '12:00-13:30', 'Т-503', 'M.A.Botov@urfu.ru'),
    ('Бутаков Геннадий Петрович', 'четверг', '17:40-19:10', 'Р-048', 'g.p.butakov@urfu.ru'),
    ('Веретенников Борис Михайлович', 'понедельник', '17:40-19:10', 'Р-048', 'b.m.veretennikov@urfu.ru'),
    ('Власова Алиса Михайловна', 'вторник', '8:30-10:00', 'С-305', 'A.M.Vlasova@urfu.ru'),
    ('Герасимов Максим Федорович', 'среда', '16:00-17:30', 'Сп-501', 'maksim.gerasimov@urfu.ru'),
    ('Кащенко Надежда Михайловна', 'среда', '16:00-17:30', 'Т-503', 'nadezhda.kashchenko@urfu.ru'),
    ('Кизилова Елена Вадимовна', 'пятница', '16:00-17:30', 'Мт-213', 'E.V.Kizilova@urfu.ru'),
    ('Кныш Алла Александровна', 'четверг', '17:40-19:10', 'Р-203', 'a.a.knysh@urfu.ru'),
    ('Криковцева Татьяна Георгиевна', 'вторник', '16:00-17:30', 'Ф-414', 't.g.krikovtceva@urfu.ru'),
    ('Крохин Александр Леонидович', 'четверг', '16:00-17:30', 'Р-239', 'a.l.krokhin@urfu.ru'),
    ('Ливадний Екатерина Дмитриевна', 'среда', '14:15-15:45', 'Р-104', '---'),
    ('Лобашева Нина Анатольевна', 'вторник', '17:40-19:05', 'Р-102', 'n.a.lobasheva@urfu.ru'),
    ('Магомедова Рада Сергеевна', 'суббота', '16:00-17:30', 'Т-508', 'r.s.magomedova@urfu.ru'),
    ('Малыгина Кристина Денисовна', 'пятница', '17:40-19:10', 'Р-243', '---'),
    ('Маркина Анна Сергеевна', 'понедельник', '14:15-15:45', 'Р-211', 'a.s.kirianova@urfu.ru'),
    ('Мельников Юрий Борисович', 'четверг', '16:00-17:30', 'Р-403', 'j.b.melnikov@urfu.ru'),
    ('Миронов Денис Сергеевич', 'понедельник', '16:00-17:30', 'Р-243', 'd.s.mironov@urfu.ru'),
    ('Поторочина Ксения Сергеевна', 'четверг', '14:15-15:45', 'Р-050', 'k.s.potorochina@urfu.ru'),
    ('Поторочина Ксения Сергеевна', 'пятница', '16:00-17:30', 'Р-048', 'k.s.potorochina@urfu.ru'),
    ('Расин Олег Вениаминович', 'среда', '19:15-20:45', 'Т-503', 'O.V.Rasin@urfu.ru'),
    ('Рыбалко Александр Федорович', 'среда', '14:15-15:45', 'Т-503', 'A.F.Rybalko@urfu.ru'),
    ('Чащина Вера Геннадиевна', 'понедельник', '8:30-10:00', 'Т-503', 'VG.Chashchina@urfu.ru'),
    ('Чуксина Наталия Владимировна', 'вторник', '16:00-17:30', 'Р-403', 'n.v.chuksina@urfu.ru'),
    ('Шапарь Юлия Викторовна', 'вторник', '17:40-19:10', 'Р-203', 'j.v.shapar@urfu.ru'),
    ('Шестакова Ирина Александровна', 'четверг', '17:40-19:10', 'Р146', 'i.a.shestakova@urfu.ru'),
    ('Янковская Анастасия Викторовна', 'вторник', '14:15-15:45', 'Т-903', 'av.diachkova@urfu.ru')
]

data_additional = [
    ('Агафонов Александр Петрович', 'вторник', '14:15-15:45', 'СП-501', '---'),
    ('Агафонов Александр Петрович', 'вторник', '16:00-17:30', 'СП-501', '---'),
    ('Агафонов Александр Петрович', 'четверг', '14:15-15:45', 'СП-501', '---'),
    ('Агафонов Александр Петрович', 'четверг', '16:00-17:30', 'СП-501', '---'),
    ('Агафонов Александр Петрович', 'четверг', '17:40-19:05', 'СП-501', '---'),
    ('Белоусов Иван Николаевич', 'понедельник', '12:00-13:30', 'Р-325', 'i.n.belousov@urfu.ru'),
    ('Белоусов Иван Николаевич', 'понедельник', '14:15-15:45', 'Р-243', 'i.n.belousov@urfu.ru'),
    ('Белоусов Иван Николаевич', 'среда', '12:00-13:30', 'Р-215', 'i.n.belousov@urfu.ru'),
    ('Белоусов Иван Николаевич', 'среда', '14:15-15:45', 'Р-239', 'i.n.belousov@urfu.ru')
]

def check_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        tables = ['schedule', 'schedule_additional']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                return False
        
        # Проверяем количество записей
        cursor.execute("SELECT COUNT(*) FROM schedule")
        db_count_main = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM schedule_additional")
        db_count_additional = cursor.fetchone()[0]
        
        if db_count_main != len(data) or db_count_additional != len(data_additional):
            return False
            
        # Проверяем хэши данных
        def get_table_hash(table_name, source_data):
            cursor.execute(f"SELECT GROUP_CONCAT(full_name||day_of_week||time_range||room||contact, '|') FROM {table_name}")
            db_hash = hash(cursor.fetchone()[0])
            data_hash = hash('|'.join([''.join(map(str, item)) for item in source_data]))
            return db_hash == data_hash
        
        return get_table_hash('schedule', data) and get_table_hash('schedule_additional', data_additional)
        
    except sqlite3.Error as e:
        print(f"Ошибка проверки БД: {e}")
        return False
    finally:
        conn.close()

def update_database():
    """Полная перезапись данных в БД"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DROP TABLE IF EXISTS schedule")
        cursor.execute("DROP TABLE IF EXISTS schedule_additional")
        
        create_tables()
        
        # Вставляем данные
        cursor.executemany(
            '''INSERT INTO schedule 
            (full_name, day_of_week, time_range, room, contact) 
            VALUES (?, ?, ?, ?, ?)''',
            data
        )
        
        cursor.executemany(
            '''INSERT INTO schedule_additional 
            (full_name, day_of_week, time_range, room, contact) 
            VALUES (?, ?, ?, ?, ?)''',
            data_additional
        )
        
        conn.commit()
        print(f"Обновлено записей: {len(data) + len(data_additional)}")
        return True
        
    except sqlite3.Error as e:
        print(f"Ошибка обновления БД: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    if update_database():
        print("✅ База данных успешно заполнена!")