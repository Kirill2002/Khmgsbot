from telebot.types import Message
import shelve
import random
from telebot import types
import telebot

TOKEN = '985809331:AAE7qf3r5K0ky-DcsN0Ruqvuwr6yr6C3YTk'
bot = telebot.TeleBot(TOKEN)

admin_id = 380499304
instapostcost = 5
codecost = 10
code_number = 1000

class Command:
    def __init__(self, type='start', mess_ago=0):
        self.type = type
        self.mess_ago = mess_ago

class User:
    def __init__(self, first_name, last_name, insta):
        self.first_name = first_name
        self.last_name = last_name
        self.insta = insta
        self.last_command = Command()
        self.points = 0
        self.attempts = 0

class Admin_info:
    def __init__(self):
        self.done_id = set()
        self.check_id = 0
        self.codes = set()

def admin_info_init():
    dbase = shelve.open('users')
    if 'admin_info' not in dbase.keys():
        dbase['admin_info'] = Admin_info()
    dbase.close()

admin_info_init()

def start(id):
    user = User('None', 'None', 'None')
    dbase = shelve.open('users')
    if str(id) in dbase.keys():
        bot.send_message(id, 'Здається, ми вже почали')
    else:
        dbase[str(id)] = user
        bot.send_message(id, 'Привіт, я Тарас!\nЯк вас зовуть?')
    dbase.close()

def points(id):
    dbase = shelve.open('users')
    bot.send_message(id, dbase[str(id)].points)
    dbase.close()

def checkdone(id):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Так')
    btn2 = types.KeyboardButton('Ні')
    markup.add(btn1, btn2)
    bot.send_message(id, 'Ви впевнені, що хочете відправити листа до Києва на перевірку свого завдання? Збрешете - ОБНУЛЮЮТЬ БАЛИ ТА ВІДПРАВЛЯТЬ В ЗАСЛАННЯ!!!', reply_markup=markup)

def done(id):
    dbase = shelve.open('users')
    admin_info = dbase['admin_info']
    if id in admin_info.done_id:
        bot.send_message(id, 'Зачекайте будь-ласка. Адмін не резиновий')
        dbase.close()
        return
    admin_info.done_id.add(id)
    if admin_info.done_id.__len__()==1:
        bot.send_message(admin_id, 'Хтось чекає на перевірку')
    dbase['admin_info'] = admin_info
    dbase.close()
    bot.send_message(id, 'Зараз перевіримо...')

def checkcount():
    dbase = shelve.open('users')
    admin_info = dbase['admin_info']
    bot.send_message(admin_id, admin_info.done_id.__len__())
    dbase.close()

def check():
    dbase = shelve.open('users')
    admin_info = dbase['admin_info']
    if admin_info.done_id.__len__()==0:
        bot.send_message(admin_id, 'Нема кого перевіряти')
        return
    user_id = random.choice(list(admin_info.done_id))
    admin_info.done_id.discard(user_id)
    admin_info.check_id = user_id
    dbase['admin_info']=admin_info
    user = dbase[str(user_id)]
    dbase.close()
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Всьо ОК!')
    btn2 = types.KeyboardButton('Нє, ну це бан!')
    markup.add(btn1, btn2)
    bot.send_message(admin_id, f'{user.first_name} {user.last_name} каже, що виконав завдання в Instagram\nДавайте перевіримо {user.insta}', reply_markup=markup)


def checked(sentence):
    dbase = shelve.open('users')
    admin_info = dbase['admin_info']
    if admin_info.check_id==0:
        bot.send_message(admin_id, 'Ви нікого не перевіряєте')
        dbase.close()
        return
    user = dbase[str(admin_info.check_id)]
    if sentence:
        user.points += instapostcost
        bot.send_message(admin_id, f'{user.first_name} успішно отримав свої бали')
        bot.send_message(admin_info.check_id, f'Вітаю, лови {str(instapostcost)} балів!')
    else:
        user.points = 0
        bot.send_message(admin_id, f'{user.first_name} отримав по заслузі...')
        bot.send_message(admin_info.check_id, 'Я ж попереджав(\nОбнуляю усі твої бали(')
    dbase[str(admin_info.check_id)] = user
    admin_info.check_id = 0
    dbase['admin_info'] = admin_info
    dbase.close()


