import psycopg2
import configparser

'''Функция подключения к базе данных с переданнвми ей параметрами подключения, 
которые хранятся в файле config.ini'''
def connect_to_db(database,user,password):
    conn = psycopg2.connect(database = database, user = user, password = password)
    return conn

'''Функция которая выполняет удаление таблиц и создает новые. 
На вход принимает результат подключения к базе данных'''
def create_tables(conn):
    with conn.cursor() as cursor:
        print('Удаляем таблицы')
        cursor.execute('''
            DROP TABLE emails;
            DROP TABLE phones;
            DROP TABLE clients;
        ''')
        print('Удаление таблиц завершено')
        print('Создание таблицы CLIENTS')
        cursor.execute('''CREATE TABLE IF NOT EXISTS clients
                       (client_id SERIAL PRIMARY KEY NOT NULL,
                       first_nm VARCHAR(10) NOT NULL,
                       second_nm VARCHAR(10) NOT NULL)
                       ''')
        print('Создание таблицы PHONES')
        cursor.execute('''CREATE TABLE IF NOT EXISTS phones
                       (phone_id SERIAL PRIMARY KEY NOT NULL,
                       client_id INTEGER NOT NULL REFERENCES clients(client_id),
                       phone_num VARCHAR(12) CHECK (phone_num ~ '^[0-9+NA]'))
                       ''')
        print('Создание таблицы EMAILS')
        cursor.execute('''CREATE TABLE IF NOT EXISTS emails
                       (email_id SERIAL PRIMARY KEY NOT NULL,
                       client_id INTEGER NOT NULL REFERENCES clients(client_id),
                       email VARCHAR(50) NOT NULL UNIQUE CHECK (email ~* '[A-Z]@.'))
                       ''')
    conn.commit()
    conn.close
'''Функция, возвращающая результат в виде списка значений, 
который затем используется для добавления информации о новом телефоне клиента
Ввод необходимых значений осуществляется с клавиатуры'''
def input_client_data_to_add_phone():
    client_list = []
    first_name = input('Введите имя:').capitalize().strip()
    client_list.append(first_name)
    second_name = input('Введите фамилию:').capitalize().strip()
    client_list.append(second_name)
    phone = input('Введите номер телефона:').strip()
    if phone == "":
        phone = 'NA'
    client_list.append(phone)
    return client_list

'''Функция, возвращающая результат в виде списка значений, 
который затем используется для добавления информации о новом клиенте
Ввод необходимых значений осуществляется с клавиатуры'''
def input_client_data():
    client_list = []
    first_name = input('Введите имя:').capitalize().strip()
    client_list.append(first_name)
    second_name = input('Введите фамилию:').capitalize().strip()
    client_list.append(second_name)
    phone = input('Введите номер телефона:').strip()
    if phone == "":
        phone = 'NA'
    client_list.append(phone)
    email = input('Введите email:').strip()
    client_list.append(email.lower())
    return client_list

'''Функция, возвращающая результат в виде списка значений, 
который затем используется для обновления информации о клиенте
Ввод необходимых значений осуществляется с клавиатуры'''
def input_client_data_to_update():
    client_list = []
    first_name = input('Введите НОВОЕ имя:').capitalize().strip()
    client_list.append(first_name)
    second_name = input('Введите НОВУЮ фамилию:').capitalize().strip()
    client_list.append(second_name)
    phone = input('Введите НОВЫЙ номер телефона:').strip()
    if phone == "":
        phone = 'NA'
    client_list.append(phone)
    email = input('Введите НОВЫЙ email:').strip()
    client_list.append(email.lower())
    return client_list

'''Функция, возвращающая результат в виде списка значений, 
который затем используется для удаления информации о клиенте
Ввод необходимых значений осуществляется с клавиатуры'''
def input_client_data_to_delete():
    client_list = []
    first_name = input('Введите имя:').capitalize().strip()
    client_list.append(first_name)
    second_name = input('Введите фамилию:').capitalize().strip()
    client_list.append(second_name)
    return client_list

