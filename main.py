import discord
import os
import random
import requests
import json
from pprint import pprint
from mojang import API
from keep_alive import keep_alive
import datetime
import time
import asyncio

intents = discord.Intents.default()
intents.message_content = True

api = API()

accessKey = os.environ['apiKey']

client = discord.Client(intents=intents)
version = "beta 1.3"

skillList = [
  "combat", "mining", "alchemy", "farming", "taming", "enchanting", "foraging",
  "fishing", "carpentry"
]
players = ["darksoul_", "spluxify", "severedpanda", "kingofthewinds"]
profileNo = [0, 1, 1, 2]


def get_uuid(username):
  uuid = api.get_uuid(username)
  #pprint(uuid)
  return uuid


def get_bedwars_data(uuid):

  requestLink = str("https://api.hypixel.net/player?key=" + accessKey +
                    "&uuid=" + uuid)
  info = []
  data = requests.get(requestLink).json()
  info.append(data["player"]["achievements"]["bedwars_wins"])
  info.append(data["player"]["achievements"]["bedwars_beds"])
  info.append(data["player"]["achievements"]["bedwars_level"])

  #response = requests.get("https://api.hypixel.net/player")
  #json_data = json.loads(response.text)
  #data = json_data[0]['rank']
  return info


def get_skywars_data(uuid):
  requestLink = str("https://api.hypixel.net/player?key=" + accessKey +
                    "&uuid=" + uuid)
  info = []
  data = requests.get(requestLink).json()
  info.append(data["player"]["achievements"]["skywars_kills_solo"])
  info.append(data["player"]["achievements"]["skywars_wins_solo"])
  info.append(data["player"]["achievements"]["skywars_kills_team"])
  info.append(data["player"]["achievements"]["skywars_wins_team"])
  return info


def get_online_status(uuid):
  requestLink = str("https://api.hypixel.net/status?key=" + accessKey +
                    "&uuid=" + uuid)
  status = requests.get(requestLink).json()
  return status["session"]["online"]


def get_gamemode(uuid):
  requestLink = str("https://api.hypixel.net/status?key=" + accessKey +
                    "&uuid=" + uuid)
  status = requests.get(requestLink).json()
  return status["session"]["gameType"]


def get_mode_location(uuid):
  requestLink = str("https://api.hypixel.net/status?key=" + accessKey +
                    "&uuid=" + uuid)
  status = requests.get(requestLink).json()
  return status["session"]["mode"]


def get_skyblock_data(uuid):
  requestLink = str("https://api.hypixel.net/skyblock/profiles?key=" +
                    accessKey + "&uuid=" + uuid)
  data = requests.get(requestLink).json()
  pprint(data["profiles"])
  return "done"


def readSkillsData():
  file = open("skillsData.txt", "r")
  dataList = file.readlines()
  playerList = [[], [], [],[]]
  for i in range(0, len(dataList)):
    dataList[i] = dataList[i].replace("\n", "")
    index = dataList[i].find(":")
    username = dataList[i][0:index]
    skills = dataList[i][index + 1:]
    playerList[i].append(username)
    for j in range(0, 9):
      index = skills.find(" ")
      playerList[i].append(skills[0:index])
      skills = skills[index + 1:]
  file.close()
  return playerList


def writeSkillsData(info):
  file = open("skillsData.txt", "w")
  for x in range(0, len(info)):
    file.write(str(info[x][0]) + ":")
    for y in range(1, 10):
      file.write(str(info[x][y]) + " ")
    if (x != len(info) - 1):
      file.write("\n")
  file.close()


async def checkSkills(playerList):
  print("checking skills")

  for i in range(0, len(playerList)):
    uuid = get_uuid(playerList[i][0])
    print(playerList[i][0])
    requestLink = str("https://api.hypixel.net/skyblock/profiles?key=" +
                      accessKey + "&uuid=" + uuid)
    data = requests.get(requestLink).json()
    requestLink2 = str("https://api.hypixel.net/resources/skyblock/skills")
    skillValues = requests.get(requestLink2).json()
    profile = profileNo[i]
    #print(uuid)
    for j in range(1, 10):
      currentSkillType = skillList[j - 1]
      exp = data["profiles"][profile]["members"][uuid]["experience_skill_" +
                                                       currentSkillType]
      max = skillValues["collections"][currentSkillType.upper()]["maxLevel"]
      if (skillValues["collections"][currentSkillType.upper()]["levels"][
          max - 1]["totalExpRequired"] <= exp):
        ok = "done"
      elif (skillValues["collections"][currentSkillType.upper()]["levels"][int(
          playerList[i][j])]["totalExpRequired"] <= exp):
        channel = client.get_channel(int(os.environ['channelid']))
        await channel.send(playerList[i][0] + " has just leveled up " +
                           currentSkillType + " from level " +
                           playerList[i][j] + " to level " +
                           str(int(playerList[i][j]) + 1) + " GG!")
        playerList[i][j] = str(int(playerList[i][j]) + 1)
        writeSkillsData(playerList)


