from multiprocessing.dummy.connection import families
from faunadb.errors import ErrorData
import pygame
import sys
import time
import random
import pickle
import os

pygame.init()

import urllib.request

#image
def_powerup = pygame.transform.scale(
    pygame.image.load(r'images\powerups\Default.PNG'),
    (70, int(70 * 149 / 129)))


def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        # print('Internet is on')
        return True
    except:
        return False


internet = connect()

if internet:
    import operator
    from typing import final
    from faunadb import query as q
    from faunadb.objects import Ref
    from faunadb.client import FaunaClient
    import re

    client = FaunaClient(
        secret="fnAEalXja4AAScBNFQW0lxRWEg-VZEhs-thXkrb6",
        # secret = "fnAEcMKAPvAAR5LqwD05oCTtvuIWTdsSHyuOu7AE",
        domain="db.us.fauna.com",
        # NOTE: Use the correct domain for your database's Region Group.
        port=443,
        scheme="https")

ndataset = 10


def sortedLeaderboardList(index, collection):
    indexes = client.query(q.paginate(q.match(q.index(index))))

    data = [indexes['data']]  # list of ref ids
    # print(indexes['data'])

    result = re.findall('\d+',
                        str(data))  # to find all the numbers in the list
    # print(result)

    fData = []

    for i in result:
        user_details = client.query(q.get(q.ref(q.collection(collection), i)))
        details = user_details['data']
        # print(details)
        tempData = [
            details['name'], details['score'], details['time'],
            1 / float(details['time']),
            int(user_details['ref'].id())
        ]
        # print(tempData)
        fData.append(tempData)

    finalData = sorted(fData, key=operator.itemgetter(1, 3), reverse=True)
    # print(finalData)

    return finalData


def pushDictData(collection, data):
    client.query(q.create(q.collection(collection), {'data': data}))


def countDocs(collection):
    count = client.query(q.count(q.documents(q.collection(collection))))

    return count


def deleteDoc(collection, refid):
    client.query(q.delete(q.ref(q.collection(collection), refid)))


def sameScoreTimes(data, score):
    lTimes = []

    for i in data:
        if i[1] == score:
            lTimes.append(i[2])

    return lTimes

def writeBigGame(bigGame):
    bigData = {'bigGame':bigGame}
    with open('bigGame.dat', 'wb') as file:
        pickle.dump(bigData, file)

def bigGameVar():
    global data, sortedData
    names = []
    for i in sortedData:
        names.append(i[0])

    if os.path.exists("bigGame.dat"):
        print('file exists')
        with open('bigGame.dat', 'rb') as file:
            bigData = pickle.load(file)
        bigGame = bigData['bigGame']
        print(f"In file, bigGame: {bigGame}")
    
    if data['name'] not in names:
        bigGame = False
        print('Name not on leaderboard, bigGame: False')
    elif not(os.path.exists("bigGame.dat")):
        bigGame = False

    writeBigGame(bigGame)
    return bigGame

def pushData(name, score, time, bigGame):

    sortedData1 = sortedLeaderboardList(index='testindex',
                                        collection='testcollection')

    # for i in sortedData1:
    #     print(i)

    lScores = []
    lnames = []

    for i in sortedData1:
        lScores.append(i[1])
        lnames.append(i[0])

    # print(lScores)

    count = countDocs(collection='testcollection')

    dataDict = {'name': name, 'score': score, 'time': time}

    sending = False

    lTimes = sameScoreTimes(data=sortedData1, score=min(lScores))

    if count < ndataset:
        sending = True
    elif score > min(lScores):
        sending = True
        if lScores.count(min(lScores)) == 1:
            for i in sortedData1:
                if i[1] == min(lScores):
                    deleteDoc(collection='testcollection', refid=i[4])
    elif score == min(lScores):
        if time < max(lTimes):
            sending = True
            for i in sortedData1:
                if i[2] == max(lTimes):
                    deleteDoc(collection='testcollection', refid=i[4])

    if (sending):
        if (bigGame):
            for i in sortedData1:
                if name == i[0]:
                    deleteDoc(collection='testcollection', refid=i[4])
                    pushDictData(collection='testcollection', data=dataDict)
                    print("Data sent successfully!")
                    writeBigGame(True)
        else:
            if name in lnames:
                print(
                    'A player already thrives on the leaderboard with this name. Kindly enter the new name.'
                )
                changeName()
                # send data with changed name
                pass
                writeBigGame(True)
            else:
                pushDictData(collection='testcollection', data=dataDict)
                print("Data sent successfully!")
                writeBigGame(True)
    else:
        print("Data not sent since conditions are not met")

# pulling data
def pullingSortedData():
    try:
        data = sortedLeaderboardList(index='testindex',
                                     collection='testcollection')
        file = open("sortedData.dat", "wb")
        pickle.dump(data, file)
        file.close()
        print('data pulled')
        return data
    except:
        try:
            file = open("sortedData.dat", "rb")
            data = pickle.load(file)
            print('data taken from file')
            file.close()
            return data
        except:
            data = []
            print('data can\'t be pulled and file is empty or non-existent')
            return data


def saveGameDataForLater(name, score, time):
    try:
        fileR = open('savedData.dat', "rb")
        data = pickle.load(fileR)
        if data['score'] < score:
            fileW = open('savedData.dat', 'wb')
            pickle.dump(data, fileW)
        elif data['score'] == score:
            if data['time'] > time:
                fileW = open('savedData.dat', 'wb')
                pickle.dump(data, fileW)
        fileR.close()
    except:
        file = open('savedData.dat', 'wb')
        data = {'name': name, 'score': score, 'time': time}
        pickle.dump(data, file)
        file.close()


