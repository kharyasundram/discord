import discord
import asyncio
import requests
import string
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error

TOKEN = "NzU0NjU0MDE0OTkzNDY1MzQ0.X134UQ.7v6WZE-RrCXkMdaZrf-Lmk-kgXk"
client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return    

    if message.content.startswith('!google'):
        try:
            result = await chatbot_query(message.content[8:])
        except Exception as e:
            result = ""
            print (e)
        msg = result
        await message.channel.send(msg)

    if message.content.startswith('!recent'):
        try:
            result = await chatbot_query_result(message.content[8:])
        except Exception as e:
            result = ""
            print (e)
        msg = result
        await message.channel.send(msg)
        # await client.send(message.channel, msg)

    if message.content.startswith('hi'):
        msg = 'hey'
        await message.channel.send(msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def chatbot_query(query, index=0):
    print ("query", query)
    fallback = 'Sorry, I cannot think of a reply for that.'
    result = ''
    result_list = []
    try:
        AddShowsearching(query, "Add")
    except Exception as e:
        print ("e", e)
    try:
        for j in search(query, tld="co.in", num=10, stop=10, pause=2): 
            result_list.append(j) 

        search_result_list = list(search(query, tld="co.in", num=10, stop=3, pause=1))
        # requests.packages.urllib3.disable_warnings()
        page = requests.get(search_result_list[index])

        tree = html.fromstring(page.content)

        soup = BeautifulSoup(page.content, features="lxml")

        article_text = ''
        article = soup.findAll('p')
        for element in article:
            article_text += '\n' + ''.join(element.findAll(text = True))
        article_text = article_text.replace('\n', '')
        first_sentence = article_text.split('.')
        first_sentence = first_sentence[0].split('?')[0]

        chars_without_whitespace = first_sentence.translate(
            { ord(c): None for c in string.whitespace }
        )

        if len(chars_without_whitespace) > 0:
            result = first_sentence
        else:
            result = fallback
        result_list.append(result)
        return result_list
    except:
        if len(result) == 0: result = fallback
        return result

@client.event
async def chatbot_query_result(query, index=0):
    fallback = 'Sorry, There have no match for recent search'
    result = ''
    result_list = []
    try:
        status, result, msg = AddShowsearching(query, "result")
        if status==200:
            if len(result)<1:
                return fallback
            return result
    except Exception as e:
        print ("e", e)
        return fallback

def AddShowsearching(query, method_type):
    try:
        connection = mysql.connector.connect(host='localhost',database='chatbot',user='root',password='')
        if connection.is_connected():
            db_Info = connection.get_server_info()
            cursor = connection.cursor()
            if method_type == "Add":
                query = [str(query)]
                sql = """INSERT INTO Searchhistory (discription) VALUES (%s)"""
                result = cursor.execute(sql, query)
                connection.commit()
                status, result, msg = 200, None, "Success"
                return status, result, msg
            elif method_type == "result":
                query = "%"+query+"%"
                sql = """select discription from Searchhistory where discription like "%s";"""%(query)
                result = cursor.execute(sql)
                data = []
                records = cursor.fetchall()
                for row in records:
                    data.append(row[0])
                status, result, msg = 200, data, "Success"
                return status, result, msg
            else:
                status, result, msg = 400, None, e
                return status, result, msg
    except Error as e:
        status, result, msg = 400, None, e
        return status, result, msg
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
    

client.run(TOKEN)