async def checkAuctions(playerList):
  print("checking auctions")

  for i in range(0, len(playerList)):
    uuid = get_uuid(playerList[i])
    
    requestLink = str("https://api.hypixel.net/skyblock/auction?key=" +
                      accessKey + "&player=" + uuid)
    data = requests.get(requestLink).json()
    #pprint(data["auctions"][len(data["auctions"])-1])

    if (len(data["auctions"]) > 0):
      counter = 1
      auctionTime = data["auctions"][len(data["auctions"]) - counter]["start"]
      currentAdjustedTime = (
        datetime.datetime.timestamp(datetime.datetime.now()) * 1000) - 91000
      

      while (currentAdjustedTime < auctionTime):
        cost = data["auctions"][len(data["auctions"]) -
                                counter]["starting_bid"]
        cost = str('{:,}'.format(cost))
        auctionName = data["auctions"][len(data["auctions"]) -
                                       counter]["item_name"]
        pprint(auctionName)

        channel = client.get_channel(int(os.environ['channelid']))
        if ("bin" in data["auctions"][len(data["auctions"]) - counter]):
          await channel.send(playerList[i] +
                             " has just started a BIN auction for " +
                             auctionName + " costing " + cost + " coins!")
        else:
          await channel.send(playerList[i] +
                             " has just started an auction for " +
                             auctionName + " starting at " + cost + " coins!")

        if (len(data["auctions"]) > counter):
          counter = counter + 1
          auctionTime = data["auctions"][len(data["auctions"]) -
                                         counter]["start"]
          currentAdjustedTime = (datetime.datetime.timestamp(
            datetime.datetime.now()) * 1000) - 91000
        else:
          break

  
  await checkSkills(readSkillsData())
  await asyncio.sleep(90)
  await checkAuctions(playerList)


@client.event
async def on_ready():
  print("{0.user} is connected".format(client))
  channel = client.get_channel(793112204366577667)
  await channel.send("bot is up")
  await checkAuctions(players)


@client.event
async def on_message(input):

  if (input.author == client.user):
    return
  if (input.content.startswith("*hello")):
    await input.channel.send("whats up monkey")
  if (input.content.startswith("*help")):
    await input.channel.send("i cannot offer u mental help")
  if (input.content.startswith("*commands")):
    await input.channel.send(
      "*hello: say hi to the bot\n"
      "*help: if u seek help, type this in\n"
      "*version: check the current version of the bot\n"
      "*bedwars [playerName]: gives basic bedwars stats\n"
      "*skywars [playerName]: gives basic skywars stats\n"
      "*online [playerName]: tells you if this player is online and what mode they are playing"
    )

  if (input.content.startswith("*version")):
    await input.channel.send("current version: " + version)
  if (input.content.startswith("*bedwars")):
    uuid = get_uuid(str(input.content)[9:])
    info = get_bedwars_data(uuid)
    await input.channel.send("you have " + str(info[0]) + " bedwars wins\n"
                             "you have broken " + str(info[1]) +
                             " beds in bedwars\n"
                             "your current bedwars level is " + str(info[2]))
  if (input.content.startswith("*skywars")):
    uuid = get_uuid(str(input.content[9:]))
    info = get_skywars_data(str(uuid))
    await input.channel.send("you have " + str(info[1]) +
                             " solo skywars wins\n"
                             "you have " + str(info[0]) +
                             " solo skywars kills\n"
                             "you have " + str(info[3]) +
                             " team skywars wins\n"
                             "you have " + str(info[2]) +
                             " team skywars kills")
  if (input.content.startswith("*online")):
    uuid = get_uuid(str(input.content[8:]))
    print(uuid)
    status = get_online_status(str(uuid))
    if (status == True):
      gameMode = get_gamemode(str(uuid))
      if (gameMode != ""):
        location = get_mode_location(str(uuid))
        await input.channel.send("this person is currently online playing " +
                                 gameMode + " and is in the mode " + location)
      else:
        await input.channel.send("this person is currently online playing " +
                                 gameMode)
    else:
      await input.channel.send("this person isn't online")


keep_alive()

accessCode = os.environ['Token']
client.run(accessCode)