sortedData = pullingSortedData()


if internet and os.path.exists("savedData.dat"):
    try:
        fileR = open('savedData.dat',"rb")
        data = pickle.load(fileR)
        bigGame = bigGameVar()
        pushData(name = data['name'], score = data['score'], time = data['time'], bigGame = bigGame)
        fileR.close()
        os.remove("savedData.dat")
        print('Saved data from previous games sent')
    except:
        print("Saved data from previous games couldn't be sent due to an unexpected error")

# line pygame.draw.line(SCREEN, BLUE, (100,200), (300,450),5) #screen, color, starting point, ending point, width
# rect pygame.draw.rect(SCREEN, BLUE, (390,390,50,25)) #screen, color, (starting_x, starting_y, width,height)
# circle pygame.draw.circle(SCREEN, BLUE, (150,150), 75) #screen, color, (center_x, center_y), radius)
# polygon pygame.draw.polygon(SCREEN, BLUE, ((25,75),(76,125),(250,375),(390,25),(60,540))) #screen, color, (coordinates of polygon(consecutive))
# image pygame.image.load("space-invaders.png")


def changeName():
    pass



#constants
LENGTH = 454
PIXEL = 15
SCREEN = pygame.display.set_mode((LENGTH + 100, LENGTH), pygame.RESIZABLE)

