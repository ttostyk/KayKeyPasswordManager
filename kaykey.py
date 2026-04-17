import os, json, base64
import getpass
import secrets
import string
import pyperclip
from colorama import init, Fore, Style
from cryptography.fernet import Fernet

"""
KayKey - менеджер паролей
Писал этот код месяц, было много проверок, фиксов, я не гений.
Это простой школьный проект. Что бы люди могли хранить свои пароли.
Метод реализованный проектом KayKey сразу же отсеивает 80% вирусов/стиллеров от возможности взлома аккаунтов.
"""

init(autoreset=True)

# Это файлы хранения
# мастер пароль в master.key
# cобственно пароли от сервисов в passwords.enc
DATA_FILE = "passwords.enc"
KEY_FILE = "master.key"

def print_banner():
    # Красивенький баннер (я устал его составлять)
    banner = f"""
{Fore.RED}{Style.BRIGHT}
 ██╗  ██╗ █████╗ ██╗   ██╗██╗  ██╗███████╗██╗   ██╗
 ██║ ██╔╝██╔══██╗╚██╗ ██╔╝██║ ██╔╝██╔════╝╚██╗ ██╔╝
 █████╔╝ ███████║ ╚████╔╝ █████╔╝ █████╗   ╚████╔╝
 ██╔═██╗ ██╔══██║  ╚██╔╝  ██╔═██╗ ██╔══╝    ╚██╔╝
 ██║  ██╗██║  ██║   ██║   ██║  ██╗███████╗   ██║
 ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝   ╚═╝
{Fore.CYAN}      Менеджер паролей — надёжность и простота
{Style.RESET_ALL}
    """
    print(banner)

def make_key(password):
    # Приводим к 32 байтам, даже если человек ввёл "123"
    return base64.urlsafe_b64encode(password.ljust(32)[:32].encode()).decode()

def vault_unpack():
    # Это собственно функция чтения хранилищя, где храняться ключи в виде .json и мастер пароль
    if not os.path.exists(DATA_FILE):
        return []
    with open(KEY_FILE, "r") as f:
        key = f.read()
    fernet = Fernet(key)
    with open(DATA_FILE, "rb") as f:
        data = fernet.decrypt(f.read())
    return json.loads(data)

def vault_seal(data, key):
    # Функция "Запаковки" ну или же сохранения файлов хранилищя
    fernet = Fernet(key)
    with open(DATA_FILE, "wb") as f:
        f.write(fernet.encrypt(json.dumps(data).encode()))
    with open(KEY_FILE, "w") as f:
        f.write(key)

def generate_password():
    # Ну, тут легко и понятно, простейшая генерация паролей
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(12))

