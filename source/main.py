import os, random, datetime, time, config, PIL, mc, requests, json, psutil, platform, dog, subprocess, cpuinfo, re, wikipedia, math, sqlite3 as sql
from local import *
from config import *
from vkbottle.bot import Bot, Message
from vkbottle import VideoUploader, Keyboard, KeyboardButtonColor, Text, OpenLink, VoiceMessageUploader, PhotoMessageUploader
from vkbottle.dispatch.rules.base import AttachmentTypeRule, ChatActionRule, FromUserRule
from bs4 import BeautifulSoup
from loguru import *
from requests import get
from PIL import Image, ImageDraw, ImageFont
from mc.builtin import validators
from sys import version
from gtts import gTTS
from wand.image import Image
from wand.display import display
from wand.font import Font
from simpledemotivators import *
from requests import get

bot=Bot(config.token)

def read_ff(file): # Read From File
    try:
        Ff = open(file, 'r', encoding='UTF-8')
        Contents = Ff.read()
        Ff.close()
        return Contents
    except:
        return None
        
logger.info(read_ff("Assets/hello.txt") + botver + '\n') 

logger.info('Initialization...')

connection = sql.connect("playerdata.db", check_same_thread=False)  # Database connection
q = connection.cursor()
q.execute('CREATE TABLE IF NOT EXISTS players (id INTEGER DEFAULT NULL, status INTEGER DEFAULT 0, kolvo INTEGER DEFAULT 0, picgen INTEGER DEFAULT 3, txtgen INTEGER DEFAULT 25, dst STRING DEFAULT 0, rnd INTEGER DEFAULT 3, learn INTEGER DEFAULT 0, arrange INTEGER DEFAULT 0)')

logger.info('Loading files and directories...')
if not os.path.exists('Images'):
    os.mkdir('Images')

if not os.path.exists('Dialogs'):
    os.mkdir('Dialogs')

if not os.path.exists('modules'):
    os.mkdir('modules')

if not os.path.exists(config.lists_dir):
    os.mkdir(config.lists_dir)
        
for i in range(len(config.lists_files)):
    if not os.path.exists(config.lists_dir + config.lists_files[i]):
        f = open(config.lists_dir + config.lists_files[i], 'w', encoding='utf8')
        f.write('')
        f.close()

modules = os.listdir(config.modules_dir)
for i in range(len(modules)):
    if '.py' in modules[i]:
        logger.info('Starting module "' + modules[i] + '"...')
        exec(read_ff(config.modules_dir + modules[i]))
        
logger.info('One moment...')
logger.add(path_to_log, format='{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}', backtrace=False, encoding='utf-8')   
start_menu = Keyboard(inline=True)
start_menu.add(Text('Команды доступные в лс', {"cmd": "daemon_func"}))
start_menu.add(Text('Политика приватности', {"cmd": "daemon_policy"}))
start_time = time.time()

logger.success('Ready!')

# React to photo
@bot.on.chat_message(AttachmentTypeRule("photo"))
async def photoadd(ans: Message):
        await addtobd(ans.peer_id)
        photo = ans.attachments[0].photo.sizes[-1].url
        if ans.from_id > 0:
            f = open(dir_to_pic + str(ans.peer_id) + '.txt', 'r', encoding='utf8')
            l = f.read()
            f.close
            f = open(dir_to_pic + str(ans.peer_id) + '.txt', 'w', encoding='utf8')
            f.write(l + photo + '\n')
            f.close()       