'''Функция, возвращающая результат в виде введенного значения, 
которое затем используется для выборки иныормации.
Ввод необходимых значений осуществляется с клавиатуры'''
def input_client_data_to_find():
    param = input('Введите значение:').lower().strip()
    return param

'''Функция добавления нового пользователя в БД. 
На вход принимает информацию о соединении, имя, фамилию, номер телефона и адрес электронной почты
В теле функции нет проверки на проверку существующего пользователя. 
Предполагается, что пользователь абсолютно новый.
'''
def add_new_user(conn,first_name,second_name,phone,email):
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO clients(first_nm, second_nm)"
                       "VALUES"
                         "(%s, %s) "
                       "RETURNING client_id",(first_name, second_name))
        id = cursor.fetchone()

        cursor.execute("INSERT INTO phones(client_id, phone_num)"
                       "VALUES (%s, %s)", (id[0], phone))

        cursor.execute("INSERT INTO emails(client_id, email)"
                       "VALUES"
                       "(%s, %s)", (id[0], email))
        conn.commit()

'''Функция добавления нового номера телефона существующего клиента. 
На вход принимает информацию о соединении, имя, фамилию и номер телефона.
В теле функции происходит поиск нужного пользователя с помощью SELECT и,
если он найден, то происходит обновление номера телефона.
'''
def add_phone(conn,first_name,second_name,phone):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM clients "
                       "WHERE first_nm = %s AND second_nm = %s",
                       (first_name, second_name))
        client_name = cursor.fetchone()
        if client_name:
            cursor.execute("SELECT phone_num, first_nm, second_nm FROM phones AS p "
                           "JOIN clients AS c "
                           "  ON c.client_id = p.client_id "
                           "WHERE phone_num = %s",
                           (phone,))
            phone_found = cursor.fetchone()
            if phone_found:
                print(f'Такой номер телефона уже существует для клиента "{phone_found[1]} {phone_found[2]}"')
            else:
                cursor.execute("INSERT INTO phones(client_id, phone_num)"
                               "VALUES (%s, %s)", (client_name[0], phone))
                conn.commit()
                print(f'Номер телефона для клиента "{first_name} {second_name}" добавлен')
        else:
            print(f'Клиента с именем {first_name} {second_name} не существует')

'''Функция обновление нового пользователя в БД. 
На вход принимает информацию о клиенте, для которого нужно внести изменения и обновленную информацию для него.
В теле функции выполняется поиск существующего клиента и сверка с НОВЫМИ введенными значениями
Ввод данных производится вручную с клавиатуры.
'''
def update_client(conn, first_name, second_name, phone, email, new_first_name, new_second_name, new_phone, new_email):
    with (conn.cursor() as cursor):
        cursor.execute("SELECT * FROM clients "
                       "WHERE first_nm = %s AND second_nm = %s",
                        (first_name, second_name))
        client_name = cursor.fetchone()

        cursor.execute("SELECT * FROM clients "
                       "WHERE first_nm = %s AND second_nm = %s",
                        (new_first_name, new_second_name))
        new_client_name = cursor.fetchone()
        if new_client_name:
            print(f'Клиент с именем {new_client_name[1]} {new_client_name[2]} уже существует')
        else:
            cursor.execute("SELECT phone_num, first_nm, second_nm FROM phones AS p "
                           "JOIN clients AS c "
                           "  ON c.client_id = p.client_id "
                           "WHERE phone_num = %s",
                           (new_phone,))
            phone_found = cursor.fetchone()
            if phone_found:
                print(f'Такой номер телефона уже существует для клиента "{phone_found[1]} {phone_found[2]}"')
            else:
                cursor.execute("SELECT email, first_nm, second_nm FROM emails AS e "
                                "JOIN clients AS c "
                                "  ON c.client_id = e.client_id "
                                "WHERE email = %s",
                                (new_email,))
                email_found = cursor.fetchone()
                if email_found:
                    print(f'Такой Email уже существует для клиента "{email_found[1]} {email_found[2]}"')
                else:
                    cursor.execute("UPDATE clients SET first_nm = %s "
                                   "WHERE client_id = %s",
                                    (new_first_name, client_name[0]))

                    cursor.execute("UPDATE clients SET second_nm = %s "
                                   "WHERE client_id = %s",
                                    (new_second_name,client_name[0]))

                    cursor.execute("UPDATE phones SET phone_num = %s "
                                   "WHERE phone_num = %s",
                                    (new_phone,phone))

                    cursor.execute("UPDATE emails SET email = %s "
                                   "WHERE email = %s",
                                    (new_email, email))
                    conn.commit()
                    print(f'Данные для клиента "{first_name} {second_name}" обновлены данными\n '
                          f'Имя: {new_first_name}\n Фамилия: {new_second_name}\n Телефон: {new_phone}\n Email: {new_email}')

