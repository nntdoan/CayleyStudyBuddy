from botutils import parse_a_post, render_tex
from dotenv import load_dotenv
import subprocess as sp
import asyncio
import random
import glob
import json
import os

from discord import File
from discord.ext import commands
from discord.utils import get

'''
Created on Nov 20 by nntdoan
Resources that have helped me start: 
... https://realpython.com/how-to-make-a-discord-bot-python/
'''

# replace the path with the path to your .env file
load_dotenv(dotenv_path="../.env")
TOKEN = os.getenv('DISCORD_TOKEN')


bot = commands.Bot(command_prefix='.c.')



@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print( f'{bot.user.name} is connected to the following guild(s):\n'+
        '\n'.join([f'{c.name} (id: {c.id})' for c in bot.guilds]) )



@bot.command(name='q', help='Command Cayley to ask you a question.')
async def ask_question(ctx, _topic: str):
    questions = glob.glob(f"./data/*_{_topic}.json")[0]
    with open(questions) as f:
        picked = random.choice(json.load(f))
    to_ask, to_answer = parse_a_post(picked['link'], picked['accepted_answer_id'])
    notice="Here a question about "
    for t in picked['tags']:
        notice+= t+", " 
    notice+="wanna hear more? Gimme a :thumbsup:"
    pre_ask = await ctx.send(notice)
    await pre_ask.add_reaction('👍') 

    # Home-made Latex; render early so the user doesn't have to wait for too long
    render_tex('Question :'+to_ask)

    def check(reaction, user):
        return (not user.bot) and (str(reaction.emoji) == '👍') 

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        # delete pre_ask
        await pre_ask.delete()
    else:
        await pre_ask.delete()
        # Send the rendered picture to the channel
        notice = "\nGimme another :thumbsup: when you're ready for an answer. I'll let you know anyway after 10min max"
        await ctx.send(notice)
        asked = await ctx.send(file=File('tex/temp.png'))
        await asked.add_reaction('👍') 

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=600.0, check=check)
        except asyncio.TimeoutError:
            render_tex(to_answer)
            await ctx.send(file=File('tex/temp.png'))
            await ctx.send('More can be found here: <'+picked['link']+'>')
        else:
            render_tex(to_answer)
            await ctx.send(file=File('tex/temp.png'))
            await ctx.send('More can be found here: <'+picked['link']+'>')




# @bot.command(name='config', help='Config your Cayley.')
# @commands.has_role('admin')
# async def roll(ctx, nQuestion: int, frequency: int, time: int):  
#     # to-implement!!!
#     await ctx.send("I'll behave as you wish, my child!")


# @bot.event
# async def on_message(message):
#     # to-implement:run sentiment analysis on randomly selected message in a channel
#     # the bot add emoji to itself
#     if message.author == bot.user:
#         if ':EmojiName:' in message.content:
#             emoji = get(bot.get_all_emojis(), name='EmojiName')
#             await message.add_reaction(emoji)



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')



@bot.event
async def on_error(event, *args, **kwargs):
    with open('error.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

        
bot.run(TOKEN)