def generate(number):
    dbase = shelve.open('users')
    admin_info = dbase['admin_info']
    random.seed()
    while len(admin_info.codes)<number:
        admin_info.codes.add(random.randint(1000000, 10000000))
    dbase['admin_info'] = admin_info
    dbase.close()
    f = open('codes.txt', 'w')
    for i in admin_info.codes:
        f.write(str(i) + '\n')
    f.close()
    f = open("codes.txt", 'rb')
    bot.send_document(admin_id, f)

def checkcode(id, text):
    dbase = shelve.open('users')
    admin_info = dbase['admin_info']
    user = dbase[str(id)]
    if int(text) in admin_info.codes:
        admin_info.codes.discard(int(text))
        user.points += codecost
        user.attempts = 0
        bot.send_message(id, f'Вітаю! +{str(codecost)} балів тобі!')
    else:
        user.attempts += 1
        if user.attempts==1:
            bot.send_message(id, 'Не вгадав...')
        elif (user.attempts>1) and (user.attempts<5):
            bot.send_message(id, f'Давай пограємо в гру!)\n5 невдалих спроб = я обнуляю тобі усі бали...\nP.S.{str(user.attempts)} ти вже використав')
        else:
            user.points = 0
            bot.send_message(id, 'Нє, ну я попереджав...')
    dbase['admin_info'] = admin_info
    dbase[str(id)] = user
    dbase.close()

def reset(id):
    user = User('None', 'None', 'None')
    dbase = shelve.open('users')
    dbase[str(id)] = user
    bot.send_message(id, 'Цього разу точно вийде!)\nЯк вас зовуть?')
    dbase.close()

def people():
    dbase = shelve.open('users')
    people = 'В заході беруть участь:\n'
    for i in dbase.keys():
        if i!='admin_info':
            user = dbase[i]
            people += f'{user.last_name} {user.first_name}: {str(user.points)}\n'
    people += f'Кількість людей: {dbase.__len__()-1}'
    dbase.close()
    bot.send_message(admin_id, people)

def send(text, photo_id='None'):
    dbase = shelve.open('users')
    if photo_id=='None':
        for i in dbase.keys():
            if (i!='admin_info') and (int(i)!=admin_id):
                bot.send_message(int(i), text)
    else:
        for i in dbase.keys():
            if (i!='admin_info') and (int(i)!=admin_id):
                bot.send_photo(chat_id=int(i), photo=photo_id, caption=text)
    dbase.close()

def thoughts(id):
    text = "Думи мої, думи мої,\nВи мої єдині,\nНе кидайте хоч ви мене\nПри лихій годині.\nПрилітайте, сизокрилі\nМої голуб'ята,\nІз-за Дніпра широкого\nУ степ погуляти\nЗ киргизами убогими.\nВони вже убогі,\nУже голі... Та на волі\nЩе моляться богу.\nПрилітайте ж, мої любі,\nТихими речами\nПривітаю вас, як діток,\nІ заплачу з вами.\n"
    bot.send_message(id, text)

def help(id):
    help = '/help - список команд\n/done - натисніть цю команду, якщо ви вже виконали завдання в Instagram(будеш брехати - обнулюю бали)\n/checkcode - перевірити код\n/points - кількість балів\n/reset - почати спочатку\n/thoughts - натисни'
    help_admin = '\n\n\nКоманди, доступні лише адміну(звичайний смертний не побачить їх у команді \help та не зможе ними користуватись):\n/send - розсилка користувачам\n/generate - нова партія кодів\n/checkcount - кількість людей, що очікують на перевірку\n/check - перевірити когось\n/people - список людей, що приймають участь'
    if admin_id==id:
        help += help_admin
    bot.send_message(id, help)

def is_reg(id):
    is_reg = True
    dbase = shelve.open('users')
    user = dbase[str(id)]
    if user.insta=='None':
        is_reg = False
    dbase.close()
    return is_reg