'''Функция удаления номера телефона из БД для указанного клиента. 
На вход принимает информацию о клиенте, для которого нужно удалить номер телефона.
В теле функции выполняется поиск существующего клиента и номер введенного телефона для удаления.
Ввод данных производится вручную с клавиатуры.
'''
def delete_phone(conn, first_name, second_name, phone):
    with (conn.cursor() as cursor):
        with (conn.cursor() as cursor):
            cursor.execute("SELECT * FROM clients "
                           "WHERE first_nm = %s AND second_nm = %s",
                           (first_name, second_name))
            client_name = cursor.fetchone()

            if client_name:
                cursor.execute("SELECT phone_num, first_nm, second_nm FROM phones AS p "
                               "JOIN clients AS c "
                               "  ON c.client_id = p.client_id "
                               "WHERE phone_num = %s",
                               (phone,))
                phone_found = cursor.fetchone()
                if phone_found:
                    cursor.execute("DELETE FROM phones "
                                   "WHERE phone_num = %s",
                                   (phone,))
                    conn.commit()
                    print(f'Номер телефона "{phone}" для клиента "{first_name} {second_name}" удален.')
                else:
                    print(f'Такой номер телефона для клиента "{first_name} {second_name}" не существует.')
            else:
                print(f'Клиент с именем "{first_name} {second_name}" не существует.')

'''Функция удаления данных о клиенте.
На вход принимает информацию о клиенте, которого нужно удалить из БД.
Ввод данных производится вручную с клавиатуры.
'''
def delete_client(conn, first_name, second_name):
    with (conn.cursor() as cursor):
        cursor.execute("SELECT * FROM clients "
                        "WHERE first_nm = %s AND second_nm = %s",
                        (first_name, second_name))
        client_name = cursor.fetchone()

        if client_name:
            cursor.execute("DELETE FROM emails "
                            "WHERE client_id = %s",
                            (client_name[0],))

            cursor.execute("DELETE FROM phones "
                            "WHERE client_id = %s",
                            (client_name[0],))

            cursor.execute("DELETE FROM clients "
                            "WHERE client_id = %s",
                            (client_name[0],))
            conn.commit()
            print(f'Данные о клиенте "{first_name} {second_name}" удалены.')
        else:
            print(f'Клиент с именем "{first_name} {second_name}" не существует.')

'''Функция поиска клиента по имени, может производиться ввод часть имени
 в результате чего будут выведены все клиенты, удовлетворяющих условию.
Ввод данных производится вручную с клавиатуры.
'''
def select_client_name(conn, first_name):
    with (conn.cursor() as cursor):
        cursor.execute("""
                        SELECT first_nm, second_nm, email, phone_num  FROM clients c 
                        JOIN emails e 
                         on c.client_id = e.client_id 
                        JOIN phones p 
                         on c.client_id = p.client_id 
                        WHERE UPPER(first_nm) LIKE %s;
                        """, (f'%{first_name.upper()}%',))
        print(*[' '.join(item) +'\n' for item in cursor.fetchall()])

