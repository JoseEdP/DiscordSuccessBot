# This  requires the 'members' privileged intents

import os
import discord
from discord.ext import commands
import random
import sqlite3
from sqlite3 import Error
import requests
import tweepy


description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
image_types = ["png", "jpeg", "jpg"]
#picPurify API Key
picPurify_API= ""
#replace with admin discord id
discordAdmin = 123456789

bot = commands.Bot(command_prefix='!', description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    database = r"users.db"
    # create a database connection
    global conn
    conn = create_connection(database)
    print("DB Connected")


@bot.event
async def on_reaction_add(reaction, user):
    print(reaction.message.author)
    if reaction.message.author.id != discordAdmin:
        print("Bad author")
        return
    else:
        #replace id with channel id
        if reaction.message.channel.id != 1234567879:
            print("wrong channel")
            return
        if reaction.emoji == "👍":
            print("Emoji found")
            channel = reaction.message.channel
            attachm = reaction.message.attachments[0].url
            request = requests.get(attachm, stream=True)
            if attachm.endswith("png"):
                filename = 'temp.png'
            elif attachm.endswith("jpg"):
                filename = 'tempy.jpg'
            elif attachm.endswith("jpeg"):
                filename = 'temp.jpeg'
            else:
                return
            if request.status_code == 200:
                with open(filename, 'wb') as image:
                    for chunk in request:
                        image.write(chunk)
                tweet_image("From our Discord! Link in bio.", filename)
                os.remove(filename)
            else:
                print("bad request")


        else:
            print("wrong emoji")



@bot.event
async def on_message( message: discord.Message,):
    #replace channel id
    if message.channel.id == 123456789:
        id = message.author.id
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(image) for image in image_types):
                if attachment.filename.lower().endswith("png"):
                    await attachment.save("temp.png")
                    ext = "png"
                if attachment.filename.lower().endswith("jpg"):
                    await attachment.save("temp.jpg")
                    ext = "jpg"
                if attachment.filename.lower().endswith("jpeg"):
                    await attachment.save("temp.jpeg")
                    ext = "jpeg"
                ff = open("temp." + ext, 'rb')
                f = {'file_image':ff}
                if image_check(f) == True:
                    if check_image(conn, attachment.filename.lower()) == False:
                        insert_image(conn, (attachment.filename.lower()))
                        with conn:
                            # create a new project
                            checks = check_user(conn, id)
                            if checks == True:
                                current_points = get_points(conn, id)
                                update_points(conn, (current_points, id))
                                await message.channel.send("Thanks for sharing <@" + str(id) + ">! You now have "+ str(get_points(conn, id)) + " points.")
                            else:
                                project = (id, '1',);
                                project_id = create_project(conn, project)
                                await message.channel.send("Welcome <@" + str(id) + ">! To start you have "+ str(get_points(conn, id)) + " points.")
                    else:
                        await message.delete()
                        await message.channel.send(" <@" + str(id) + ">, this image has already beeen sent.")
                else:
                    await message.delete()
            else:
                await message.delete()
                await message.channel.send(" <@" + str(id) + ">, please only send images.")
            try:
                ff.close()
                os.remove("temp." + ext)
            except:
                continue
    else:
        print("bad channel")
    
    await bot.process_commands(message)



@bot.command()
async def balance(ctx):
    #replace channel id
    if ctx.channel.id == 123456789:
        id = ctx.author.id
        checks = check_user(conn, id)
        if checks == True:
            u_p = get_points(conn, ctx.author.id)
            await ctx.channel.send("<@" + str(ctx.author.id) + "> has " + str(u_p) + " points.")
        else:
            await ctx.channel.send("<@" + str(ctx.author.id) + "> does not have any points.")


@bot.command()
async def rmpoints(ctx, points: int, id: int):
    #replace discord id
    if ctx.author.id == 123456789:
        if check_user(conn, id) == True:
            current_points = get_points(conn, id)
            remove_points(conn, (current_points, points, id))
            await ctx.channel.send("<@" + str(id) + "> now has " + str(get_points(conn, id)))
        else:
            await ctx.channel.send("User does not exist.")
    else:
        print("Not allowed.")




def remove_points(conn, task):
    sql = ''' UPDATE projects
              SET points = ? - ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_project(conn, project):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO projects(id,points)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid

def insert_image(conn, task):
    sql = ''' INSERT INTO images(file_name)
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, [task])
    conn.commit()
    return cur.lastrowid

def check_user(conn, id):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    temp = ("SELECT * FROM projects WHERE id LIKE '%" + str(id) + "%';")
    cur.execute(temp)

    rows = cur.fetchone()
    if rows is not None:
        return True
    else:
        return False

def check_image(conn, task):
    cur = conn.cursor()
    temp = ("SELECT * FROM images WHERE file_name LIKE '%" + task + "%';")
    cur.execute(temp)

    rows = cur.fetchone()
    if rows is not None:
        return True
    else:
        return False

def get_points(conn, id):
    cur = conn.cursor()
    temp = ("SELECT * FROM projects WHERE id LIKE '%" + str(id) + "%';")
    cur.execute(temp)

    rows = cur.fetchone()
    return(rows[1])


        
def update_points(conn, task):
    #pointss += 1
    sql = ''' UPDATE projects
              SET points = ? + 1
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()


def image_check(image):
    r = requests.post("https://www.picpurify.com/analyse/1.1", files = image, data = {"API_KEY":picPurify_API, "task":"porn_moderation,drug_moderation,gore_moderation"})
    results =  r.json()
    if results["status"] == "success":
        if results["final_decision"] != "OK":
            return False
        else:
            return True
    else:
        return False

        
def twitter_api():
    #replace tweepy values
    auth = tweepy.OAuthHandler("123456789", "123456789")
    auth.set_access_token("123456789", "123456789")

    api = tweepy.API(auth)
    return api


def tweet_image(message, file):
    api = twitter_api()
    filename = file
    with open(filename, 'rb') as image:
        api.update_with_media(filename, status=message)
    


#replace with discord token
bot.run('123456789')