CLOCK = pygame.time.Clock()
rate = 8
coin_2, point_2 = False, False
#colours
LIGHTBROWN = '#AD9157'
DARKBROWN = '#4F3119'
BLACKBROWN = '#11110F'
BLACK = (0, 0, 0)
GREY = (50, 50, 50)
RED = (255, 0, 0)
ORANGE = (255, 120, 0)
VOILET = (100, 0, 100)
PINK = (255, 0, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 255, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
A = "".join([chr(x) for x in range(65, 91)])
ALPHA = A + A.lower() + '_' + ''.join([str(x) for x in range(10)])

#[[name,score,timeplayed,1_time,ref_id]]


#user data
def newUser_init():
    global Cursor, Text_Val, iterrr
    iterrr = 0
    Cursor = False
    Text_Val = ''


try:
    file = open('userData.dat', 'rb')
    data = pickle.load(file)
    non_cheater = True
except pickle.UnpicklingError:
    user = 'Cheater'
    non_cheater = False
if non_cheater:
    if data['name'] == '' or data['name'] == None:
        user = 'NewUser'
        print('Redirecting to New User')
        newUser_init()
    else:
        user = 'Home'
    file.close()


def show(msg, color, x, y, size):
    score_show = pygame.font.Font("freesansbold.ttf",
                                  size).render(msg, True, color)
    SCREEN.blit(score_show, (x, y))


selected_items = [False, False, False, False, False, False]

I = 0
iterr = 0


def update_data():
    with open('userData.dat', 'wb') as file:
        pickle.dump(data, file)


def button(text,
           x,
           y,
           width,
           height,
           bg_color=WHITE,
           x_offset=10,
           text_size=10,
           text_col=BLACK,
           hover_col=BLUE,
           hover_width=2):
    global event_list
    pos = pygame.mouse.get_pos()
    if pos[0] >= x and pos[0] <= x + width and pos[1] >= y and pos[
            1] <= y + height:
        pygame.draw.rect(SCREEN, hover_col,
                         (x - hover_width, y - hover_width,
                          width + hover_width * 2, height + hover_width * 2))
        if pygame.mouse.get_pressed()[0]:
            return True
    pygame.draw.rect(SCREEN, bg_color, (x, y, width, height))
    show(text, text_col, x + x_offset,
         (y + (height - text_size) // 2 if height > text_size else height),
         text_size)


def screen_animation(decreaser=False, r=25, color=BLACK, timer=0.01):
    global I, iterr

    if iterr == 0:
        I = r if decreaser else 0
        stopper = False
    stopper = True if I > r else (True if I < 0 else False)
    if stopper:
        iterr = 0
        return True
    s = pygame.Surface((LENGTH, LENGTH))
    s.set_alpha((I * 255 // r + 255 % r))
    I -= 1 if decreaser else -1
    iterr += 1
    time.sleep(timer)
    s.fill(color)
    SCREEN.blit(s, (0, 0))
    return False


def home_params():
    pass
    # global i, decreaser, done
    # i = 0
    # done = False
    # decreaser = False


breaker = False


def home():
    SCREEN.fill(BLACK)
    global i, decreaser, done, user, start, breaker
    show('home', WHITE, 0, 0, 32)
    show(data['name'], WHITE, 350, 0, 16)
    # show(data['coin'], WHITE, 450, 0, 16)
    newUser = button('NewUser', 200, 250, 100, 30)
    if newUser:
        newUser_init()
        user = 'NewUser'
    user = 'Arsenal' if button('Play Game', 200, 200, 100, 30) else user
    user = 'LeaderBoard' if button('LeaderBoard', 200, 300, 100, 30) else user
    user = 'Missions' if button('Missions', 200, 350, 100, 30) else user
    user = 'MarketPlace' if button('Shop', 200, 400, 100, 30) else user
    user = 'Inventory' if button('Inventory', 400, 400, 100, 30) else user
    n = button('N', 400, 250, 100, 30)
    if n:
        breaker = True
    # if not done:
    #     d = screen_animation()
    #     done = d
    # if done:
    #     d = screen_animation(True)
    #     done = not d


def arsenal():
    global user, start, SCREEN, selected_items
    LENGTH = pygame.display.get_surface().get_width()
    # LENGTH = 554
    # SCREEN = pygame.display.set_mode((LENGTH, 454))
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('Your Arsenel for the game', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    with open('items.dat', 'rb') as file:
        list_items = pickle.load(file)

        mul = (LENGTH - 30) // 3
        for i, item in enumerate(list_items['Powerups'].items()):
            if i <= 2:
                global event_list
                pos = pygame.mouse.get_pos()
                x, y, width, height = (20 + i * mul, 70, mul - 20, 135)
                pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                pygame.draw.rect(SCREEN, LIGHTBROWN,
                                 (x + 5, y + 5, width - 10, height - 10))
                SCREEN.blit(def_powerup, (60 + i * mul, 80))
                if i == 1:
                    show(item[0], BLACK, 30 + i * mul, 165, 14)
                    show(f'{item[1][0]} in stock', WHITE, 30 + i * mul, 185,
                         12)
                else:
                    show(item[0], BLACK, (65 if i == 2 else 35) + i * mul, 165,
                         16)
                    show(f'{item[1][0]} in stock', WHITE, 30 + i * mul, 185,
                         12)
                s = pygame.Surface((width, height))
                s.set_colorkey(GREY)
                s.set_alpha(0)
                if pos[0] >= x and pos[0] <= x + width and pos[1] >= y and pos[
                        1] <= y + height and item[1][0] != '0':
                    if pygame.mouse.get_pressed()[0]:
                        with open('items.dat', 'wb') as f:
                            list_items['Powerups'][item[0]] = (str(
                                int(item[1][0]) +
                                (1 if selected_items[i] else -1)), item[1])
                            pickle.dump(list_items, f)
                        selected_items[i] = not selected_items[i]
                    s.set_alpha(60)
                if selected_items[i]:
                    s.set_alpha(120)
                SCREEN.blit(s, (x, y))

            elif i <= 5:
                x, y, width, height = (20 + (i - 3) * mul, 230, mul - 20, 135)
                pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                pygame.draw.rect(SCREEN, LIGHTBROWN,
                                 (x + 5, y + 5, width - 10, height - 10))
                SCREEN.blit(def_powerup, (60 + (i - 3) * mul, 240))
                show(item[0], BLACK, (45 if i == 4 else 65) + (i - 3) * mul,
                     325, 16)
                show(f'{item[1][0]} in stock', WHITE, 30 + (i - 3) * mul, 345,
                     12)
                s = pygame.Surface((width, height))
                pos = pygame.mouse.get_pos()
                s.set_colorkey(GREY)
                s.set_alpha(0)
                if pos[0] >= x and pos[0] <= x + width and pos[1] >= y and pos[
                        1] <= y + height and item[1][0] != '0':
                    if pygame.mouse.get_pressed()[0]:
                        with open('items.dat', 'wb') as f:
                            list_items['Powerups'][item[0]] = int(
                                item[1][0]) + (1 if selected_items[i] else -1)
                            pickle.dump(list_items, f)
                        selected_items[i] = not selected_items[i]
                    s.set_alpha(60)
                if selected_items[i]:
                    s.set_alpha(120)
                SCREEN.blit(s, (x, y))
    show('2x Coins :' + ('Activated' if coin_2 else 'Not Activated'), WHITE,
         25, 375, 18)
    show('2x Points :' + ('Activated' if point_2 else 'Not Activated'), WHITE,
         305, 375, 18)
    user = 'Emulator' if button('Start Game',
                                LENGTH // 2 - 55,
                                410,
                                110,
                                32,
                                DARKBROWN,
                                text_col=WHITE,
                                text_size=16,
                                hover_width=0) else user
    user = 'Home' if button('Home', LENGTH - 70, 10, 100, 30) else user
    if user == 'Emulator':
        emulator_params()


def emulator_params():
    global Blocks, snake, direction, body, Apple, random_cord, Bomb, SpeedUp, SpeedDown, counter, rnt, score, ee_dec, ee_done, realm
    global Theme, blocks, LENGTH, rate, start, SCREEN, popup, applex, appley
    LENGTH = 454
    rate = 4 if selected_items[3] else (12 if selected_items[2] else 8)
    Theme = [
        LIGHTBROWN, (210, 190, 210), RED, YELLOW, GREY, GREEN, BLUE, WHITE,
        DARKBROWN
    ]
    # bg_color, bomb_col, snake_col, apple_col, empty_col, sup_col, sdown_col, text_col, text_bg
    score = 0
    realm = False
    rnt = [0, 0, 0]
    ee_dec = False
    popup = False
    ee_done = False
    counter = [0, 0, 0]  #bomb,speedup,speeddown
    Apple = True
    Bomb, SpeedUp, SpeedDown = False, False, False
    snake = [LENGTH // 2, LENGTH // 2]
    direction = 'up'
    body = [(LENGTH // 2, LENGTH // 2 + PIXEL),
            (LENGTH // 2, LENGTH // 2 + 2 * PIXEL)]

    class Blocks:
        def __init__(self, x, y, block_type=None) -> None:
            self.x = x
            self.y = y
            self.block_type = block_type
            self.color = Theme[4]

        def draw(self):
            if self.block_type == "snake" or self.block_type == "head":
                self.color = Theme[2]
            elif self.block_type == None:
                self.color = Theme[4]
            elif self.block_type == 'apple':
                self.color = Theme[3]
            elif self.block_type == 'bomb':
                self.color = Theme[1]
            elif self.block_type == 'speedup':
                self.color = Theme[5]
            elif self.block_type == 'speeddown':
                self.color = Theme[6]
            pygame.draw.rect(SCREEN, self.color,
                             (self.x + 1, self.y + 1, PIXEL - 2, PIXEL - 2))

    blocks = []

    #Spawner Function
    def random_cord(lis):
        b = random.choice(list(filter(lambda x: x.block_type == None, lis)))
        return (b.x, b.y)

    #Main Block loop
    for x in range(0, (LENGTH // PIXEL)):
        X = 2 + x * PIXEL
        for y in range(0, (LENGTH // PIXEL) - 2):
            Y = 2 + (y + 2) * PIXEL
            block = Blocks(X, Y)
            blocks.append(block)
    SCREEN = pygame.display.set_mode((LENGTH, LENGTH))
    start = time.time()
    applex, appley = random_cord(blocks)


def emulator():
    global direction, Apple, Bomb, SpeedUp, SpeedDown, counter, rnt, Theme, event_list, realm, t0, start, selected_items, blocks, popup, coin_2, point_2
    global applex, appley, bombx, bomby, speedupx, speedupy, speeddownx, speeddowny, score, rate, ee_dec, ee_done, user, data, coins, t, SCREEN
    gameover = False
    SCREEN.fill(Theme[0])
    pygame.draw.rect(SCREEN, BLACK, (2, 32, LENGTH - 4, LENGTH - 35))

    body.insert(0, tuple(snake))
    body.pop(-1)
    if not popup:
        #Bomb
        if counter[0] == 0:
            bombx, bomby = -1, -1
            rnt[0] = random.randint((150 if selected_items[4] else 20),
                                    (160 if selected_items[4] else 35))
        elif counter[0] == rnt[0]:
            Bomb = True
        elif counter[0] == rnt[0] + 40:
            counter[0] = -1
        #SpeedUp
        if counter[1] == 0:
            speedupx, speedupy = -1, -1
            rnt[1] = random.randint((20 if selected_items[1] else 65),
                                    (35 if selected_items[1] else 85))
        elif counter[1] == rnt[1]:
            SpeedUp = True
        elif counter[1] == rnt[1] + 60:  # + (rate - 8) * 5:
            counter[1] = -1
        #SpeedDown
        if counter[2] == 0:
            speeddownx, speeddowny = -1, -1
            rnt[2] = random.randint((20 if selected_items[0] else 65),
                                    (35 if selected_items[0] else 85))
        elif counter[2] == rnt[2]:
            SpeedDown = True
        elif counter[2] == rnt[2] + 60:
            counter[2] = -1

        counter = [x + 1 for x in counter]
        #Spawner
        if Bomb == True:
            bombx, bomby = random_cord(blocks)
            Bomb = False
        if SpeedUp == True:
            speedupx, speedupy = random_cord(blocks)
            SpeedUp = False
        if SpeedDown == True:
            speeddownx, speeddowny = random_cord(blocks)
            SpeedDown = False
        #Collision Logics
        if tuple(snake) == (applex, appley):
            body.append(body[-1])
            Apple = True
            score += 100 if point_2 else 50
        elif tuple(snake) == (bombx, bomby):
            bombx, bomby = -1, -1
            score -= 100
        elif tuple(snake) == (speedupx, speedupy):
            speedupx, speedupy = -1, -1
            rate += 2
            score += 300 if point_2 else 150
        elif tuple(snake) == (speeddownx, speeddowny):
            speeddownx, speeddowny = -1, -1
            rate -= 2
            score += 300 if point_2 else 150
        if Apple == True:
            applex, appley = random_cord(blocks)
            Apple = False
        if (tuple(snake) in body[1::]):
            gameover = True
        if not (-10 < snake[0] < 450) or not (-10 + 2 * PIXEL < snake[1] <
                                              450) and not selected_items[5]:
            gameover = True
        if selected_items[5]:
            snake[0] = -13 if snake[0] == 452 else (
                452 if snake[0] == -13 else snake[0])
            snake[1] = 17 if snake[1] == 452 else (
                452 if snake[1] == 17 else snake[1])
        # 0 speed Realm
        if rate == 0:
            realm = True
            t0 = time.time()
            rate = 200
        if realm:
            selected_items[5] = True
            Theme[2], Theme[7] = Theme[7], Theme[2]
            Theme[4] = Theme[0]
            Theme[5], Theme[3], Theme[6], Theme[
                1] = VOILET, VOILET, VOILET, VOILET
            if counter[0] % 5 == 0:
                body.append(body[-1])
            if counter[0] % 2 == 0:
                direction = 'up' if snake[1] > 250 else 'down'
            else:
                direction = 'left' if snake[0] > 250 else 'right'

            if time.time() - t0 > 3:
                SCREEN.fill((0, 0, 0))
                show('The laws of Physics tends to bend when', (200, 200, 200),
                     20, 210, 22)
                show('someone enters the speed 0 realm', (200, 200, 200), 45,
                     240, 22)
            else:
                if not ee_done:
                    ee_dec = screen_animation(False, 5, Theme[7], 0.001)
                    ee_done = ee_dec
                if ee_done:
                    ee_dec = screen_animation(True, 5, Theme[7], 0.0001)
                    ee_done = not ee_dec
        #event loop

        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and not direction == "down":
                    direction = "up"
                if event.key == pygame.K_DOWN and not direction == "up":
                    direction = "down"
                if event.key == pygame.K_LEFT and not direction == "right":
                    direction = "left"
                if event.key == pygame.K_RIGHT and not direction == "left":
                    direction = "right"
        #Movement
        if direction == 'up':
            snake[1] -= PIXEL
        elif direction == 'down':
            snake[1] += PIXEL
        elif direction == 'left':
            snake[0] -= PIXEL
        elif direction == 'right':
            snake[0] += PIXEL
        #GameOver
        if gameover:
            popup = True
            t = f'{(time.time() - start):.2f}'
            coins = int(8 * (score / 1000) -
                        (time.time() - start) / 60) * (2 if coin_2 else 1)
            data['coin'] = f"{int(data['coin'])+coins}"
            if data['highscore'] == score:
                data['time'] = t

            # data['coin'] = f"{int(data['coin'])+coins}"
            update_data()

            bigGame = bigGameVar()

            if internet:
                try:
                    pushData(data['name'], score, t, bigGame)
                except:
                    print(
                        'Data not sent to servers due to an unexpected error')
                    saveGameDataForLater(data['name'], score, t)
            else:
                print(
                    'Data not sent as there is no internet. The data is saved and will be sent when there is an internet connection and the game is opened.'
                )
                saveGameDataForLater(data['name'], score, t)
    #block loop
    for block in blocks:
        block.block_type = None
        for part in body:
            if (block.x, block.y) == part:
                block.block_type = 'head'
        if (block.x, block.y) == tuple(snake):
            block.block_type = 'snake'
        elif (block.x, block.y) == (applex, appley):
            block.block_type = 'apple'
        elif (block.x, block.y) == (bombx, bomby):
            block.block_type = 'bomb'
        elif (block.x, block.y) == (speedupx, speedupy):
            block.block_type = 'speedup'
        elif (block.x, block.y) == (speeddownx, speeddowny):
            block.block_type = 'speeddown'
        block.draw()
    #Score
    data['highscore'] = score if score > data['highscore'] else data[
        'highscore']
    mul = (LENGTH) // 3
    pygame.draw.rect(SCREEN, DARKBROWN, (mul - 140, 2, 95, 24))
    show("Score :" + str(score), Theme[7], mul - 140 + 5, 6, 16)
    pygame.draw.rect(SCREEN, DARKBROWN, (mul * 2 - 140, 2, 90, 24))
    show("Speed :" + str(rate if rate < 200 else 0), Theme[7],
         mul * 2 - 140 + 5, 6, 16)
    pygame.draw.rect(SCREEN, DARKBROWN, (mul * 3 - 145, 2, 140, 24))
    show("High Score :" + str(data['highscore']), Theme[7], mul * 3 - 145 + 5,
         6, 16)
    if popup:
        s = pygame.Surface((LENGTH, LENGTH))
        s.set_colorkey(GREY)
        s.set_alpha(200)
        SCREEN.blit(s, (0, 0))
        pygame.draw.rect(SCREEN, DARKBROWN,
                         (LENGTH // 2 - 180, LENGTH // 2 - 150, 360, 300), 0,
                         1)
        pygame.draw.rect(
            SCREEN, LIGHTBROWN,
            (LENGTH // 2 - 180 + 5, LENGTH // 2 - 150 + 5, 350, 290), 0, 1)
        show('Game Over', DARKBROWN, LENGTH // 2 - 120, LENGTH // 2 - 130, 40)
        show("Score :" + str(score), WHITE, LENGTH // 2 - 100,
             LENGTH // 2 - 80, 20)
        show("High Score :" + str(data['highscore']), WHITE, LENGTH // 2 - 100,
             LENGTH // 2 - 50, 20)
        show("Time :" + t, WHITE, LENGTH // 2 - 100, LENGTH // 2 - 20, 20)
        show("Coins :" + str(coins), WHITE, LENGTH // 2 - 100,
             LENGTH // 2 + 10, 20)
        if button('Home', LENGTH // 2 - 100, LENGTH // 2 + 40, 100, 30):
            user = 'Home'
            selected_items = [False, False, False, False, False, False]
            SCREEN = pygame.display.set_mode((LENGTH + 100, LENGTH),
                                             pygame.RESIZABLE)


def leaderboard():
    global sortedData
    # fauna
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('LEADERBOARDS', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    if len(sortedData) > 0:
        for i, dt in enumerate(sortedData):
            if i < 10:
                show(dt[0], BLACK, 30, 78 + i * 35, 30)
                show(str(dt[1]), BLACK, 175, 78 + i * 35, 30)
                show(str(dt[2]), BLACK, 320, 78 + i * 35, 30)
    else:
        show('Oops! No Data Available', WHITE, 50, 200, 30)
    if (button('R', LENGTH - 40, 10, 20, 20, BLACKBROWN, 4, 14, WHITE,
               LIGHTBROWN)):
        sortedData = pullingSortedData()
        print('Refresh clicked')


def missions():
    global user
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('MISSIONS', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (20, 50, LENGTH - 40, 40), 0, 8)
    show("Today's Special Mission :", WHITE, 30, 54, 16)
    show("Mission Text", WHITE, 35, 74, 14)
    pygame.draw.line(SCREEN, WHITE, (100, 100), (LENGTH - 20, 100), 3)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (20, 110, LENGTH - 40, 40), 0, 8)
    show("Mission 1 :", WHITE, 30, 114, 16)
    show("Mission Text", WHITE, 35, 134, 14)
    user = 'Home' if button('Home', LENGTH - 70, 10, 100, 30) else user


opened = [True, False, False, False]

pop = False


def marketplace():
    global user, start, SCREEN, LENGTH, opened, pop, q
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('MARKET PLACE', WHITE, 10, 10, 20)
    mul = (LENGTH - 30) // 4
    pygame.draw.rect(SCREEN, DARKBROWN, (10, 50, mul - 10, 390))

    def popup():
        global pop
        s = pygame.Surface((LENGTH, LENGTH))
        s.set_colorkey(GREY)
        s.set_alpha(200)
        SCREEN.blit(s, (0, 0))
        pygame.draw.rect(SCREEN, LIGHTBROWN, (50, 180, 450, 90), 0, 1)
        show('Are you sure you wanna purchase this item ?', BLACK, 70, 200, 18)
        pop = False if button('no',
                              410,
                              240,
                              70,
                              30,
                              DARKBROWN,
                              text_size=18,
                              text_col=WHITE,
                              hover_col=DARKBROWN,
                              hover_width=0) else True

        return True if button('yes',
                              70,
                              240,
                              70,
                              30,
                              DARKBROWN,
                              text_size=18,
                              text_col=WHITE,
                              hover_col=DARKBROWN,
                              hover_width=0) else False

    if button("Background",
              10,
              50,
              mul - 10,
              30, (LIGHTBROWN if opened[0] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_width=0,
              hover_col=LIGHTBROWN):
        opened = [True, False, False, False]
    if button("Snake",
              10,
              80,
              mul - 10,
              30, (LIGHTBROWN if opened[1] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_width=0,
              hover_col=LIGHTBROWN):
        opened = [False, True, False, False]
    if button("Powerups",
              10,
              110,
              mul - 10,
              30, (LIGHTBROWN if opened[2] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_col=LIGHTBROWN,
              hover_width=0):
        opened = [False, False, True, False]
    if button("Offers",
              10,
              140,
              mul - 10,
              30, (LIGHTBROWN if opened[3] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_col=LIGHTBROWN,
              hover_width=0):
        opened = [False, False, False, True]
    pygame.draw.rect(SCREEN, LIGHTBROWN,
                     (mul + 5, 50, LENGTH - 10 - mul - 5, 390))
    with open('items.dat', 'rb') as file:
        list_items = pickle.load(file)
        if opened[2]:
            for i, item in enumerate(list_items['Powerups'].items()):

                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    SCREEN.blit(def_powerup, (37 + (i + 1) * mul, 80))
                    if i == 1:
                        show(item[1][1], BLACK, 30 + (i + 1) * mul, 165, 18)
                        show(item[0], BLACK, 25 + (i + 1) * mul, 185, 11)
                        show(f'{item[1][0]} in stock', WHITE,
                             30 + (i + 1) * mul, 210, 10)
                    else:
                        show(item[1][1], BLACK,
                             (85 if
                              (i + 1) == 2 else 30) + (i + 1) * mul, 165, 18)
                        show(item[0], BLACK,
                             (85 if
                              (i + 1) == 2 else 30) + (i + 1) * mul, 185, 12)
                        show(f'{item[1][0]} in stock', WHITE,
                             30 + (i + 1) * mul, 210, 10)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if not pop:
                        if pos[0] >= x and pos[0] <= x + width and pos[
                                1] >= y and pos[1] <= y + height:
                            if pygame.mouse.get_pressed()[0]:
                                pop = True
                                q = i
                            s.set_alpha(60)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    show(item[1][1], BLACK, 30 + (i - 2) * mul, 355, 18)
                    show(item[0], BLACK, 30 + (i - 2) * mul, 375, 12)
                    show(f'{item[1][0]} in stock', WHITE, 30 + (i - 2) * mul,
                         400, 10)
                    SCREEN.blit(def_powerup, (37 + (i - 2) * mul, 270))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if not pop:
                        if pos[0] >= x and pos[0] <= x + width and pos[
                                1] >= y and pos[1] <= y + height:
                            if pygame.mouse.get_pressed()[0]:
                                pop = True
                                q = i
                            s.set_alpha(60)
                    SCREEN.blit(s, (x, y))
                if pop:
                    cont = popup()
                    if cont:
                        t = list_items['Powerups'][list(
                            list_items['Powerups'].keys())[q]]
                        data['coin'] = str(int(data['coin']) - int(t[1]))
                        update_data()
                        with open('items.dat', 'wb') as f:
                            list_items['Powerups'][list(
                                list_items['Powerups'].keys())[q]] = (
                                    str(int(t[0]) + 1), t[1])
                            pickle.dump(list_items, f)
                            pop = False
        elif opened[3]:
            for i, item in enumerate(list_items['Offers'].items()):
                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    SCREEN.blit(def_powerup, (37 + (i + 1) * mul, 80))
                    if i <= 1:
                        show('', BLACK, 30 + (i + 1) * mul, 165, 18)
                        show('', BLACK, 25 + (i + 1) * mul, 185, 14)
                    else:
                        show('40', BLACK, 30 + (i + 1) * mul, 165, 18)
                        show('2x Box', BLACK, 30 + (i + 1) * mul, 185, 14)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0]:
                            selected_items[i] = not selected_items[i]
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    k = sum([(40 if x == '5' else
                              (15 if x == '4' else
                               (12 if int(x) <= 1 else 8))) * int(y)
                             for x, y in item[1].items()])
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    SCREEN.blit(def_powerup, (37 + (i - 2) * mul, 270))
                    if i == 5:
                        show('15', BLACK, 30 + (i - 2) * mul, 355, 18)
                        show('Lucky Box', BLACK, 30 + (i - 2) * mul, 375, 14)
                    else:
                        show(str(int(k * 0.8)), BLACK, 30 + (i - 2) * mul, 355,
                             18)
                        show(str(k), BLACK, 30 + (i - 2) * mul, 375, 14)
                        pygame.draw.line(SCREEN, BLACK,
                                         (60 + (i - 2) * mul, 382),
                                         (65 + (i - 2) * mul - 50, 382), 1)
                        show(item[0], BLACK, 30 + (i - 2) * mul, 400, 14)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0]:
                            selected_items[i] = not selected_items[i]
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))
        else:
            for i, item in enumerate(list_items['Themes'].items()):
                Dic = list(item[1].keys())
                D = list(item[1].values())
                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pygame.draw.rect(SCREEN,
                                     globals()[Dic[0 if opened[0] else 1]],
                                     (x + 15, y + 15, width - 30, 65))
                    show(('25' if opened[0] else '15'), BLACK,
                         30 + (i + 1) * mul, 165, 18)
                    show(Dic[0 if opened[0] else 1], BLACK, 32 + (i + 1) * mul,
                         185, 14)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed(
                        )[0] and not D[0 if opened[0] else 1]:
                            pop = True
                            q = i
                        s.set_alpha(60)
                    if D[0 if opened[0] else 1]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    show(('25' if opened[0] else '15'), BLACK,
                         30 + (i - 2) * mul, 355, 18)
                    show(Dic[0 if opened[0] else 1], BLACK, 32 + (i - 2) * mul,
                         375, 14)
                    pygame.draw.rect(SCREEN,
                                     globals()[Dic[0 if opened[0] else 1]],
                                     (x + 15, y + 15, width - 30, 65))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed(
                        )[0] and not D[0 if opened[0] else 1]:
                            pop = True
                            q = i
                        s.set_alpha(60)
                    if D[0 if opened[0] else 1]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))
                if pop:
                    cont = popup()
                    if cont:
                        t = list_items['Themes'][list(
                            list_items['Themes'].keys())[q]]
                        data['coin'] = str(
                            int(data['coin']) - (25 if opened[0] else 15))
                        update_data()
                        with open('items.dat', 'wb') as f:
                            t[list(t.keys())[0 if opened[0] else 1]] = True
                            list_items['Themes'][list(
                                list_items['Themes'].keys())[q]] = t
                            pickle.dump(list_items, f)
                            pop = False

    user = 'Home' if button('Home', LENGTH - 70, 10, 100, 30) else user
    show(data['coin'], LIGHTBROWN, LENGTH - 130, 10, 16)


def inventory():
    global user, start, SCREEN, LENGTH, opened
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('INVENTORY', WHITE, 10, 10, 20)
    mul = (LENGTH - 30) // 4
    pygame.draw.rect(SCREEN, DARKBROWN, (10, 50, mul - 10, 390))
    if button("Background",
              10,
              50,
              mul - 10,
              30, (LIGHTBROWN if opened[0] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_width=0,
              hover_col=LIGHTBROWN):
        opened = [True, False, False, False]
    if button("Snake",
              10,
              80,
              mul - 10,
              30, (LIGHTBROWN if opened[1] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_width=0,
              hover_col=LIGHTBROWN):
        opened = [False, True, False, False]
    if button("Powerups",
              10,
              110,
              mul - 10,
              30, (LIGHTBROWN if opened[2] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_col=LIGHTBROWN,
              hover_width=0):
        opened = [False, False, True, False]
    if button("2x",
              10,
              140,
              mul - 10,
              30, (LIGHTBROWN if opened[3] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_col=LIGHTBROWN,
              hover_width=0):
        opened = [False, False, False, True]
    pygame.draw.rect(SCREEN, LIGHTBROWN,
                     (mul + 5, 50, LENGTH - 10 - mul - 5, 390))

    with open('items.dat', 'rb') as file:
        list_items = pickle.load(file)
        if opened[2]:
            for i, item in enumerate(list_items['Powerups'].items()):

                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    SCREEN.blit(def_powerup, (37 + (i + 1) * mul, 80))
                    if i == 1:
                        show(item[1][1], BLACK, 30 + (i + 1) * mul, 165, 16)
                        show(item[0], BLACK, 25 + (i + 1) * mul, 185, 11)
                        show(f'{item[1][0]} in stock', WHITE,
                             30 + (i + 1) * mul, 210, 10)
                    else:
                        show(item[1][1], BLACK,
                             (85 if
                              (i + 1) == 2 else 30) + (i + 1) * mul, 165, 16)
                        show(item[0], BLACK,
                             (85 if
                              (i + 1) == 2 else 30) + (i + 1) * mul, 185, 12)
                        show(f'{item[1][0]} in stock', WHITE,
                             30 + (i + 1) * mul, 210, 10)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0]:
                            selected_items[i] = not selected_items[i]
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    show(item[1][1], BLACK, 30 + (i - 2) * mul, 355, 16)
                    show(item[0], BLACK, 30 + (i - 2) * mul, 375, 12)
                    show(f'{item[1][0]} in stock', WHITE, 30 + (i - 2) * mul,
                         400, 10)
                    SCREEN.blit(def_powerup, (37 + (i - 2) * mul, 270))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0]:
                            selected_items[i] = not selected_items[i]
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))
        else:
            for i, item in enumerate(list_items['Themes'].items()):
                Dic = list(item[1].keys())
                D = list(item[1].values())
                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pygame.draw.rect(SCREEN,
                                     globals()[Dic[0 if opened[0] else 1]],
                                     (x + 15, y + 15, width - 30, 65))
                    show(Dic[0 if opened[0] else 1], BLACK, 32 + (i + 1) * mul,
                         170, 16)
                    show(
                        'Purchased' if D[0 if opened[0] else 1] else
                        'Not Purchased', BLACK, 32 + (i + 1) * mul, 215, 10)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0]:
                            selected_items[i] = not selected_items[i]
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    show(Dic[0 if opened[0] else 1], BLACK, 32 + (i - 2) * mul,
                         360, 16)
                    show(
                        'Purchased' if D[0 if opened[0] else 1] else
                        'Not Purchased', BLACK, 32 + (i - 2) * mul, 405, 10)
                    pygame.draw.rect(SCREEN,
                                     globals()[Dic[0 if opened[0] else 1]],
                                     (x + 15, y + 15, width - 30, 65))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0]:
                            selected_items[i] = not selected_items[i]
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

    with open('items.dat', 'rb') as file:
        list_items = pickle.load(file)
        if opened[3]:
            for i, item in enumerate(list_items['Offers'].items()):
                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    SCREEN.blit(def_powerup, (37 + (i + 1) * mul, 80))
                    if i == 1:
                        show(item[1][1], BLACK, 30 + (i + 1) * mul, 165, 16)
                        show(item[0], BLACK, 25 + (i + 1) * mul, 185, 11)
                        show(f'{item[1][0]} in stock', WHITE,
                             30 + (i + 1) * mul, 210, 10)
                    else:
                        show(item[1][1], BLACK,
                             (85 if
                              (i + 1) == 2 else 30) + (i + 1) * mul, 165, 16)
                        show(item[0], BLACK,
                             (85 if
                              (i + 1) == 2 else 30) + (i + 1) * mul, 185, 12)
                        show(f'{item[1][0]} in stock', WHITE,
                             30 + (i + 1) * mul, 210, 10)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0]:
                            selected_items[i] = not selected_items[i]
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    show(item[1][1], BLACK, 30 + (i - 2) * mul, 355, 16)
                    show(item[0], BLACK, 30 + (i - 2) * mul, 375, 12)
                    show(f'{item[1][0]} in stock', WHITE, 30 + (i - 2) * mul,
                         400, 10)
                    SCREEN.blit(def_powerup, (37 + (i - 2) * mul, 270))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0]:
                            selected_items[i] = not selected_items[i]
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

    user = 'Home' if button('Home', LENGTH - 70, 10, 100, 30) else user


def settings():
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('SETTINGS', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    pass


def newuser():
    LENGTH = pygame.display.get_surface().get_width()
    global user, Text_Val, iterrr, Cursor, data
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('SIGN UP', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    if len(Text_Val) == 0:
        show("Type your name here.", WHITE, (LENGTH - 200) // 2, 220, 20)
    else:
        show(Text_Val, WHITE, (LENGTH - len(Text_Val) * 10) // 2, 220, 20)
        if iterrr % 8 == 0:
            Text_Val = Text_Val[:-1] + '|'
            Cursor = True
        if iterrr % 8 == 4 and Cursor:
            Text_Val = Text_Val[:-1] + ' '
            Cursor = False
        iterrr += 1
    user = 'Home' if button('Home', LENGTH - 70, 10, 100, 30) else user
    #
    # if iterrr>10:
    #     Text_Val+='|'
    # else:
    #     Text_Val=Text_Val[:-1]
    # iterrr+=1
    # iterrr=0 if iterrr>20 else iterrr
    pygame.draw.line(SCREEN, DARKBROWN, (50, 250), (LENGTH - 50, 250), 1)
    Text_Ent = button('Create Account', (LENGTH - 155) // 2,
                      260,
                      140,
                      40,
                      bg_color=DARKBROWN,
                      text_col=WHITE,
                      text_size=14,
                      hover_width=0)
    for event in event_list:
        if event.type == pygame.KEYDOWN:
            if event.unicode in ALPHA:
                Text_Val = Text_Val[:-1] + str(
                    event.unicode) + ('|' if Cursor else ' ')
            elif event.key == pygame.K_BACKSPACE:
                Text_Val = Text_Val[:-2] + ('|' if Cursor else ' ')
            elif event.unicode == '\r':
                Text_Ent = True

    if Text_Ent:
        data = {'name': Text_Val[:-1], 'highscore': 0, 'coin': 0, 'time': ''}
        update_data()
        user = 'Home'


def cheater():
    SCREEN.fill(BLACK)
    show('Cheater Cheater Compulsive Eater', WHITE, 20, 30, 24)
    with open('userData.dat', 'wb') as file:
        pickle.dump({'name': '', 'highscore': 0, 'coins': 0, 'time': ''}, file)


def main():
    global event_list, Text_Val
    SCREEN.fill(BLACK)
    home_params()
    while True:
        event_list = pygame.event.get()
        if user == 'Home':
            home()
        elif user == 'Emulator':
            emulator()
        elif user == 'LeaderBoard':
            leaderboard()
        elif user == 'Settings':
            settings()
        elif user == 'NewUser':
            newuser()
        elif user == 'Cheater':
            cheater()
        elif user == 'Arsenal':
            arsenal()
        elif user == 'MarketPlace':
            marketplace()
        elif user == 'Inventory':
            inventory()
        elif user == 'Missions':
            missions()
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        CLOCK.tick(rate)
        if breaker:
            break

main()

if breaker:
    with open('Builder.py', 'r') as f:
        file = f.read()
        exec(file)