'''Функция поиска клиента по фамилии, может производиться ввод часть фамилии
 в результате чего будут выведены все клиенты, удовлетворяющих условию.
Ввод данных производится вручную с клавиатуры.
'''
def select_client_surname(conn, second_name):
    with (conn.cursor() as cursor):
        cursor.execute("""
                        SELECT first_nm, second_nm, email, phone_num  FROM clients c 
                        JOIN emails e 
                         on c.client_id = e.client_id 
                        JOIN phones p 
                         on c.client_id = p.client_id 
                        WHERE UPPER(second_nm) LIKE %s;
                        """, (f'%{second_name.upper()}%',))
        print(*[' '.join(item) +'\n' for item in cursor.fetchall()])

'''Функция поиска клиента по номеру телефона, может производиться ввод часть номера телефона
 в результате чего будут выведены все клиенты, удовлетворяющих условию.
Ввод данных производится вручную с клавиатуры.
'''
def select_client_phone(conn, phone):
    with (conn.cursor() as cursor):
        cursor.execute("""
                        SELECT first_nm, second_nm, email, phone_num  FROM phones p 
                        JOIN emails e 
                         on p.client_id = e.client_id 
                        JOIN clients c 
                         on c.client_id = p.client_id 
                        WHERE phone_num LIKE %s;
                        """, (f'%{phone}%',))
        print(*[' '.join(item) +'\n' for item in cursor.fetchall()])

'''Функция поиска клиента по Email, может производиться ввод часть Email
 в результате чего будут выведены все клиенты, удовлетворяющих условию.
Ввод данных производится вручную с клавиатуры.
'''
def select_client_email(conn, email):
    with (conn.cursor() as cursor):
        cursor.execute("""
                        SELECT first_nm, second_nm, email, phone_num  FROM emails e 
                        JOIN clients c 
                         on c.client_id = e.client_id 
                        JOIN phones p 
                         on e.client_id = p.client_id 
                        WHERE LOWER(email) LIKE %s;
                        """, (f'%{email.lower()}%',))
        print(*[' '.join(item) +'\n' for item in cursor.fetchall()])

