from telethon import TelegramClient
from telethon import events
from telethon.tl.custom import Button
from telethon.tl.types import MessageEntityBotCommand, MessageEntityMention
import sqlite3

def connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print('Connect')
    except:
        print('Nope')
    return connection

def chek_user(user_id, cursor):
    cursor.execute("SELECT * FROM zaba where id_u = {}".format(user_id))
    user = cursor.fetchone()
    return user

api_id = 'your token' 
api_hash = 'your token'
bot_token = 'your token'

connect = connection('zaba')
cursor = connect.cursor()


client = TelegramClient('mmo_traktir_bot', api_id, api_hash).start(bot_token = bot_token)
    
@client.on(events.NewMessage(pattern='/buy'))
async def buy(event):
    
    cursor.execute('SELECT * FROM tovars')
    data_tovara = cursor.fetchall()
    buttons = []
    for i in data_tovara:
        buttons.append([Button.inline('{} - {}\U0001F4B0 - {}\U000026A1'.format(i[4], i[2], i[3]), i[0])])
    
    await event.respond('Выбирайте, чем хотите сегодня насладиться:',buttons = buttons)


@client.on(events.NewMessage(pattern='/napitki'))
async def napitki(event):
    
    cursor.execute('SELECT * FROM tovars')
    data_tovara = cursor.fetchall()
    text = ''
    for i in data_tovara:
        text += '{} - {}.\n Стоимость \U0001F4B0: {}.\n Получаемая энергия \U000026A1: {}\n-----------------------------\n'.format(i[4], i[1], i[2], i[3]) 
    await event.respond(text)

    
@client.on(events.CallbackQuery())
async def knopki(event):
    
    user = chek_user(event.original_update.user_id,cursor)
    tovar = event.original_update.data.decode('utf-8')
    
    cursor.execute('SELECT * FROM tovars WHERE id_t = \'{}\''.format(tovar))
    data_tovara = cursor.fetchone()
               
            
    if user[3] - data_tovara[2] >= 0:
        cursor.execute("UPDATE zaba SET frogecoins = frogecoins - ? WHERE id_u= ?",(data_tovara[2],user[0]))
        connect.commit()
        cursor.execute('UPDATE inventory SET kolvo = kolvo + 1 WHERE id_u= ? AND id_t= ?',(user[0],tovar))
        connect.commit()
        await event.answer('Куплено')
    else:
        await event.answer('У вас недостаточно монет')               
   
@client.on(events.NewMessage(chats = '@taverna_Zhabograd'))
async def pokupka_tovarov_for_friends(event):
    
    if event.original_update.message.entities != None:
        if type(event.original_update.message.entities[0]) != MessageEntityBotCommand:
            
            try:
                user_who_take = chek_user(event.original_update.message.entities[0].user_id, cursor)
            except:
                user_who_take = chek_user(1045489755,cursor)
            if user_who_take == None:
                await event.respond('У пользователя нет жабы')
        #else: 
        #    await event.respond('Непонятного кому вы хотите купить пиво, попробуйте снова')

        #
            print(event.original_update)
            try:
                user_who_buy = chek_user(event.original_update.message.from_id.user_id, cursor)
            except:
                user_who_buy = chek_user(1045489755,cursor)
                
            if user_who_buy == None:
                await event.respond('У вас нет жабы, создайте ее')

            if user_who_buy and user_who_take != None:

                text = event.original_update.message.message
                
                cursor.execute('SELECT * FROM tovars')
                tovar = cursor.fetchall()
                
                for i in tovar:
                    if text.find(i[4]) > -1:                    
                        if user_who_buy[3] - i[2] >= 0:
                            cursor.execute("UPDATE zaba SET frogecoins = frogecoins - ? WHERE id_u= ?",(i[2],user_who_buy[0]))
                            connect.commit()
                            cursor.execute('UPDATE inventory SET kolvo = kolvo + 1 WHERE id_u= ? AND id_t= ?',(user_who_take[0],i[0]))
                            connect.commit()
                            await event.respond('Отправлено вашему другу')
                        else:
                            await event.respond('У вас недостаточно монет')
            
        
client.start()
client.run_until_disconnected()

'''
\U0001f37a - beer

\U0001f376 - sake

\U0001f377 - wine

\U0001f943 - wiski

\U0001f379 - cocktail

\U0001f375 - green_tea
'''

'''
\U0001f37a
\U0001f376
\U0001f377
\U0001f943
\U0001f379
\U0001f375
'''

#update zaba set current_energy = current_energy + (select buff_energy from tovars where id_t = 'beer') where id_u = 1045489755;
#text = event.message.message.encode('unicode_escape').decode('utf-8')      
#await event.respond('\U0001f44e')