# Reacts to any message in the conversation
@bot.on.chat_message()
async def allmsg(ans: Message):
    await addtobd(ans.peer_id)
    if await check_bl_wl(ans) != False:
        randomint = random.randint(1000, 10000000)
        if len(ans.text) <= 60 and ans.text != '' and ans.from_id > 0 and ans.text[:3] != '[id' and ans.text[:1] != '/': # Checking for a Valid Message
            # Opening the file, add the user's message if it matches.
            f = open(dir_to_txt + str(ans.peer_id) + '.txt', 'r', encoding='utf8')
            l = f.read()
            f.close()
            f = open(dir_to_txt + str(ans.peer_id) + '.txt', 'w', encoding='utf8')
            f.write(l + ans.text + '\n')
            f.close()
            # Updating the database, add the number of messages in the conversation database.
            q.execute(f"SELECT * FROM players WHERE id = {ans.peer_id}")
            result = q.fetchall()
            status = result[0][1]
            kolvo = result[0][2]
            picgen = result[0][3]
            txtgen = result[0][4]
            learn = result[0][7]
            q.execute(f"UPDATE players SET kolvo = '{kolvo + 1}' WHERE id = '{ans.peer_id}'")
            connection.commit()
            # Checking the number of lines in photo/text databases
            pic2 = 0
            with open(dir_to_pic + str(ans.peer_id) + '.txt', encoding='utf8') as f:
                for line in f:
                    pic2 = pic2 + 1
            lines = 0
            with open(dir_to_txt + str(ans.peer_id) + '.txt', encoding='utf8') as f:
                for line in f:
                    lines = lines + 1
            # If the lines of pictures / text and the number of messages in the sql database come down, then we generate           
            if lines >= txtgen and pic2 >= picgen and kolvo >=txtgen and learn != 1:
                if status == 0: # This is if mode 0 (standard)
                    # Choosing random text and photo
                    with open(dir_to_txt + str(ans.peer_id) + '.txt', encoding='utf8') as file:
                        content = file.read().splitlines()
                    generator = mc.PhraseGenerator(samples=content)
                    rndtxt = generator.generate_phrase(attempts=20, validators=[validators.words_count(minimal=1, maximal=5)])
                    rndtxt2 = generator.generate_phrase(attempts=20, validators=[validators.words_count(minimal=1, maximal=10)])
                    with open(dir_to_pic + str(ans.peer_id) + '.txt', encoding='utf8') as file:
                        content2 = file.read().splitlines()
                    rndpic = random.choice(content2)
                    p = requests.get(rndpic)
                    out = open(fr'randomimg_{randomint}.jpg', "wb")
                    out.write(p.content)
                    out.close()
                    # Seting the number of messages in the sql database to 0
                    q.execute(f"SELECT * FROM players WHERE id = {ans.peer_id}")
                    result = q.fetchall()
                    kolvo = result[0][2]
                    mode = result[0][5]
                    arrange = result[0][8]
                    q.execute(f"UPDATE players SET kolvo = '0' WHERE id = '{ans.peer_id}'")
                    connection.commit()
                    if mode == 1:
                        user_img = PIL.Image.open(f'randomimg_{randomint}.jpg').convert("RGBA")
                        (width, height) = user_img.size
                        image = Image(filename=f'randomimg_{randomint}.jpg')
                        with image.clone() as liquid:
                            liquid.liquid_rescale(width-350, height-350)
                            liquid.save(filename=f'randomimg_{randomint}.jpg')
                            liquid.size
                        user_img = PIL.Image.open(f'randomimg_{randomint}.jpg').resize((width, height))
                        user_img.save(f'randomimg_{randomint}.jpg')
                    if arrange == 1:
                        dem = Demotivator(rndtxt, rndtxt2)
                        dem.create(f'randomimg_{randomint}.jpg', watermark=watermarkwrong, result_filename=f'dem_{randomint}.jpg')
                    else:
                        dem =  Demotivator(rndtxt, rndtxt2)
                        dem.create(f'randomimg_{randomint}.jpg', watermark=watermarkwrong, result_filename=f'dem_{randomint}.jpg')
                    photo = await PhotoMessageUploader(bot.api).upload(f'dem_{randomint}.jpg')
                    await ans.answer(attachment=photo)
                    await logging(ans.peer_id)
                    os.remove(f'randomimg_{randomint}.jpg')
                    os.remove(f'dem_{randomint}.jpg')
        
                else:
                    with open(dir_to_txt + str(ans.peer_id) + '.txt', encoding='utf8') as file:
                        content = file.read().splitlines()
                    # Updating the base of the number of messages
                    q.execute(f"SELECT * FROM players WHERE id = {ans.peer_id}")
                    result = q.fetchall()
                    kolvo = result[0][2]
                    q.execute(f"UPDATE players SET kolvo = '0' WHERE id = '{ans.peer_id}'")
                    connection.commit()
                    # Selecting random text
                    rndtxt = random.choice(content)
                    content.remove(rndtxt)
                    rntxt = random.choice(content)
                    content.remove(rntxt)
                    rndtxt2 = rntxt.lower() + ' ' + random.choice(content).lower()
                    await logging(ans.peer_id)
                   # Here shitcode (We cut off the text, etc.), if not fixed sorry .-.
                    if len(rndtxt2) <= 60:
                        await ans.answer(rndtxt + ' ' + rndtxt2)
                    else:
                        rndtxt2 = rndtxt2[:60]
                        await ans.answer(rndtxt + ' ' + rndtxt2)

@bot.on.private_message(payload={"cmd": "daemon_func"})
async def func_info_msg(ans: Message):
    if await check_bl_wl(ans) != False:
        await ans.reply(func_info_ls)

@bot.on.private_message(payload={"cmd": "daemon_policy"})
async def privacy_policy(ans: Message):
    if await check_bl_wl(ans) != False:
        await ans.reply(privacy_policy_msg)     

@bot.on.private_message()
async def ls_msg(ans: Message):
    if await check_bl_wl(ans) != False:
        await ans.reply(hello_msg, keyboard=start_menu)

if __name__ == '__main__':    
    bot.run_forever()