if __name__ == '__main__':
    config = configparser.ConfigParser()

    # Чтение файла конфигурации
    config.read('config.ini')

    # Получение данных из файла конфигурации
    access_db = config.get('Settings', 'database')
    access_user = config.get('Settings', 'user')
    access_password = config.get('Settings', 'password')

    # Подключение к БД
    conn = connect_to_db(access_db, access_user, access_password)

    # Переменные диалога программы, будем их использовать ниже для диалога с пользователем
    rqst_to_create_new_user = 'Вы хотите продолжить и создать нового клиента?: Y/N\n'
    rqst_to_add_phone_num = 'Добавить номер телефона?: Y/N\n'
    rqst_to_update_client = 'Изменить данные о пользователе?: Y/N\n'
    rqst_to_delete_phone = 'Удалить телефон из базы для указанного клиента?: Y/N\n'
    rqst_to_delete_client = 'Удалить указанного клиента и его данные из базы?: Y/N\n'
    rqst_to_select_client = 'Выполнить поиск клиента?: Y/N\n'

    # Предлагаем пользователю создать новый набор таблиц к сущесвующей БД или продолжить с уже имеющимся
    q_to_remove_db = input('Вы хотите создать новые таблицы?: Y/N\n')
    if q_to_remove_db.lower() == "y": # если пользователь выбрал Y, то подключаемся к БД и удаляем существующие таблицы
        create_tables(conn)
        print('База данных и таблицы к ней созданы')
        q_to_continue = input(rqst_to_create_new_user) # запрашиваем продолжить работу с БД или нет
        while q_to_continue.lower() != "n": # будем запрашивать и добавлять клиентов до тех пор, пока не выбран ответ N
            client = input_client_data() # в переменную Client кладем полученную информацию о пользователе
            add_new_user(conn, client[0], client[1], client[2], client[3]) # вызов функции добавления нового пользователя
            q_to_continue = input(rqst_to_create_new_user)
    else:
        q_to_continue = input(rqst_to_create_new_user)
        while q_to_continue.lower() != "n": # будем запрашивать и добавлять пользователй до тех пор, пока не выбран ответ N
            client = input_client_data() # в переменную Client кладем полученную информацию о пользователе
            add_new_user(conn, client[0], client[1], client[2], client[3]) # вызов функции добавления нового пользователя
            q_to_continue = input(rqst_to_create_new_user)

        q_to_add_phone = input(rqst_to_add_phone_num) # запрашиваем о добавлении нового номера телефона
        while q_to_add_phone.lower() != "n": # будем запрашивать и добавлять номера до тех пор, пока не выбран ответ N
            client = input_client_data_to_add_phone() # в переменную Client кладем полученную информацию о пользователе
            add_phone(conn, client[0], client[1], client[2]) # вызов функции добавления нового номера телефона
            q_to_add_phone = input(rqst_to_add_phone_num)

        q_to_update = input(rqst_to_update_client) # запрашиваем об обновлении данных о клиенте
        while q_to_update.lower() != "n": # будем запрашивать и обновлять данные о клиенте до тех пор, пока не выбран ответ N
            client = input_client_data() # в переменную Client кладем полученную информацию о пользователе
            client_upd = input_client_data_to_update()  # вызов функции обновления данных о клиенте
            update_client(conn, client[0], client[1], client[2], client[3],
                          client_upd[0], client_upd[1], client_upd[2], client_upd[3])
            q_to_update = input(rqst_to_update_client)

        q_to_delete_phone = input(rqst_to_delete_phone) # запрашиваем об удалении номера телефона
        while q_to_delete_phone.lower() != "n": # будем запрашивать и удалять данные до тех пор, пока не выбран ответ N
            client = input_client_data_to_add_phone() # в переменную Client кладем полученную информацию о пользователе
            delete_phone(conn, client[0], client[1], client[2]) # вызов функции удаления номера телефона
            q_to_delete_phone = input(rqst_to_delete_phone)

        q_to_delete_client = input(rqst_to_delete_client) # запрашиваем об удалении клиента
        while q_to_delete_client.lower() != "n": # будем запрашивать и удалять данные до тех пор, пока не выбран ответ N
            client = input_client_data_to_delete() # в переменную Client кладем полученную информацию о пользователе
            delete_client(conn, client[0], client[1]) # вызов функции удаления номера телефона
            q_to_delete_client = input(rqst_to_delete_client)

        q_to_select_client = input(rqst_to_select_client) # запрашиваем о поиске клиента по указанному критерию
        while q_to_select_client.lower() != "n": # будем запрашивать до тех пор, пока не выбран ответ N
            q_to_select_client_name = input("По имени: Y/N\n") # запрос поиска по имени
            if q_to_select_client_name.lower() == "y":
                client = input_client_data_to_find()
                select_client_name(conn, client)
            else:
                q_to_select_client_surname = input("По фамилии: Y/N\n") # запрос поиска по фамилии
                if q_to_select_client_surname.lower() == "y":
                    client = input_client_data_to_find()
                    select_client_surname(conn, client)
                else:
                    q_to_select_client_phone = input("По телефону: Y/N\n") # запрос поиска по телефону
                    if q_to_select_client_phone.lower() == "y":
                        client = input_client_data_to_find()
                        select_client_phone(conn, client)
                    else:
                        q_to_select_client_email = input("По Email: Y/N\n") # запрос поиска по Email
                        if q_to_select_client_email.lower() == "y":
                            client = input_client_data_to_find()
                            select_client_email(conn, client)
            q_to_select_client = input(rqst_to_select_client)

print('Программа завершена')