def text_analis(id, text):
    dbase = shelve.open('users')
    user = dbase[str(id)]
    user.last_command.mess_ago += 1
    dbase[str(id)] = user
    dbase.close()
    if id == admin_id:
        if 'Всьо ОК!' in text:
            checked(True)
        elif 'Нє, ну це бан!' in text:
            checked(False)
        elif user.last_command.type=='/checkcode' and user.last_command.mess_ago==1 and text.isdigit():
            checkcode(id, text)
        elif user.last_command.type=='/send' and user.last_command.mess_ago==1:
            send(text)
        elif user.last_command.type=='/done' and user.last_command.mess_ago==1 and text=='Так':
            done(id)
        elif user.last_command.type=='/done' and user.last_command.mess_ago==1 and text=='Ні':
            bot.send_message(id, 'Виконай завдання і я з радістю перевірю тебе')
        else:
            bot.send_message(admin_id, 'Будеш спамити - навіть не подивлюсь, що ти адмін. Забаню нахер!')  # изменить
    else:
        if user.last_command.type=='/checkcode' and user.last_command.mess_ago==1 and text.isdigit():
            checkcode(id, text)
        elif user.last_command.type=='/done' and user.last_command.mess_ago==1 and text=='Так':
            done(id)
        elif user.last_command.type=='/done' and user.last_command.mess_ago==1 and text=='Ні':
            bot.send_message(id, 'Виконай завдання і я з радістю перевірю тебе')
        else:
            bot.send_message(id, 'Давай ближче до справи. Обери потрібну команду і я тобі допоможу')

def comsave(id, text):
    dbase = shelve.open('users')
    user = dbase[str(id)]
    user.last_command.mess_ago=0
    user.last_command.type=text
    dbase[str(id)] = user
    dbase.close()

def reg(id, text):
    dbase = shelve.open('users')
    user = dbase[str(id)]
    if user.first_name=='None':
        user.first_name=text
        bot.send_message(id, f'Назвіть своє прізвище, {text}')
    elif user.last_name=='None':
        user.last_name=text
        bot.send_message(id, f'Надайте будь-ласка посилання на ваш Instagram-аккаунт, {user.first_name}')
    elif user.insta=='None':
        user.insta=text
        bot.send_message(id, 'Ви успішно зареєстровані')
    dbase[str(id)] = user
    dbase.close()


@bot.message_handler(commands=['start', 'help', 'points', 'done', 'checkcode', 'reset', 'thoughts'])
def command_handler(message: Message):
    if 'start' in message.text:
        start(message.chat.id)
    elif 'help' in message.text:
        help(message.chat.id)
    elif 'points' in message.text:
        points(message.chat.id)
    elif 'done' in message.text:
        comsave(message.chat.id, message.text)
        checkdone(message.chat.id)
    elif 'checkcode' in message.text:
        comsave(message.chat.id, message.text)
        bot.send_message(message.chat.id, 'Введіть код, будь-ласка')
    elif 'reset' in message.text:
        reset(message.chat.id)
    elif 'thoughts' in message.text:
        thoughts(message.chat.id)


@bot.message_handler(commands=['checkcount', 'check', 'generate', 'people', 'send'])
def admin_command_handler(message: Message):
    if message.chat.id==admin_id:
        comsave(message.chat.id, message.text)
        if 'checkcount' in message.text:
            checkcount()
        elif 'check' in message.text:
            check()
        elif 'generate' in message.text:
            generate(code_number)
        elif 'people' in message.text:
            people()
        elif 'send' in message.text:
            comsave(message.chat.id, message.text)
            bot.send_message(admin_id, 'Введіть текст повідомлення, яке ви хочете відправити користувачам')
    else:
        bot.send_message(message.chat.id, 'Давай ближче до справи. Обери потрібну команду і я тобі допоможу')


@bot.message_handler(content_types=['text'])
def message_handler(message: Message):
    if is_reg(message.chat.id):
        text_analis(message.chat.id, message.text)
    else:
        reg(message.chat.id, message.text)


@bot.message_handler(content_types=['photo'])
def photo_handler(message: Message):
    if message.chat.id==admin_id:
        dbase = shelve.open('users')
        user = dbase[str(message.chat.id)]
        user.last_command.mess_ago+=1
        if (user.last_command.type=='/send') and (user.last_command.mess_ago==1):
             send(text=message.caption, photo_id=message.photo[0].file_id)
        dbase[str(message.chat.id)] = user
        dbase.close()

bot.polling(none_stop=True, interval=0, timeout=120)
