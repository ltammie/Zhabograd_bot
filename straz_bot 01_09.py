import sqlite3
from telethon import TelegramClient
from telethon import events
from random import randint
from os import listdir
from datetime import datetime
from telethon.tl.custom import Button

def connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print('Connect')
    except:
        print('Nope')
    return connection

def chek_user(user_id):
    cursor.execute("SELECT * FROM zaba where id_u = {}".format(user_id))
    user = cursor.fetchone()
    return user
        
def energy_check(user):
    cursor.execute("SELECT * FROM working where id_u = {}".format(user[0]))
    data_w = cursor.fetchone()
    if data_w[1] == 0:
            raznica = (datetime.now() - datetime.strptime(data_w[2], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()//60
            if (user[6] + raznica) >  user[2]:
                cursor.execute("UPDATE zaba SET  current_energy = energy WHERE id_u= {}".format(user[0]))
                connect.commit()
            else:
                cursor.execute("UPDATE zaba SET  current_energy = current_energy + ? WHERE id_u= ?",(str(raznica), user[0]))
                connect.commit()
            cursor.execute("UPDATE working SET data_nachala = ? WHERE id_u= ?",(datetime.now(), user[0]))
            connect.commit()

async def lvl_exp_check(user_id, exp, lvl, max_energy):
    levels = [[1, 100], [2, 300], [3, 500], [4, 700], [5, 900], [6, 1100], [7, 1300], [8, 1500], [9, 1700], [10, 1900]]
    if exp > levels[lvl-1][1]:
        exp -= levels[lvl-1][1]
        lvl += 1
        max_energy += randint(30,50)        
        await client.send_message(user_id,'Вы получили новый уровень!\n Ваш текущий уровень {}.\n Количество максимальной энергии увеличилось {}.\n Трата сил на работу уменьшилась на 1!'.format(lvl, max_energy))
    return max_energy, exp, lvl
        
def novaya_frog(id_chela):
    img = listdir('./images')
    energy = randint(30,60)
    data = (id_chela, 1, energy, 0, img[randint(1,len(img)-1)], 'Noname', energy, 0)

    cursor.execute("INSERT INTO zaba VALUES (?,?,?,?,?,?,?,?)",(data))
    connect.commit()
    cursor.execute("INSERT INTO working VALUES (?,?,?)",(id_chela, 0, datetime.now()))
    connect.commit()
    cursor.execute("select id_t, emoji from tovars")
    data_tovar = cursor.fetchall()
    
    for i in data_tovar:
        cursor.execute("INSERT INTO inventory VALUES (?,?,?,?)",(id_chela, i[0], 0, i[1]))
        connect.commit()
    
    text = '''
Ваша Жаба!

Уровень \U0001F438: {}
Опыт \U0001F9E0: {}
Энергия \U000026A1: {}/{}
Фрогекоины \U0001F4B0: {}
    '''.format(data[1], data[7], data[6], data[2], data[3])      

    return text, data[4]

###################################### Function END

api_id = 'your token' 
api_hash = 'your token'

bot_token = 'your token'
client = TelegramClient('mmo_bot', api_id, api_hash).start(bot_token = bot_token)

connect = connection('zaba')
cursor = connect.cursor()

#Новая жаба
@client.on(events.NewMessage(pattern='/new_jaba'))
async def new_jaba(event):
    #Данные юзера
    user = chek_user(event.message.peer_id.user_id)

    if user != None:
        await event.respond('У вас уже есть Жаба, вы точно хотите получить новую жабу? Вы потеряете все деньги, предметы и уровни!',
                      buttons = [Button.inline('Конечно', b'yes'),
                                Button.inline('Никак нет', b'no')])
    elif user == None:

        text, img = novaya_frog(event.message.peer_id.user_id)    
        await event.respond(text, file = 'images/' + img)

@client.on(events.CallbackQuery(data = b'no'))      
async def nothing(event):
    await event.respond('Вот и славно')
    
@client.on(events.CallbackQuery(data = b'yes'))      
async def delete_zaba(event):
    cursor.executescript("DELETE FROM zaba WHERE id_u = {0};DELETE FROM working WHERE id_u = {0};DELETE FROM inventory WHERE id_u = {0}".format(event.original_update.user_id))    
    text, img = novaya_frog(event.original_update.user_id)
    await event.respond(text, file = 'images/' + img)

    
@client.on(events.NewMessage(pattern='/inventory'))
async def inventory(event):
    user = chek_user(event.message.peer_id.user_id)
    
    if user != None: 
        try:
            cursor.execute('SELECT kolvo, emoji, id_t FROM inventory WHERE id_u = {}'.format(event.message.peer_id.user_id))
        except:
            cursor.execute('SELECT kolvo, emoji, id_t FROM inventory WHERE id_u = {}'.format(event.original_update.message.from_id.user_id))

        data_tovara = cursor.fetchall()
        buttons = []
        for i in data_tovara:
            buttons.append([Button.inline('{} - {}'.format(i[1],i[0]), 'I'+i[2])])

        await event.respond('Ваш инвентарь:', buttons = buttons)
    else:
        await event.respond('У вас нет жабки, не хотите получить жабку? /new_jaba')
#Name
@client.on(events.NewMessage(pattern='/set_name'))
async def set_name(event):
    user = chek_user(event.message.peer_id.user_id)
    
    if user != None:        
        text = event.message.message.split('/set_name')
        name = ' '.join(text[1].split())        
        cursor.execute("UPDATE zaba SET name = ? WHERE id_u= ?",(name, user[0]))
        connect.commit()
    else:
        await event.respond('У вас нет жабки, не хотите получить жабку? /new_jaba')

@client.on(events.NewMessage(pattern='/my_jaba'))
async def my_jaba(event):
    user = chek_user(event.message.peer_id.user_id)
    if user != None:
        
        energy_check(user)  

        img = listdir('./images')
        user = chek_user(user[0])
        
        text = '''
Ваша Жаба!

Имя: {}
Уровень \U0001F438: {}
Опыт \U0001F9E0: {}
Энергия \U000026A1: {}/{}
Фрогекоины \U0001F4B0: {}
    '''.format(user[5], user[1], user[7], user[6], user[2], user[3])           

        await event.respond(text, file = 'images/' + user[4])
    else:
        await event.respond('У вас нет жабки, не хотите получить жабку? /new_jaba')
        
@client.on(events.NewMessage(pattern='/rabota'))
async def rabota(event):
    user = chek_user(event.message.peer_id.user_id)
    
    
    if user != None:
        cursor.execute("SELECT * FROM working where id_u = {}".format(event.message.peer_id.user_id))
        data_w = cursor.fetchone()
        if data_w[1] > 0:
            await event.respond("Жабка на работе, если хочешь вернуть домой нажми домой /home")
        else:
            energy_check(user)
            user = chek_user(user[0])
            await event.respond('Ваш уровень энергии \U000026A1: {}\{}'.format(user[6],user[2]))
            await event.respond('Выберите работу',
                                buttons = [[Button.inline('Прыгатель по кувшникам', '1')],
                                           [Button.inline('Ловец комаров', '2')],
                                           [Button.inline('Инспектор по червям', '3')],
                                           [Button.inline('Контрабандист икринок', '4')]])
    else:
        await event.respond('У вас нет жабки, не хотите получить жабку? /new_jaba')

@client.on(events.NewMessage(pattern='/home'))
async def home(event):
    
    cursor.execute("SELECT * FROM working where id_u = {}".format(event.message.peer_id.user_id))
    data_w = cursor.fetchone()
    
    if data_w[1] == 0:
        await event.respond('Ваша Жаба отдыхает дома')
    elif data_w[1] > 0:
        user = chek_user(event.message.peer_id.user_id)

        cursor.execute("SELECT * FROM rabota where id = {}".format(data_w[1]))
        data_r = cursor.fetchone()
        
        raznica = (datetime.now() - datetime.strptime(data_w[2], '%Y-%m-%d %H:%M:%S.%f')).total_seconds()//60
    #Подсчет сложности
        if user[1] >= data_r[3]:
            sloznost = 1
        else:
            sloznost = data_r[3] - user[1] + 1
    #Подсчет денег и энергии в зависимости от сложности
        if raznica > user[6]//sloznost:
            money = int(data_r[2]*user[6]/sloznost)
            energy = int((user[6]//sloznost)*sloznost)            
        else:
            money = int(data_r[2]*raznica)
            energy = int(raznica*sloznost)
    #Вероятность плохого хорошего события или никакого
        chance_sobitie = randint(0,100)
        

        if user[1] >= data_r[4]:
            chance_proval = 1
        else:
            chance_proval = data_r[4] - user[1] + 1
        if raznica > 10:
            if user[1] >= 1:
                chance_good = 100 - data_r[5] - user[1] + 1
        else: chance_good = 101
        #print('Вероятность события',chance_sobitie)
        #print('Вероятность хорошего расклада',chance_good)
        #print('Вероятность плохого расклада',chance_proval)
        if  chance_sobitie <=  chance_proval:
            cursor.execute('SELECT * FROM sobitie where id = {} and id_s = 0'.format(data_r[0]))
        elif chance_sobitie >=  chance_good:
            cursor.execute('SELECT * FROM sobitie where id = {} and id_s = 1'.format(data_r[0]))
        else:
            cursor.execute('SELECT * FROM sobitie where id = {} and id_s = 2'.format(data_r[0]))

        data_s = cursor.fetchall()
        data_s = data_s[randint(0, len(data_s)-1)]
        print(data_s)
        if data_s[0] == 0: #bad
            money -= data_s[3]
            await event.respond('{}\nВы потеряли:{}'.format(data_s[2],data_s[3]))
        elif data_s[0] == 1: #good
            money += data_s[3]
            await event.respond('{}\nВы получили:{}'.format(data_s[2],data_s[3]))
        elif data_s[0] == 2:
            await event.respond('{}'.format(data_s[2]))
                

        
        max_energy, exp, lvl = await lvl_exp_check(user[0],int(money/2)+user[7],user[1],user[2])
        cursor.execute("UPDATE zaba SET frogecoins = frogecoins + ?, current_energy = current_energy - ?, exp = ?, lvl = ?, energy = ? WHERE id_u= ?", (money, energy, exp, lvl, max_energy, user[0]))
        connect.commit()        
        cursor.execute("UPDATE working SET id = 0, data_nachala = ? WHERE id_u= ?",(datetime.now(), event.message.peer_id.user_id))
        connect.commit()
        
        text = '''
Ваша жаба заработала: {} \U0001F4B0
Ваша жаба потратила энергии: {} \U000026A1
Ваша жаба заработала опыта \U0001F9E0: {}
Время на работе: {} минут \U0000231B'''.format(money, energy , int(money/2), int(raznica))
        await event.respond(text)

@client.on(events.CallbackQuery())
async def knopki(event):
    dannie_knopki = event.data.decode('utf-8')
    user = event.original_update.user_id
    print(event)
    if dannie_knopki.isdigit():
        cursor.execute("UPDATE working SET id = ?, data_nachala = ? WHERE id_u= ?",(dannie_knopki, datetime.now(), user))
        connect.commit()
        await event.answer('\U0001F438 побежала на работу')
        await event.edit('Убежала на работу..')
        
    elif dannie_knopki[0] == 'I':
        cursor.execute("update inventory set kolvo = case when (SELECT kolvo FROM inventory WHERE id_u= {0} AND id_t= {1}) > 0 then kolvo - 1 else 0 end WHERE id_u = {0} and id_t= {1}".format(user,'\''+dannie_knopki[1:]+'\''))
        connect.commit()
        cursor.execute('UPDATE zaba SET current_energy = case when current_energy + (SELECT buff_energy FROM tovars WHERE id_t = {1}) < energy then current_energy + (SELECT buff_energy FROM tovars WHERE id_t = {1}) else energy end WHERE id_u = {0}'.format(user,'\''+dannie_knopki[1:]+'\''))
        connect.commit()

        cursor.execute('SELECT kolvo, emoji, id_t FROM inventory WHERE id_u = {}'.format(user))
        data_tovara = cursor.fetchall()
                
        buttons = []
        for i in data_tovara:
            buttons.append([Button.inline('{} - {}'.format(i[1],i[0]),'I'+i[2])])
        try:    
            await event.edit('Ваш инвентарь:', buttons = buttons)
            await event.answer('Мммм вкусно')
        except Exception: await event.answer('Nope')
            
    #else:
        
        
        

    
client.start()
client.run_until_disconnected()
