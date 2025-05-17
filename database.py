import sqlite3
from config import DATABASE_NAME

def create_tables():
    """Создание таблиц в базе данных"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS schedule(
        full_name TEXT NOT NULL,
        day_of_week TEXT NOT NULL,
        time_range TEXT NOT NULL,
        room TEXT NOT NULL,
        contact TEXT NOT NULL
    )''')
    
    conn.commit()
    conn.close()

def get_teacher_schedule(full_name: str):
    """Поиск расписания по ФИО"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT day_of_week, time_range, room, contact FROM schedule WHERE full_name = ?',
        (full_name,)
    )
    
    result = cursor.fetchall()
    conn.close()
    return result