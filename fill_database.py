from database import create_tables
import sqlite3
from config import DATABASE_NAME

data = [
    ('Белоусов Иван Николаевич', 'понедельник', '10:15-11:45', 'Р-234', 'i.n.belousov@urfu.ru'),
    ('Белоусова Вероника Игоревна', 'понедельник', '19:15-20:40', 'https://bbb.urfu.ru', 'v.i.belousova@urfu.ru'),
    ('Белоусова Марина Михайловна', 'среда', '16:00-17:30', 'Р-203', 'm.m.mikhaleva@urfu.ru'),
    ('Бутаков Геннадий Петрович', 'четверг', '17:40-19:05', 'Р-048', 'g.p.butakov@urfu.ru'),
    ('Веретенников Борис Михайлович', 'понедельник', '17:40-19:05', 'Р-048', 'b.m.veretennikov@urfu.ru'),
    ('Кныш Алла Александровна', 'четверг', '17:40-19:05', 'Р-203', 'a.a.knysh@urfu.ru'),
    ('Криковцева Татьяна Георгиевна', 'вторник', '16:00-17:30', 'Ф-414', 't.g.krikovtceva@urfu.ru'),
    ('Крохин Александр Леонидович', 'четверг', '16:00-17:30', 'Р-239', 'a.l.krokhin@urfu.ru'),
    ('Ливадний Екатерина Дмитриевна', 'среда', '14:15-15:45', 'Р-104', 'edanashkina@urfu.ru'),
    ('Малыгина Кристина Денисовна', 'пятница', '17:40-19:05', 'Р-243', '---'),
    ('Маркина Анна Сергеевна', 'понедельник', '14:15-15:45', 'Р-211', 'a.s.kirianova@urfu.ru'),
    ('Мельников Юрий Борисович', 'четверг', '16:00-17:30', 'Р-403', 'j.b.melnikov@urfu.ru'),
    ('Миронов Денис Сергеевич', 'понедельник', '16:00-17:30', 'Р-243', 'd.s.mironov@urfu.ru'),
    ('Поторочина Ксения Сергеевна', 'четверг', '14:15-15:45', 'Р-050', 'k.s.potorochina@urfu.ru'),
    ('Поторочина Ксения Сергеевна', 'пятница', '16:00-17:30', 'Р-048', 'k.s.potorochina@urfu.ru'),
    ('Чуксина Наталия Владимировна', 'вторник', '16:00-17:30', 'Р-403', 'n.v.chuksina@urfu.ru'),
    ('Шапарь Юлия Викторовна', 'вторник', '17:40-19:05', 'Р-203', 'j.v.shapar@urfu.ru'),
    ('Шестакова Ирина Александровна', 'четверг', '17:40-19:05', 'Р146', 'i.a.shestakova@urfu.ru'),
    ('Янковская Анастасия Викторовна', 'вторник', '14:15-15:45', 'Т-903', 'av.diachkova@urfu.ru')
]


def check_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        # Проверяем существование таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schedule'")
        if not cursor.fetchone():
            return False
        
        # Проверяем количество записей
        cursor.execute("SELECT COUNT(*) FROM schedule")
        db_count = cursor.fetchone()[0]
        
        # Проверяем соответствие количества записей
        if db_count != len(data):
            return False
            
        # Проверяем хэш данных
        cursor.execute("SELECT GROUP_CONCAT(full_name||day_of_week||time_range||room||contact, '|') FROM schedule")
        db_hash = hash(cursor.fetchone()[0])
        data_hash = hash('|'.join([''.join(map(str, item)) for item in data]))
        
        return db_hash == data_hash
        
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
        # Удаляем старую таблицу
        cursor.execute("DROP TABLE IF EXISTS schedule")
        
        # Создаем новую таблицу с актуальной структурой
        create_tables()
        
        # Вставляем новые данные
        cursor.executemany(
            '''INSERT INTO schedule 
            (full_name, day_of_week, time_range, room, contact) 
            VALUES (?, ?, ?, ?, ?)''',
            data
        )
        conn.commit()
        print(f"Обновлено записей: {len(data)}")
        return True
        
    except sqlite3.Error as e:
        print(f"Ошибка обновления БД: {e}")
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    if update_database():
        print("✅ База данных успешно заполнена!")