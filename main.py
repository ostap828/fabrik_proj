import tkinter as tk
from clothing_factory_gui import ОдежнаяФабрикаGUI
from supplier_gui import SupplierGUI
import psycopg2
from psycopg2 import Error

def создать_соединение_с_бд():
    try:
        conn = psycopg2.connect(
            database="clothing_factory",
            user="postgres",
            password="Ostap_628",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        return conn, cursor
    except Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None, None

def запустить_фабрику():
    root = tk.Tk()
    app = ОдежнаяФабрикаGUI(root)
    root.mainloop()

def запустить_поставщиков():
    conn, cursor = создать_соединение_с_бд()
    if conn and cursor:
        root = tk.Tk()
        app = SupplierGUI(root, conn, cursor)
        root.mainloop()
    else:
        print("Не удалось запустить интерфейс поставщиков")

if __name__ == "__main__":
    # Создаем главное окно выбора
    root = tk.Tk()
    root.title("Выбор интерфейса")
    root.geometry("300x150")

    # Создаем кнопки для выбора интерфейса
    ttk.Button(root, text="Интерфейс фабрики", command=lambda: [root.destroy(), запустить_фабрику()]).pack(pady=20)
    ttk.Button(root, text="Интерфейс поставщиков", command=lambda: [root.destroy(), запустить_поставщиков()]).pack(pady=20)

    root.mainloop()
