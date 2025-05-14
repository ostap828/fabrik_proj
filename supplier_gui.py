import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from psycopg2 import Error


class SupplierGUI:
    def __init__(self, parent_frame, db_connection, db_cursor):
        self.frame = parent_frame
        self.conn = db_connection
        self.cursor = db_cursor

        self.создать_интерфейс()

    def создать_интерфейс(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Правая часть - список поставщиков и их заказов
        frame_правая = ttk.Frame(main_frame)
        frame_правая.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        # Список поставщиков
        frame_список = ttk.LabelFrame(frame_правая, text="Список поставщиков", padding=10)
        frame_список.pack(fill='x', padx=5, pady=5)

        self.список_поставщиков = ttk.Treeview(frame_список, columns=("Компания", "Контакт", "Телефон", "Email", "Адрес"), show="headings", height=5)
        self.список_поставщиков.pack(expand=True, fill='both')

        for col in ("Компания", "Контакт", "Телефон", "Email", "Адрес"):
            self.список_поставщиков.heading(col, text=col)
            self.список_поставщиков.column(col, width=100)

        # Список заказов
        frame_заказы = ttk.LabelFrame(frame_правая, text="Заказы поставщика", padding=10)
        frame_заказы.pack(fill='both', expand=True, padx=5, pady=5)

        self.список_заказов_поставщика = ttk.Treeview(frame_заказы, columns=(
            "ID", "Категория", "Тип", "Цвет", "Количество", "Цена", "Дата заказа", "Статус"
        ), show="headings")
        self.список_заказов_поставщика.pack(expand=True, fill='both')

        for col in ("ID", "Категория", "Тип", "Цвет", "Количество", "Цена", "Дата заказа", "Статус"):
            self.список_заказов_поставщика.heading(col, text=col)
            self.список_заказов_поставщика.column(col, width=100)

        # Кнопки управления заказами
        frame_кнопки = ttk.Frame(frame_заказы)
        frame_кнопки.pack(fill='x', pady=5)
        ttk.Button(frame_кнопки, text="Обновить статус", command=self.обновить_статус_заказа_поставщика).pack(side='left', padx=5)

        # Привязываем событие выбора поставщика
        self.список_поставщиков.bind('<<TreeviewSelect>>', self.показать_заказы_поставщика)

        # Обновляем список поставщиков
        self.обновить_список_поставщиков()

    def обновить_список_заказов_поставщика(self):
        # Очищаем список заказов
        for item in self.список_заказов_поставщика.get_children():
            self.список_заказов_поставщика.delete(item)

        # Получаем выбранного поставщика
        selected_item = self.список_поставщиков.selection()
        if not selected_item:
            return

        # Получаем ID поставщика из тегов элемента
        supplier_id = int(self.список_поставщиков.item(selected_item[0])['tags'][0])

        # Получаем заказы поставщика из базы данных
        self.cursor.execute("""
            SELECT id, category, type, color, quantity, price, created_at, status
            FROM fittings_orders
            WHERE supplier_id = %s
            ORDER BY created_at DESC
        """, (supplier_id,))

        for заказ in self.cursor.fetchall():
            self.список_заказов_поставщика.insert("", "end", values=(
                заказ[0],  # ID
                заказ[1],  # Категория
                заказ[2],  # Тип
                заказ[3] if заказ[3] else "Не указан",  # Цвет
                заказ[4] if заказ[4] else "Не указано",  # Количество
                f"{заказ[5]} руб." if заказ[5] else "Не указана",  # Цена
                заказ[6].strftime("%Y-%m-%d %H:%M"),  # Дата заказа
                заказ[7]  # Статус
            ))

    def показать_заказы_поставщика(self, event):
        self.обновить_список_заказов_поставщика()

    def обновить_список_поставщиков(self):
        # Очищаем список
        for item in self.список_поставщиков.get_children():
            self.список_поставщиков.delete(item)

        # Получаем поставщиков из базы данных
        self.cursor.execute("""
            SELECT id, company_name, contact_person, phone, email, address
            FROM suppliers
            ORDER BY company_name
        """)

        for поставщик in self.cursor.fetchall():
            self.список_поставщиков.insert("", "end", values=(
                поставщик[1],  # Компания
                поставщик[2],  # Контакт
                поставщик[3],  # Телефон
                поставщик[4],  # Email
                поставщик[5]   # Адрес
            ), tags=(str(поставщик[0]),))  # ID поставщика в тегах

    def обновить_статус_заказа_поставщика(self):
        # Получаем выбранный заказ
        selected_item = self.список_заказов_поставщика.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите заказ")
            return

        # Получаем ID заказа
        order_id = self.список_заказов_поставщика.item(selected_item[0])['values'][0]

        # Создаем окно обновления статуса
        окно_статуса = tk.Toplevel(self.frame)
        окно_статуса.title("Обновить статус заказа")
        окно_статуса.geometry("300x150")

        # Выпадающий список статусов
        ttk.Label(окно_статуса, text="Новый статус:").pack(pady=10)
        статус = ttk.Combobox(окно_статуса, values=[
            "В обработке",
            "В пути",
            "Доставлено",
            "Отменено"
        ], width=30)
        статус.pack(pady=10)

        def подтвердить_статус():
            новый_статус = статус.get()
            if not новый_статус:
                messagebox.showwarning("Предупреждение", "Выберите статус")
                return

            try:
                # Обновляем статус заказа в базе данных
                self.cursor.execute("""
                    UPDATE fittings_orders
                    SET status = %s
                    WHERE id = %s
                """, (новый_статус, order_id))

                # Обновляем статус в received_fittings
                self.cursor.execute("""
                    UPDATE received_fittings
                    SET status = %s
                    WHERE order_id = %s
                """, (новый_статус, order_id))

                # Если статус "Доставлено", обновляем дату получения
                if новый_статус == "Доставлено":
                    self.cursor.execute("""
                        UPDATE received_fittings
                        SET received_at = CURRENT_TIMESTAMP
                        WHERE order_id = %s
                    """, (order_id,))

                self.conn.commit()

                # Обновляем списки
                self.показать_заказы_поставщика(None)  # Обновляем список заказов поставщика

                messagebox.showinfo("Успех", "Статус заказа обновлен")
                окно_статуса.destroy()
            except Error as e:
                self.conn.rollback()
                messagebox.showerror("Ошибка", f"Не удалось обновить статус: {e}")

        # Кнопки
        frame_кнопки = ttk.Frame(окно_статуса)
        frame_кнопки.pack(pady=10)
        ttk.Button(frame_кнопки, text="Подтвердить", command=подтвердить_статус).pack(side='left', padx=5)
        ttk.Button(frame_кнопки, text="Отмена", command=окно_статуса.destroy).pack(side='left', padx=5)

    def сделать_заказ(self):
        # Получаем выбранного поставщика
        selected_item = self.список_поставщиков.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите поставщика")
            return

        # Получаем ID поставщика из тегов элемента
        supplier_id = int(self.список_поставщиков.item(selected_item[0])['tags'][0])
        поставщик = self.список_поставщиков.item(selected_item[0])['values']

        # Создаем окно заказа
        окно_заказа = tk.Toplevel(self.frame)
        окно_заказа.title("Заказ фурнитуры")
        окно_заказа.geometry("500x400")

        # Отображаем информацию о поставщике
        ttk.Label(окно_заказа, text=f"Поставщик: {поставщик[0]}", font=('Arial', 10, 'bold')).pack(pady=5)
        ttk.Label(окно_заказа, text=f"Контакт: {поставщик[1]}").pack(pady=2)
        ttk.Label(окно_заказа, text=f"Телефон: {поставщик[2]}").pack(pady=2)

        # Форма заказа
        frame_заказ = ttk.LabelFrame(окно_заказа, text="Детали заказа", padding=10)
        frame_заказ.pack(fill='both', expand=True, padx=10, pady=10)

        # Категория товара
        ttk.Label(frame_заказ, text="Категория:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        категория = ttk.Combobox(frame_заказ, values=["Фурнитура", "Трикотажные полотна"], width=30)
        категория.grid(row=0, column=1, padx=5, pady=5)

        # Тип фурнитуры (будет меняться в зависимости от категории)
        ttk.Label(frame_заказ, text="Тип:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        тип = ttk.Combobox(frame_заказ, width=30)
        тип.grid(row=1, column=1, padx=5, pady=5)

        # Функция обновления списка типов в зависимости от категории
        def обновить_типы(event):
            if категория.get() == "Фурнитура":
                тип['values'] = [
                    "Пуговицы",
                    "Молнии",
                    "Кнопки",
                    "Крючки",
                    "Петли",
                    "Пряжки",
                    "Застежки",
                    "Липучки",
                    "Шнурки",
                    "Декоративные элементы"
                ]
            elif категория.get() == "Трикотажные полотна":
                тип['values'] = [
                    "Кулир",
                    "Футер",
                    "Начес",
                    "Вискоза",
                    "Рибана",
                    "Эластан",
                    "Модал",
                    "Интерлок",
                    "Капитоний",
                    "Бифлекс"
                ]
            тип.set('')  # Очищаем выбранное значение

        # Привязываем обновление типов к изменению категории
        категория.bind('<<ComboboxSelected>>', обновить_типы)

        # Цвет
        ttk.Label(frame_заказ, text="Цвет:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        цвет = ttk.Entry(frame_заказ, width=30)
        цвет.grid(row=2, column=1, padx=5, pady=5)

        # Количество
        ttk.Label(frame_заказ, text="Количество:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        количество = ttk.Entry(frame_заказ, width=30)
        количество.grid(row=3, column=1, padx=5, pady=5)

        # Цена за единицу
        ttk.Label(frame_заказ, text="Цена за единицу:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        цена = ttk.Entry(frame_заказ, width=30)
        цена.grid(row=4, column=1, padx=5, pady=5)

        # Дата доставки
        ttk.Label(frame_заказ, text="Дата доставки:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        дата = ttk.Entry(frame_заказ, width=30)
        дата.grid(row=5, column=1, padx=5, pady=5)

        # Комментарий
        ttk.Label(frame_заказ, text="Комментарий:").grid(row=6, column=0, padx=5, pady=5, sticky='w')
        комментарий = ttk.Entry(frame_заказ, width=30)
        комментарий.grid(row=6, column=1, padx=5, pady=5)

        def подтвердить_заказ():
            try:
                # Проверяем только категорию и тип
                if not категория.get() or not тип.get():
                    raise ValueError("Выберите категорию и тип")

                # Проверяем числовые значения только если они заполнены
                кол = int(количество.get()) if количество.get() else 0
                ц = float(цена.get()) if цена.get() else 0.0

                # Добавляем заказ в базу данных
                self.cursor.execute("""
                    INSERT INTO fittings_orders
                    (supplier_id, category, type, color, quantity, price, delivery_date, comment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    supplier_id,
                    категория.get(),
                    тип.get(),
                    цвет.get() if цвет.get() else None,
                    кол if кол > 0 else None,
                    ц if ц > 0 else None,
                    дата.get() if дата.get() else None,
                    комментарий.get() if комментарий.get() else None
                ))

                order_id = self.cursor.fetchone()[0]
                self.conn.commit()

                # Обновляем список заказов
                self.показать_заказы_поставщика(None)

                # Создаем сообщение о заказе
                сообщение = f"""
                Заказ успешно оформлен!

                Поставщик: {поставщик[0]}
                Категория: {категория.get()}
                Тип: {тип.get()}
                Цвет: {цвет.get() if цвет.get() else 'Не указан'}
                Количество: {кол if кол > 0 else 'Не указано'}
                Цена за единицу: {ц if ц > 0 else 'Не указана'} руб.
                Общая стоимость: {кол * ц if кол > 0 and ц > 0 else 'Не указана'} руб.
                Дата доставки: {дата.get() if дата.get() else 'Не указана'}
                Комментарий: {комментарий.get() if комментарий.get() else 'Нет'}
                """

                messagebox.showinfo("Заказ оформлен", сообщение)
                окно_заказа.destroy()

            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
            except Error as e:
                self.conn.rollback()
                messagebox.showerror("Ошибка базы данных", str(e))

        # Кнопки
        frame_кнопки = ttk.Frame(frame_заказ)
        frame_кнопки.grid(row=7, column=0, columnspan=2, pady=10)

        ttk.Button(frame_кнопки, text="Подтвердить", command=подтвердить_заказ).pack(side='left', padx=5)
        ttk.Button(frame_кнопки, text="Отмена", command=окно_заказа.destroy).pack(side='left', padx=5)

def все_заполнено(поля):
    return all(поле.strip() for поле in поля)

if __name__ == "__main__":
    import psycopg2
    from psycopg2 import Error
    import sys

    # Параметры подключения к базе данных
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'clothing_factory',
        'user': 'postgres',
        'password': 'Ostap_628',  # Обновленный пароль
        'port': '5432'
    }

    try:
        print("Попытка подключения к базе данных...")
        print(f"Параметры подключения: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

        # Подключаемся к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Подключение к базе данных успешно установлено!")

        # Создаем главное окно
        root = tk.Tk()
        root.title("Управление поставщиками")
        root.geometry("1200x800")

        # Создаем экземпляр SupplierGUI
        app = SupplierGUI(root, conn, cursor)

        # Запускаем главный цикл
        root.mainloop()

    except Error as e:
        print("\nОшибка при подключении к базе данных:")
        print(f"Код ошибки: {e.pgcode}")
        print(f"Сообщение: {e.pgerror}")
        print("\nПроверьте следующее:")
        print("1. PostgreSQL сервер запущен")
        print("2. База данных 'clothing_factory' существует")
        print("3. Пользователь 'postgres' имеет правильный пароль")
        print("4. Порт 5432 доступен")
        print("\nДля создания базы данных выполните:")
        print("1. psql -U postgres")
        print("2. CREATE DATABASE clothing_factory;")
        sys.exit(1)
    except Exception as e:
        print(f"\nНепредвиденная ошибка: {str(e)}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("\nСоединение с базой данных закрыто")
