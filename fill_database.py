from database import create_tables
import sqlite3
from config import DATABASE_NAME

data = [
    ('Белоусов Иван Николаевич', 'понедельник', '10:15-11:45', 'Р-234'),
    ('Белоусова Вероника Игоревна', 'понедельник', '19:15-20:40', 'https://bbb.urfu.ru'),
    ('Белоусова Марина Михайловна', 'среда', '16:00-17:30', 'Р-203'),
    ('Бутаков Геннадий Петрович', 'четверг', '17:40-19:05', 'Р-048'),
    ('Веретенников Борис Михайлович', 'понедельник', '17:40-19:05', 'Р-048'),
    ('Кныш Алла Александровна', 'четверг', '17:40-19:05', 'Р-203'),
    ('Криковцева Татьяна Георгиевна', 'вторник', '16:00-17:30', 'Ф-414'),
    ('Крохин Александр Леонидович', 'четверг', '16:00-17:30', 'Р-239'),
    ('Ливадний Екатерина Дмитриевна', 'среда', '14:15-15:45', 'Р-104'),
    ('Малыгина Кристина Денисовна', 'пятница', '17:40-19:05', 'Р-243'),
    ('Маркина Анна Сергеевна', 'понедельник', '14:15-15:45', 'Р-211'),
    ('Мельников Юрий Борисович', 'четверг', '16:00-17:30', 'Р-403'),
    ('Миронов Денис Сергеевич', 'понедельник', '16:00-17:30', 'Р-243'),
    ('Поторочина Ксения Сергеевна', 'четверг', '14:15-15:45', 'Р-050'),
    ('Поторочина Ксения Сергеевна', 'пятница', '16:00-17:30', 'Р-048'),
    ('Чуксина Наталия Владимировна', 'вторник', '16:00-17:30', 'Р-403'),
    ('Шапарь Юлия Викторовна', 'вторник', '17:40-19:05', 'Р-203'),
    ('Шестакова Ирина Александровна', 'четверг', '17:40-19:05', 'Р146'),
    ('Янковская Анастасия Викторовна', 'вторник', '14:15-15:45', 'Т-903')
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
        cursor.execute("SELECT GROUP_CONCAT(full_name||day_of_week||time_range||room, '|') FROM schedule")
        db_hash = hash(cursor.fetchone()[0])
        data_hash = hash('|'.join([''.join(map(str, item)) for item in data]))
        
        return db_hash == data_hash
        
    except sqlite3.Error as e:
        print(f"Ошибка проверки БД: {e}")
        return False
    finally:
        conn.close()

def update_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        # Создаем таблицу если не существует
        create_tables()
        
        # Очищаем таблицу
        cursor.execute("DELETE FROM schedule")
        
        # Вставляем новые данные
        cursor.executemany(
            "INSERT INTO schedule (full_name, day_of_week, time_range, room) VALUES (?, ?, ?, ?)",
            data)
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Ошибка обновления БД: {e}")
        conn.close()
        return False


if __name__ == '__main__':
    if update_database():
        print("✅ База данных успешно заполнена!")