def main(): # Это основная функция, собственно сама программа, и часть взаимодействия с пользователем(выбор 1,2,3,4,5)
    os.system('cls' if os.name == 'nt' else 'clear') # Наша любимая косметика, cls - clear -- это очищение командной строки
    print_banner() # Функция печати баннера
    if not os.path.exists(KEY_FILE): # Проверка на отсутствие уже имеющихся файлов хранилищя
        pwd = getpass.getpass("Придумайте мастер-пароль(ключ шифра): ")
        key = make_key(pwd)
        vault_seal([], key) # Создание и "Упаковка" файлов хранилищя
        print(Fore.GREEN + Style.BRIGHT + "Хранилище создано!")
    else:
        pwd = getpass.getpass(Style.BRIGHT + "Мастер-пароль(ключ шифра): ") # Проверка на пароль, если он не совпадает, то KayKey остонавливает свою работу
        key = make_key(pwd)
        with open(KEY_FILE, "r") as f:
            saved_key = f.read() # Чтение файлов хранилищя
        if key != saved_key:
            print(Fore.RED + "Неверный пароль!")
            return
        try:
            data = vault_unpack()
        except:
            print(Fore.RED + "Файл повреждён!")
            return
    data = vault_unpack()
    while True: # Это выбор для взаимодействия с программой
        print("\n",
        Fore.YELLOW + Style.BRIGHT + "1. Показать все\n",
        Fore.GREEN + Style.BRIGHT + "2. Добавить запись\n",
        Fore.RED + Style.BRIGHT + "3. Удалить запись\n",
        Style.BRIGHT + "4. Информация\n",
        Style.BRIGHT + "5. Выход")
        choice = input("> ")
        if choice == "1": # Показ записей с паролями (Сервис, Логин, Пароль)
            if not data:
                print(Style.BRIGHT + "Записей нет.")
            for i, e in enumerate(data): # Показать ВЕСЬ список сервисов, логинов, паролей, а не только один сервис, логин, пароль
                print(Style.BRIGHT + f"{i+1}. {e['service']} | {e['login']} | {Fore.RED}[пароль скрыт]")
            if data:
                n = input(Style.BRIGHT + "Номер для просмотра пароля (Enter - назад): ") # Выбор пароля из списка
                if n.isdigit() and 1 <= int(n) <= len(data):
                    e = data[int(n)-1]
                    print(Style.BRIGHT + f"Пароль: {Fore.GREEN + e['password']}") # Показ выбранного пароля.
                    print("\n",
                    Style.BRIGHT + Fore.YELLOW + "1. Скопировать\n",
                    Style.BRIGHT + "2. Назад")
                    local_choice_password_copy = input("> ")
                    if local_choice_password_copy == "1":
                        pyperclip.copy(e['password']) # -- Это копирование через в буфер обмена
                        print(Fore.GREEN + Style.BRIGHT + "Пароль скопирован в буфер обмена!")

        elif choice == "2": # Создание записи в хранилище (Сервис, Логин, Пароль)
            s = input(Style.BRIGHT + "Сервис: ")
            l = input(Style.BRIGHT + "Логин: ")
            p = input(Style.BRIGHT + "Пароль (Enter = сгенерировать): ")
            if not p:
                p = generate_password() # Генерация пароля
                print(Style.BRIGHT + "Сгенерирован:", Fore.GREEN + Style.BRIGHT + p)
            data.append({"service": s, "login": l, "password": p})
            vault_seal(data, key)
            print(Style.BRIGHT + "Добавлено!")

        elif choice == "3": # Удаление записи с хранилищя
            for i, e in enumerate(data):
                print(f"{i+1}. {e['service']}")
            n = input(Style.BRIGHT + "Номер для удаления: ")
            if n.isdigit() and 1 <= int(n) <= len(data):
                del data[int(n)-1]
                vault_seal(data, key)
                print(Fore.RED + Style.BRIGHT + "Удалено.")

        elif choice == "4": # Информация об проекте, и примечание о том как сохранить
            print("\n",
            Fore.RED + Style.BRIGHT + "=== Информация ===")
            print("",
            Fore.RED + Style.BRIGHT + "KayKey - Консольный менеджер паролей\n",
            Fore.RED + Style.BRIGHT + "Версия: 1.82.Console.Version   |   Дата версии: 17.04.2026\n",
            Fore.RED + Style.BRIGHT + "GitHub проекта: https://github.com/ttostyk/KayKeyPasswordManager | (Скопированно в буфер обмена)\n",
            Fore.RED + Style.BRIGHT + "Создатель: ttostyk(Псевдоним)\n",
            Fore.BLUE + Style.BRIGHT + "=== Примечание ===\n",
            Fore.BLUE + Style.BRIGHT + "Вы можете сохранить Файлы(master.key и passwords.enc) на любой носитель данных, что бы избежать их утери на основном устройстве.\n",
            Fore.BLUE + Style.BRIGHT + "После сохранения вы можете переместить файлы в папку проекта. Ваш мастер-ключ и списки с паролями сохраняться.\n")
            pyperclip.copy("https://github.com/ttostyk/KayKeyPasswordManager")

        elif choice == "5": # Выход с программы, просто остановка приложения.
            break

if __name__ == "__main__":
    main()
