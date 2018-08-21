import pygame
import random
import time
import os
import sys
import datetime

pygame.init()

# Checks the OS type to make sure that the paths are correct
osType = "\\"

if os.name == "posix":
    osType = "/"
else:
    osType = "\\"


# Window height and width
width = 1000
height = 800

# Making some color variables so that they are easy to call
white = (255, 255, 255)
sky_blue = (18,178,238,100)
black = (0, 0, 0)
red = (255, 0, 0)
green = (34, 145, 20)
gold = (255, 215, 0)

centerScreen = [width/2, height/2]

# Initializing the screen
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snakey")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)

# Initializes the sounds
click = pygame.mixer.Sound("audio{}click.wav".format(osType))

# Size of the snake in pixels
snakesize = 50

# Chance variables
goldAppleChance = .01
doubleChance = .1
bombChance = .35

# Number of ms in between each frame
gameSpeed = 55

# Snake Direction
xVelocity = 0
yVelocity = 0

# A list of Body types that contains a x and y element
snakeBody = []

# Which file is open
gameOpen = None

# Name of the skins
skins = []

# Snake body part has a x and an y
class Body():
    def __init__(self, x=-100, y=0):
        self.x = x
        self.y = y



# Randomly generated a new apple cords.
def newApple():
    global width, height, activeChallenges

    # Creates new coordinates if there are walls.
    if activeChallenges["walls"] or ((activeChallenges["Top Bottom Walls"] and activeChallenges["Side Walls"])):
        ax = random.randrange(snakesize, width - snakesize, snakesize)
        ay = random.randrange(snakesize, height - snakesize, snakesize)

    elif activeChallenges["Top Bottom Walls"]:
        ax = random.randrange(0, width, snakesize)
        ay = random.randrange(snakesize, height - snakesize, snakesize)

    elif activeChallenges["Side Walls"]:
        ax = random.randrange(snakesize, width - snakesize, snakesize)
        ay = random.randrange(0, height, snakesize)

    else:
        ax = random.randrange(0, width, snakesize)
        ay = random.randrange(0, height, snakesize)

    for part in snakeBody:
        if part.x == ax and part.y == ay:
            newApple()
    return (ax, ay)

# Opens error file so that if inconsistencies are found they will be printed to a log
error = open("README{}error log.txt".format(osType), "a")
date = str(datetime.datetime.now())
error.write("\n" + date + "\n")

# Place holder cords, before each game the restart() method is ran.
applecords = []

ax = 0
ay = 0

apple = Body(ax, ay)
apples = [apple]
goldApple = []

# Initalizes the bomb list
bombs = []

nearmiss = False

# Initilizes the snake head
sn = Body(x = width/2, y = height/2)
snakeBody.append(sn)

# Checks for collision in the list of snake body parts. If two body parts occupy the same location then the player loses
def checkCollision(list):
    for i in list:
        for j in list:
            if list.index(i) != list.index(j) and list.index(i) != 1 and list.index(j) != 1:
                if (list.index(i) == 0 and list.index(j) == 1) or (list.index(i) == 1 and list.index(j) ==0):
                    pass
                else:
                    if j.x == i.x and j.y == i.y:
                        return True
    return False


# Allow user to display text to the screen. The location entered will be the center of the text.
# location must be a tuple or a list.
def displayText(msg, color, location=[0,0], textSize=55):
    font = pygame.font.SysFont(None, textSize)
    text = font.render(msg, True, color)
    x = font.size(msg)[0]
    y = font.size(msg)[1]
    screen.blit(text, (location[0] - x/2, location[1] - y/2))


# Initalizes the locations for the menu options
scoreLocation = [0,height - 20]
creditsLocation = [scoreLocation[0] + 400, scoreLocation[1]]
selection = [True, False, False]
startGame = [centerScreen[0], centerScreen[1] - 100]
exitPos = [centerScreen[0], centerScreen[1] + 100]

# Frame count
fCount = 0

# To show or not to show the flashing menu option
show = True

# Game loop booleans
saveScreen = True
menu = False
loaded = False
options = False
difficulty = False
challenges = False
snakes = False
running = False
lost = False
stats = False

# Sets all the game loop variables to false. Forces the game to quit
# When adding a new variable make sure to add it to the global line
def quit():
    global saveScreen, menu, loaded, options, difficulty, snakes, running, lost, challenges, stats
    saveScreen = False
    menu = False
    stats = False
    loaded = False
    options = False
    difficulty = False
    challenges = False
    snakes = False
    running = False
    lost = False

# Number of snake parts added through out the game
score = 0


# Imports avaliable save files
saves = open("saves{}saves.txt".format(osType), "r")
avaliable = []
for line in saves:
    temp = line.strip()
    avaliable.append(temp)
saves.close()


# Game info is a dictionary of each variable and its condition
gameInfo = {}


# Variable to check if the controller is in use
controller = False

lastKnowsPos = [0,0]

# Joystick initalization
if pygame.joystick.get_count() >= 1:
    joysticks = pygame.joystick.get_count()

    for i in range(joysticks):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
#
#
#
#

# Restarts all the game variables
def restart():
    global lost, score, snakeBody, xVelocity, yVelocity, goldApple, apples, bombs
    lost = False
    score = 0
    sn = Body(x=width / 2, y=height / 2)
    snakeBody = [sn]
    yVelocity = 0
    xVelocity = 0
    cords = newApple()
    goldApple = []
    apple = Body(cords[0], cords[1])
    apples = [apple]
    bombs = []

# Loads in game file
def loadGame(file, seconds = 1):
    global loaded, saveScreen, menu, gameInfo, gameOpen, hs, skins, gameSpeed, activeChallenges, bombChance, challengeList
    # Loads saves into a dictionary
    gameSave = open("saves{}".format(osType) + file + ".txt", "r")

    for line in gameSave:
        tempTup = line.strip().split(" = ")
        if tempTup[0] not in gameInfo:
            gameInfo[tempTup[0]] = tempTup[1]


    # Corrects variable types in the dictionary
    for key, value in gameInfo.items():
        try:
            gameInfo[key] = float(value)
        except:
            pass
        try:
            gameInfo[key] = int(value)

        except:
            pass

        if value.lower() == "true":
            gameInfo[key] = True
        elif value.lower() == "false":
            gameInfo[key] = False


    # Creates a list of all the avaliable texture names
    skins = gameInfo["avaliableSkins"].split(",")

    # Creates a list of active challenges
    activeChallenges = {}
    challengeList = []
    tempActiveChallenges = gameInfo["challenges"].split(" ; ")
    for i in tempActiveChallenges:

        temp = i.split(":")

        challengeList.append(temp[0])

        if temp[1] == "True":
            temp[1] = True
        elif temp[1] == "False":
            temp[1] = False

        activeChallenges[temp[0]] = temp[1]

    challengeList.append("Back")

    # Imports the highscore
    hs = int(gameInfo["highscore"])

    gameSave.close()
    gameOpen = file

    # Gets the set game difficulty
    updateDifficulty(gameInfo["difficulty"])

    # Runs the loading animation then sets the variables to their correct state so the game can move on
    # Wondering if nessary loading wont load on Mac OS
    #loading(seconds)
    loaded = True
    saveScreen = False
    menu = True

# Writes to text document updating all the vatiables
def saveGame(file):
    global gameInfo
    if file == None:
            pass
    else:
        gameSave = open("saves{}".format(osType) + file + ".txt", "w")
        for key, val in gameInfo.items():
            gameSave.write(key + " = " + str(val) + "\n")
        gameSave.close()


# Creates a loading animation for 3 seconds **currently not used**
def loading(seconds = 1):
    for i in range(1,4):
        dots = "." * i
        screen.fill(white)
        displayText("Loading" + dots, black, (centerScreen[0] + len(dots) * 5, centerScreen[1]))
        pygame.display.flip()
        pygame.time.wait(int(1000 * seconds))

# Updates Game info based on achievements
def updateAchievements():
    global gameInfo

    # Unlocks golden skin when player gets a golden apple
    if gameInfo["goldApples"] > 0 and not gameInfo["golden"]:
        gameInfo["golden"] = True

    # Unlocks classic skin when player plays 10 games
    if gameInfo["gamesPlayed"] >= 10 and not gameInfo["classic"]:
        gameInfo["classic"] = True

    # Unlocks Robo skin when player gets a score of 20 in a game
    if gameInfo["highscore"] > 20 and not gameInfo["robo"]:
        gameInfo["robo"] = True

    # Unlocks worm if player has collected over 250 apples
    if gameInfo["totalApples"] >= 250 and not gameInfo["worm"]:
        gameInfo["worm"] = True

    # Unlocks error skin if player presses 1500 keys
    if gameInfo["keysPressed"] >= 1500 and not gameInfo["error"]:
        gameInfo["error"] = True

# Returna a list of true and falses to use for when skin selection is in process
def getSnakes():
    global skins
    temp = [True]
    for i in range(len(skins)-1):
        temp.append(False)

    return temp

# Loads new game from format file
def loadFormat(file):
    form = open("saves{}format.txt".format(osType), "r")
    save = open("saves{}".format(osType) + file + ".txt", "w")
    for i in form:
        save.write(i)

    form.close()
    save.close()

# Skin class for the previews of images includes a preview image, info, and unlock description
class Skin():
    global error

    def __init__(self, img = None, info = "", unlock = ""):
        self.setPreview(img)
        self.setInfo(info)
        self.setUnlock(unlock)
        self.canShow = True

    # Sets the preview to a pygame image
    def setPreview(self, img):
        if type(img) == pygame.Surface:
            self.preview = img
        else:
            error.write("PREVIEW ERROR: Preview must be a pygame.Surface object\n")



    # Blits the skin preview in the middle of the screen
    def show(self):
        # Checks if the data type is correct if it is incorrect once in a single game cucle it will only show the error once.
        if self.canShow:
            try:
                screen.blit(self.preview, (width/2 - 2 * snakesize, height/2 - 2 * snakesize))
            except AttributeError:
                displayText("ERROR", red, centerScreen)
                error.write("SKIN PREVIEW ERROR: Incorrect data type for skin preview. SKIN INFO:" + self.info + "\n")
                self.canShow = False
        else:
            displayText("ERROR", red, centerScreen)


    # Provide a description for the skin i.e. for golden skin "It glistens in the sun"
    def setInfo(self, info):
        if type(info) == str:
            self.info = info
        else:
            error.write("SKIN INFO ERROR: Enter a string for the skin info\n")

    # Displays info on the center bottom of screen
    def showInfo(self):
        displayText(self.info, black, (centerScreen[0], height * (7/8)))

    # Provide a description of unlock requirements i.e. score 50
    def setUnlock(self, unlock):
        if type(unlock) == str:
            self.unlock = unlock
        else:
            error.write("SKIN UNLOCK ERROR: Enter a string for the skin unlock\n")

    # Displays unlock requirements on the center bottom of screen
    def showUnlock(self):
        displayText(self.unlock, black, (centerScreen[0], height * (7/8)))


skinPreviews = []
# Loads textures for the snakes option so that textures are not rendered everytime. Increases effiency
def getSnakeOpt():
    global lock, arrowLeft, arrowRight

    if len(skinPreviews) != len(skins):
        lock = pygame.image.load("textures{}options{}snakes{}lockalpha.png".format(osType,osType,osType)).convert_alpha()
        lock = pygame.transform.scale(lock, (4 * snakesize,  4 * snakesize))


        arrowLeft = pygame.image.load("textures{}options{}snakes{}arrow.png".format(osType,osType,osType)).convert_alpha()
        arrowLeft = pygame.transform.scale(arrowLeft, (3 * snakesize, 3 * snakesize))
        arrowRight = pygame.transform.flip(arrowLeft, True, False)

        # Format Line for the addition of future textures
        # Make sure each texture is added in the same order that it is added in the list on avaliableSkins
        # previewnamePreview = pygame.image.load("textures{}options{}snakes{}previewname.png".format(osType,osType,osType)).convert_alpha()
        # previewnamePreview = pygame.transform.scale(previewnamePreview, (4*snakesize, 4*snakesize))
        # previewname = Skin(previewnamePreview, "Info", "Unlock")
        # skinPreviews.append(previewname)

        defaultPreview = pygame.image.load("textures{}options{}snakes{}default.png".format(osType, osType, osType)).convert_alpha()
        defaultPreview = pygame.transform.scale(defaultPreview, (4 * snakesize, 4 * snakesize))
        default = Skin(defaultPreview, "JJust slithering")
        skinPreviews.append(default)

        classicPreview = pygame.image.load("textures{}options{}snakes{}classic.png".format(osType,osType,osType)).convert_alpha()
        classicPreview = pygame.transform.scale(classicPreview, (4*snakesize, 4*snakesize))
        classic = Skin(classicPreview, "Just the good o'le", "Play 10 games")
        skinPreviews.append(classic)

        roboPreview = pygame.image.load("textures{}options{}snakes{}robo.png".format(osType, osType, osType)).convert_alpha()
        roboPreview = pygame.transform.scale(roboPreview, (4 * snakesize, 4 * snakesize))
        robo = Skin(roboPreview, "Boop Beep Hsss", "Reach a score of 20")
        skinPreviews.append(robo)

        wormPreview = pygame.image.load("textures{}options{}snakes{}worm.png".format(osType,osType,osType)).convert_alpha()
        wormPreview = pygame.transform.scale(wormPreview, (4*snakesize, 4*snakesize))
        worm = Skin(wormPreview, "Develops anus first", " Eat 250 apples")
        skinPreviews.append(worm)

        goldenPreview = pygame.image.load("textures{}options{}snakes{}golden.png".format(osType,osType,osType)).convert_alpha()
        goldenPreview = pygame.transform.scale(goldenPreview, (4*snakesize, 4*snakesize))
        golden = Skin(goldenPreview, "24 karat", "Eat a golden apple")
        skinPreviews.append(golden)

        errorPreview = pygame.image.load("textures{}options{}snakes{}error.png".format(osType, osType, osType)).convert_alpha()
        errorPreview = pygame.transform.scale(errorPreview, (4*snakesize, 4*snakesize))
        error = Skin(errorPreview, "texture not found", "Press 1500 keys")
        skinPreviews.append(error)

# Position for skinPreviews list to display
current = 0

# All variables for the snakes menu
        # Whether or not to display the locked text
locked = False
        # Direction of animation
direction = "NONE"
        # Speed of animation higher is faster
animation_speed = 25
        # Default variable DON'T CHANGE
rate = 10 * width

# Animates the skin previews to move off the screen and the new one onto the screen
def animate(direction, i):
    global current, skinPreviews, skins, error

    direction = direction.lower()
    try:
        if direction == "left":
            if current < len(skinPreviews) - 1:
                screen.blit(skinPreviews[current].preview, (width/2 - 2 * snakesize - i, height/2 - 2 * snakesize))
                screen.blit(skinPreviews[current + 1].preview, (width + 4 * snakesize - i, height/2 - 2 * snakesize))
                if not gameInfo[skins[current]]:
                    screen.blit(lock, (width/2 - 2 * snakesize - i, height/2 - 2 * snakesize))
                if not gameInfo[skins[current + 1]]:
                    screen.blit(lock, (width + 4 * snakesize - i, height/2 - 2 * snakesize))
            else:
                screen.blit(skinPreviews[current].preview, (width / 2 - 2 * snakesize - i, height / 2 - 2 * snakesize))
                screen.blit(skinPreviews[0].preview, (width + 4 * snakesize - i, height / 2 - 2 * snakesize))
                if not gameInfo[skins[current]]:
                    screen.blit(lock, (width/2 - 2 * snakesize - i, height/2 - 2 * snakesize))
                if not gameInfo[skins[0]]:
                    screen.blit(lock, (width + 4 * snakesize - i, height/2 - 2 * snakesize))

        elif direction == "right":
            if current > 0:
                screen.blit(skinPreviews[current].preview, (width/2 - 2 * snakesize + i, height/2 - 2 * snakesize))
                screen.blit(skinPreviews[current-1].preview, (-8 * snakesize + i, height/2 - 2 * snakesize))
                if not gameInfo[skins[current]]:
                    screen.blit(lock, (width/2 - 2 * snakesize + i, height/2 - 2 * snakesize))
                if not gameInfo[skins[current - 1]]:
                    screen.blit(lock, (-8 * snakesize + i, height/2 - 2 * snakesize))
            else:
                screen.blit(skinPreviews[current].preview, (width / 2 - 2 * snakesize + i, height / 2 - 2 * snakesize))
                screen.blit(skinPreviews[len(skinPreviews) - 1].preview, (-8 * snakesize + i, height / 2 - 2 * snakesize))
                if not gameInfo[skins[current]]:
                    screen.blit(lock, (width / 2 - 2 * snakesize + i, height / 2 - 2 * snakesize))
                if not gameInfo[skins[len(skins) - 1]]:
                    screen.blit(lock, (-8 * snakesize + i, height / 2 - 2 * snakesize))
    except AttributeError:
        displayText("ERROR", red, centerScreen)
        error.write("ATTRIBUTE ERROR: Incorrect date type being blitted. MUST BE pygame surface check skin import\n")

# When p is pressed while the game is running the game will be paused until the player presses the p key or the backspace key
def pause():
    displayText("PAUSED", red, centerScreen, 85)

    pygame.display.flip()

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    quit()
                elif event.key == pygame.K_p or event.key == pygame.K_BACKSPACE:
                    paused = False

# Initalizes the textures for the challanges that are active
def initChallenge():
    global activeChallenge, brickWall, bomb
    if activeChallenges["bombs"]:
        bomb = pygame.image.load("textures{}challenges{}bombs{}bomb.png".format(osType,osType,osType)).convert_alpha()
        bomb = pygame.transform.scale(bomb, (snakesize, snakesize))
    if activeChallenges["Top Bottom Walls"] or activeChallenges["Side Walls"] or activeChallenges["walls"]:
        brickWall = pygame.image.load("textures{}challenges{}walls{}brick.jpeg".format(osType, osType, osType)).convert_alpha()
        brickWall = pygame.transform.scale(brickWall, (snakesize, snakesize))


# Updates the difficulty of the game
def updateDifficulty(difficulty):
    global gameSpeed, bombChance
    if difficulty == "easy":
        gameSpeed = 75
        bombChance = .2
        gameInfo["difficulty"] = "easy"
    elif difficulty == "moderate":
        gameSpeed = 55
        bombChance = .35
        gameInfo["difficulty"] = "moderate"
    elif difficulty == "hard":
        gameSpeed = 40
        bombChance = .5
        gameInfo["difficulty"] = "hard"


#

                                    ##################
                                    # Load Game Loop #
                                    ##################
while saveScreen:
    screen.fill(white)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit()
        elif event.type == pygame.MOUSEBUTTONUP:
            click.play()
            pos = pygame.mouse.get_pos()[1]
            if pos < ((height-100)/3) + 100 and pos > 100:
                if avaliable[0] == "New Game":
                    avaliable[0] = "Save 1"
                    loadFormat(avaliable[0])
                loadGame(avaliable[0])

            elif pos > ((height-100)/3) + 100 and pos < 2 * (height-100)/3 + 100:
                if avaliable[1] == "New Game":
                    avaliable[1] = "Save 2"
                    loadFormat(avaliable[1])
                loadGame(avaliable[1])

            elif pos > 2 * (height-100)/3 + 100:
                if avaliable[2] == "New Game":
                    avaliable[2] = "Save 3"
                    loadFormat(avaliable[2])
                loadGame(avaliable[2])

        elif event.type == pygame.JOYBUTTONDOWN:
            controller = True
            if event.button == 0:
                for i in range(len(selection)):
                    if selection[i]:
                        selection[i] = False
                        try:
                            selection[i - 1] = True
                        except:
                            selection[2] = True
                        finally:
                            break
            elif event.button == 1:
                for i in range(len(selection)):
                    if selection[i]:
                        selection[i] = False
                        try:
                            selection[i + 1] = True
                        except:
                            selection[0] = True
                        finally:
                            break
            elif event.button == 11:
                if selection[0]:
                    if avaliable[0] == "New Game":
                        avaliable[0] = "Save 1"
                        loadFormat(avaliable[0])
                    loadGame(avaliable[0])
                    selection = [True, False, False]
                elif selection[1]:
                    if avaliable[1] == "New Game":
                        avaliable[1] = "Save 2"
                        loadFormat(avaliable[1])
                    loadGame(avaliable[1])
                    selection = [True, False, False]
                elif selection[3]:
                    if avaliable[2] == "New Game":
                        avaliable[2] = "Save 3"
                        loadFormat(avaliable[2])
                    loadGame(avaliable[2])
                    selection = [True, False, False]





    # So that the screen does not load the frame after the save names are updated
    if loaded:
        break

    # Checks for mouse movement
    pos = pygame.mouse.get_pos()
    if not (pos[0] == lastKnowsPos[0] and pos[1] == lastKnowsPos[1]):
        lastKnowsPos = pos
        controller = False

    # Checks to see if mouse is in the window based on x pos
    if not controller:
        if pos[0] > 0 and pos[0] < width-1:
            inWindow = True
        else:
            inWindow = False

        if pos[1] < ((height - 100) / 3) + 100 and pos[1] > 100 and inWindow:
            pygame.draw.rect(screen, sky_blue,(0, 100, width, (height - 100)/3))
        elif pos[1] > ((height - 100) / 3) + 100 and pos[1] < 2 * (height - 100) / 3 + 100 and inWindow:
            pygame.draw.rect(screen, sky_blue, (0, (height - 100)/3 + 100, width, (height - 100) / 3))
        elif pos[1] > 2 * (height - 100) / 3 + 100 and pos[1] < height and inWindow:
            pygame.draw.rect(screen, sky_blue, (0, 2 * (height - 100)/3 + 100, width, (height - 100) / 3))

    # Updates screen if controller is in use
    if controller:
        if selection[0]:
            pygame.draw.rect(screen, sky_blue, (0, 100, width, (height - 100) / 3))

        elif selection[1]:
            pygame.draw.rect(screen, sky_blue, (0, (height - 100) / 3 + 100, width, (height - 100) / 3))

        elif selection[2]:
            pygame.draw.rect(screen, sky_blue, (0, 2 * (height - 100) / 3 + 100, width, (height - 100) / 3))

    # Draws the text and displays text
    displayText("Snake", green, [width / 2, 50])

    third = (height - 100)/3
    startLoc = [width/2 ,height/6 + 100]

    iteration = 0
    for i in avaliable:
        displayText(i, black, startLoc)
        line = (0,(height - 100)/3 * iteration + 100, width, 2)
        iteration += 1
        pygame.draw.rect(screen, black, line)
        startLoc[1] += third

    # Updates the display
    pygame.display.flip()

saves = open("saves{}saves.txt".format(osType), "w")
for i in avaliable:
    saves.write(i + " \n")
saves.close()


# Allows for custom textures
def initTextures():
    global head, headL, headR, headD, bendBL, bendBR ,bendTL, bendTR, tailD, tailL, tailR, tailU, gapple, appleTexture, bodyUD, bodyLR
    if gameOpen != None:
        texturePath = "textures{}".format(osType) + "skins{}".format(osType) + gameInfo["texture"] + "{}".format(osType)

        ######################
        # Initalize Textures #
        ######################
            # Heads
        head = pygame.image.load(texturePath + "head.png").convert_alpha()
        head = pygame.transform.scale(head, (snakesize, snakesize))
        headL = pygame.transform.rotate(head, 90)
        headR = pygame.transform.rotate(head, -90)
        headD = pygame.transform.flip(head, False, True)

            # Body
        bodyUD = pygame.image.load(texturePath + "body.png").convert_alpha()
        bodyUD = pygame.transform.scale(bodyUD, (snakesize, snakesize))
        bodyLR = pygame.transform.rotate(bodyUD, 90)

            # Bend
        bendBL = pygame.image.load(texturePath + "bend.png").convert_alpha()
        bendBL = pygame.transform.scale(bendBL, (snakesize, snakesize))
        bendBR = pygame.transform.flip(bendBL, True, False)
        bendTL = pygame.transform.flip(bendBL, False, True)
        bendTR = pygame.transform.flip(bendBR, False, True)

            # Tail
        tailD = pygame.image.load(texturePath + "tail.png").convert_alpha()
        tailD = pygame.transform.scale(tailD, (snakesize, snakesize))
        tailU = pygame.transform.flip(tailD, False, True)
        tailL = pygame.transform.rotate(tailU, 90)
        tailR = pygame.transform.rotate(tailD, 90)

            # Gold Apple
        gapple = pygame.image.load(texturePath + "goldapple.png").convert_alpha()
        gapple = pygame.transform.scale(gapple, (snakesize, snakesize))

            # Apple
        appleTexture = pygame.image.load(texturePath + "apple.png").convert_alpha()
        appleTexture = pygame.transform.scale(appleTexture, (snakesize, snakesize))


                                    #############
                                    # Menu loop #
                                    #############

initTextures()
while menu:

    screen.fill(white)
    displayText("Snake", green, [width / 2, 50])

    fCount += 1

    # Checks for mouse movement
    pos = pygame.mouse.get_pos()
    if not (pos[0] == lastKnowsPos[0] and pos[1] == lastKnowsPos[1]):
        lastKnowsPos = pos
        controller = False

    # Checks to see if mouse is in the window based on x pos
    if not controller:
        if pos[0] > 0 and pos[0] < width - 1 and pos[1] > 0 and pos[1] < height - 1:
            inWindow = True
        else:
            inWindow = False

    # Checks if the mouse is inside the circle
    if pos[0] > centerScreen[0] - 20 and pos[0] < centerScreen[0] + 20 and pos[1] < exitPos[1] + 120 \
            and pos[1] > exitPos[1] + 80 and inWindow:
        pygame.draw.circle(screen, sky_blue, (int(centerScreen[0]), int(exitPos[1] + 100)), 20)

    # Draws the circle for the stats menu
    pygame.draw.circle(screen, black, (int(centerScreen[0]), int(exitPos[1] + 100)), 20, 4)
    displayText("=", black, (int(centerScreen[0]), int(exitPos[1] + 100)), 20)


    # Checks for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit()
            elif event.key == pygame.K_DOWN:
                # Updates the menu object that should be flashing
                for i in range(len(selection)):
                    if selection[i]:
                        selection[i] = False
                        try:
                            selection[i + 1] = True
                        except:
                            selection[0] = True
                        finally:
                            show = False
                            fCount = 0
                            break
            elif event.key == pygame.K_UP:
                # Updates the menu object that should be flashing
                for i in range(len(selection)):
                    if selection[i]:
                        selection[i] = False
                        try:
                            selection[i - 1] = True
                        except:
                            selection[len(selection) - 1] = True
                        finally:
                            show = False
                            fCount = 0
                            break
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if selection[0]:
                    initChallenge()

                    gameInfo["gamesPlayed"] += 1
                    running = True
                    restart()
                elif selection[1]:
                    options = True
                    selection = [True, False, False, False]
                else:
                    quit()
            elif event.key == pygame.K_s:
                stats = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pos[0] > centerScreen[0] - 20 and pos[0] < centerScreen[0] + 20 and pos[1] < exitPos[1] + 120 \
                    and pos[1] > exitPos[1] + 80 and inWindow:
                stats = True

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                for i in range(len(selection)):
                    if selection[i]:
                        selection[i] = False
                        try:
                            selection[i - 1] = True
                        except:
                            selection[len(selection) - 1] = True
                        finally:
                            show = False
                            fCount = 0
                            break
            elif event.button == 1:
                for i in range(len(selection)):
                    if selection[i]:
                        selection[i] = False
                        try:
                            selection[i + 1] = True
                        except:
                            selection[0] = True
                        finally:
                            show = False
                            fCount = 0
                            break
            elif event.button == 11:
                if selection[0]:
                    running = True
                    gameInfo["gamesPlayed"] += 1
                elif selection[1]:
                    options = True
                    selection = [True, False, False, False]
                else:
                    quit()


    # Causes the selected menu option to fade in and out
    if fCount % 10 == 0:
        if show:
            show = False
        else:
            show = True

    displayText("Recreation by Stefan Tobler", black, creditsLocation, 35)

    displayText("Highscore: " + str(hs), black, scoreLocation, 35)


    # Checks to see what menu option should be flashing
    if selection[0]:
        if show:
            displayText("Start Game", black, startGame)

        displayText("Options", black, centerScreen)
        displayText("Exit", black, exitPos)

    elif selection[1]:
        displayText("Start Game", black, startGame)
        if show:
            displayText("Options", black, centerScreen)

        displayText("Exit", black, exitPos)

    elif selection[2]:
        displayText("Start Game", black, startGame)
        displayText("Options", black, centerScreen)

        if show:
            displayText("Exit", black, exitPos)


    # Makes sure the moving text stays on screen
    if scoreLocation[0] < width:
        scoreLocation[0] = scoreLocation[0] + 1
    else:
        scoreLocation[0] = 0

    if creditsLocation[0] > width:
        creditsLocation[0] = 0
    else:
        creditsLocation[0] += 1

    # Updates screen
    pygame.time.wait(15)
    pygame.display.flip()

                                ##############
                                # STATS PAGE #
                                ##############

    while stats:
        screen.fill(white)

        displayText("STATS", black, [width / 2, 50])

        tempTime = gameInfo["timePlayed"]
        try:
            hours = tempTime//3600000
            tempTime -= hours * 3600000
            minutes = tempTime//60000
            tempTime -= minutes * 60000
            seconds = tempTime//1000
        except:
            seconds = 0
            minutes = 0
            hours = 0
        if seconds < 10:
            seconds = "0" + str(seconds)
        if minutes < 10:
            minutes = "0" + str(minutes)
        if hours < 10:
            hours = "0" + str(hours)


        displayText("Time Played: " + str(hours) + ":" + str(minutes) + ":" + str(seconds), black, [centerScreen[0], centerScreen[1] - 200], 35)

        displayText("Games Played: " + str(gameInfo["gamesPlayed"]), black, [centerScreen[0], centerScreen[1] - 150], 35)

        displayText("Apples Eaten: " + str(gameInfo["totalApples"]), black, [centerScreen[0], centerScreen[1] - 100], 35)

        displayText("Apples Per Game: " + str(round(gameInfo["totalApples"]/gameInfo["gamesPlayed"],2)), black, [centerScreen[0], centerScreen[1] - 50], 35)

        displayText("Gold Apples Eaten: " + str(gameInfo["goldApples"]), black, centerScreen, 35)

        displayText("Distance Traveled: " + str(round(gameInfo["distanceTraveled"], 2)) + " kilometers", black, [centerScreen[0], centerScreen[1] + 50], 35)

        displayText("Keys Pressed: " + str(gameInfo["keysPressed"]), black, [centerScreen[0], centerScreen[1] + 100], 35)

        displayText("Bombs Hit: " + str(gameInfo["bombsHit"]), black, [centerScreen[0], centerScreen[1] + 150], 35)

        displayText("Near Misses: " + str(gameInfo["nearMisses"]), black, [centerScreen[0], centerScreen[1] + 200], 35)


        # Checks for mouse movement
        pos = pygame.mouse.get_pos()
        if not (pos[0] == lastKnowsPos[0] and pos[1] == lastKnowsPos[1]):
            lastKnowsPos = pos
            controller = False

        # Checks to see if mouse is in the window based on x pos
        if not controller:
            if pos[0] > 0 and pos[0] < width - 1 and pos[1] > 0 and pos[1] < height - 1:
                inWindow = True
            else:
                inWindow = False

            # Changes color of the boxes when the mouse is over it
            if pos[0] < 100 and pos[1] < 52 and inWindow:
                pygame.draw.rect(screen, red, (0, 0, 100, 52))

        displayText("Back", black, (50, 25), 40)
        pygame.draw.rect(screen, black, (0, 50, 100, 2))
        pygame.draw.rect(screen, black, (100, 0, 2, 52))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
                elif event.key == pygame.K_BACKSPACE:
                    stats = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[0] < 100 and pos[1] < 52 and inWindow:
                    stats = False

        pygame.time.wait(55)
        pygame.display.flip()

                                        ################
                                        # Options loop #
                                        ################

    while options:
        screen.fill(white)

        fCount += 1

        if fCount % 10 == 0:
            if show:
                show = False
            else:
                show = True

        if selection[0]:
            if show:
                displayText("Snakes", black, startGame)

            displayText("Difficulty", black, centerScreen)
            displayText("Challenges", black, exitPos)
            displayText("Back", black, [exitPos[0], exitPos[1] + 100])

        elif selection[1]:
            displayText("Snakes", black, startGame)
            if show:
                displayText("Difficulty", black, centerScreen)

            displayText("Challenges", black, exitPos)
            displayText("Back", black, [exitPos[0], exitPos[1] + 100])


        elif selection[2]:
            displayText("Snakes", black, startGame)
            displayText("Difficulty", black, centerScreen)
            if show:
                displayText("Challenges", black, exitPos)

            displayText("Back", black, [exitPos[0], exitPos[1] + 100])

        elif selection[3]:
            displayText("Snakes", black, startGame)
            displayText("Difficulty", black, centerScreen)
            displayText("Challenges", black, exitPos)
            if show:
                displayText("Back", black, [exitPos[0], exitPos[1] + 100])


        displayText("Options", black, [width / 2, 50])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
                elif event.key == pygame.K_DOWN:
                    # Updates the menu object that should be flashing
                    for i in range(len(selection)):
                        if selection[i]:
                            selection[i] = False
                            try:
                                selection[i + 1] = True
                            except:
                                selection[0] = True
                            finally:
                                show = False
                                fCount = 0
                                break
                elif event.key == pygame.K_UP:
                    # Updates the menu object that should be flashing
                    for i in range(len(selection)):
                        if selection[i]:
                            selection[i] = False
                            try:
                                selection[i - 1] = True
                            except:
                                selection[len(selection)-1] = True
                            finally:
                                show = False
                                fCount = 0
                                break
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if selection[0]:
                        snakes = True
                        selection = getSnakes()
                        getSnakeOpt()
                    elif selection[1]:
                        difficulty = True
                        selection = [True, False, False, False]
                    elif selection[2]:
                        selection = 0
                        fCount = 0
                        challenges = True
                    else:
                        options = False
                        selection = [True, False, False]
                elif event.key == pygame.K_BACKSPACE:
                    options = False
                    selection = [True, False, False]
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    for i in range(len(selection)):
                        if selection[i]:
                            selection[i] = False
                            try:
                                selection[i - 1] = True
                            except:
                                selection[len(selection)-1] = True
                            finally:
                                show = False
                                fCount = 0
                                break
                elif event.button == 1:
                    for i in range(len(selection)):
                        if selection[i]:
                            selection[i] = False
                            try:
                                selection[i + 1] = True
                            except:
                                selection[0] = True
                            finally:
                                show = False
                                fCount = 0
                                break
                elif event.button == 11:
                    if selection[0]:
                        snakes = True
                        selection = getSnakes()
                        getSnakeOpt()
                    elif selection[1]:
                        difficulty = True
                        selection = [True, False, False, False]
                    elif selection[2]:
                        challenges = True
                    else:
                        options = False
                        selection = [True, False, False]
                elif event.button == 12:
                    options = False
                    selection = [True, False, False]

        pygame.time.wait(15)
        pygame.display.flip()


                                    #############################
                                    # Change Snake Texture Menu #
                                    #############################
        while snakes:
            screen.fill(white)

            displayText("Snakes", black, [width / 2, 50])

            # Checks for mouse movement
            pos = pygame.mouse.get_pos()
            if not (pos[0] == lastKnowsPos[0] and pos[1] == lastKnowsPos[1]):
                lastKnowsPos = pos
                controller = False

            # Checks to see if mouse is in the window based on x pos
            if not controller:
                if pos[0] > 0 and pos[0] < width - 1 and pos[1] > 0 and pos[1] < height - 1:
                    inWindow = True
                else:
                    inWindow = False

                # Changes color of the boxes when the mouse is over it
                if pos[0] < 100 and pos[1] < 52 and inWindow:
                    pygame.draw.rect(screen, red, (0,0,100,52))

            # Checks to see if the game should be displaying a normal image or animation
            if rate >= width/2 + 6 * snakesize:
                skinPreviews[current].show()
                if gameInfo[skins[current]]:
                    skinPreviews[current].showInfo()
                else:
                    skinPreviews[current].showUnlock()
                    screen.blit(lock, (width/2 - 2 * snakesize, height/2 - 2 * snakesize))
                if skins[current] == gameInfo["texture"]:
                    displayText("Selected", red, [width/2, height - 50])

            elif rate >= width/2 + 6 * snakesize - animation_speed and rate < width/2 + 6 * snakesize:

                # Checks for which new preview should be displayed to the screen
                if direction == "left":
                    if current < len(skinPreviews) - 1:
                        current += 1
                    else:
                        current = 0
                elif direction == "right":
                    if current > 0:
                        current -= 1
                    else:
                        current = len(skinPreviews) - 1

                skinPreviews[current].show()
                if gameInfo[skins[current]]:
                    skinPreviews[current].showInfo()
                else:
                    skinPreviews[current].showUnlock()
                    screen.blit(lock, (width / 2 - 2 * snakesize, height / 2 - 2 * snakesize))

                rate += animation_speed

            # Animation statement
            else:
                if direction == "left":
                    animate("left", rate)
                    rate += animation_speed

                elif direction == "right":
                    animate("right", rate)
                    rate += animation_speed

                else:
                    error.write("ANIMATION DIRECTION ERROR: Error found in animation direction. Direction should either be left or right.")


            displayText("Back", black, (50,25), 40)
            pygame.draw.rect(screen, black, (0,50,100,2))
            pygame.draw.rect(screen, black, (100,0,2,52))

            screen.blit(arrowLeft, (0, height/2 - (3*snakesize)/2))
            screen.blit(arrowRight, (width - 3 * snakesize, height/2 - (3*snakesize)/2))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    click.play()
                    # If player clicks in the back box then the snake menu will end
                    if pos[0] < 100 and pos[1] < 52 and inWindow:
                        snakes = False
                        selection = [True, False, False, False]
                        current = 0
                    elif pos[0] <  3 * snakesize and pos[1] > height/2 - (3*snakesize)/2 and pos[1] < height/2 + (3*snakesize)/2 and inWindow:
                        rate = 0
                        direction = "right"
                    elif pos[0] > width - 3 * snakesize and pos[1] > height / 2 - (3 * snakesize) / 2 and pos[1] < height / 2 + (3 * snakesize) / 2 and inWindow:
                        rate = 0
                        direction = "left"
                    elif pos[0] > width/2 - 2 * snakesize and pos[0] < width/2 + 2 * snakesize and pos[1] > height/2 - 2 * snakesize and pos[1] < height/2 + 2 * snakesize and inWindow:
                        if gameInfo[skins[current]]:
                            gameInfo["texture"] = skins[current]
                            initTextures()
                        else:
                            displayText("LOCKED", red, centerScreen)
                            locked = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    elif event.key == pygame.K_RIGHT:
                        # Updates which snake skin should be displayed
                        rate = 0
                        direction = "left"


                    elif event.key == pygame.K_LEFT:
                        # Updates which snake skin should be displayed
                        rate = 0
                        direction = "right"

                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if gameInfo[skins[current]]:
                            gameInfo["texture"] = skins[current]
                            initTextures()
                        else:
                            displayText("LOCKED", red, centerScreen)
                            locked = True
                    elif event.key == pygame.K_BACKSPACE:
                        snakes = False
                        selection = [True, False, False, False]
                        current = 0

                elif event.type == pygame.JOYBUTTONDOWN:
                    controller = True
                    if event.button == 2:
                        # Updates which snake skin should be displayed
                        rate = 0
                        direction = "right"

                    elif event.button == 3:
                        rate = 0
                        direction = "left"

                    elif event.button == 11:
                        if gameInfo[skins[current]]:
                            gameInfo["texture"] = skins[current]
                            initTextures()
                        else:
                            displayText("LOCKED", red, centerScreen)
                            locked = True
                    elif event.button == 12:
                        snakes = False
                        selection = [True, False, False, False]
                        current = 0

            # Fast refresh rate if animation is running and slower more efficent refresh for non animation phase
            if rate < width/2 + 6 * snakesize:
                pygame.time.wait(1)
                pygame.display.flip()
            else:
                pygame.display.flip()
                if locked:
                    pygame.time.wait(500)
                    locked = False
                else:
                    pygame.time.wait(15)

                                        ###################
                                        # DIFFICULTY MENU #
                                        ###################
        while difficulty:

            screen.fill(white)

            fCount += 1

            if fCount % 10 == 0:
                if show:
                    show = False
                else:
                    show = True

            displayText("Difficulty", black, [width / 2, 50])


            # Determines which element is flashing
            if selection[0]:
                if show:
                    displayText("Easy", black, startGame)

                displayText("Moderate", black, centerScreen)
                displayText("Hard", black, exitPos)
                displayText("Back", black, [centerScreen[0], centerScreen[1] + 200])

            elif selection[1]:
                displayText("Easy", black, startGame)
                if show:
                    displayText("Moderate", black, centerScreen)

                displayText("Hard", black, exitPos)
                displayText("Back", black, [centerScreen[0], centerScreen[1] + 200])

            elif selection[2]:
                displayText("Easy", black, startGame)
                displayText("Moderate", black, centerScreen)
                if show:
                    displayText("Hard", black, exitPos)

                displayText("Back", black, [centerScreen[0], centerScreen[1] + 200])

            elif selection[3]:
                displayText("Easy", black, startGame)
                displayText("Moderate", black, centerScreen)
                displayText("Hard", black, exitPos)
                if show:
                    displayText("Back", black, [centerScreen[0], centerScreen[1] + 200])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: #or (event.button):
                        quit()
                    elif event.key == pygame.K_DOWN:
                        # Updates the menu object that should be flashing
                        for i in range(len(selection)):
                            if selection[i]:
                                selection[i] = False
                                try:
                                    selection[i + 1] = True
                                except:
                                    selection[0] = True
                                finally:
                                    show = False
                                    fCount = 0
                                    break
                    elif event.key == pygame.K_UP:
                        # Updates the menu object that should be flashing
                        for i in range(len(selection)):
                            if selection[i]:
                                selection[i] = False
                                try:
                                    selection[i - 1] = True
                                except:
                                    selection[len(selection) - 1] = True
                                finally:
                                    show = False
                                    fCount = 0
                                    break

                    # Returns "Game Updated" on the screen and changes the delay per frame
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if selection[0]:
                            screen.fill(white)
                            displayText("Game Updated", red, centerScreen, 75)
                            updateDifficulty("easy")
                            pygame.display.flip()
                            pygame.time.wait(1000)
                        elif selection[1]:
                            screen.fill(white)
                            displayText("Game Updated", red, centerScreen, 75)
                            updateDifficulty("moderate")
                            pygame.display.flip()
                            pygame.time.wait(1000)
                        elif selection[2]:
                            screen.fill(white)
                            displayText("Game Updated", red, centerScreen, 75)
                            updateDifficulty("hard")
                            pygame.display.flip()
                            pygame.time.wait(1000)
                        else:
                            difficulty = False
                            selection = [True, False, False, False]
                    elif event.key == pygame.K_BACKSPACE:
                        difficulty = False
                        selection = [True, False, False, False]

                # Checks for controller input
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        # Moves through which menu item is selected
                        for i in range(len(selection)):
                            if selection[i]:
                                selection[i] = False
                                try:
                                    selection[i - 1] = True
                                except:
                                    selection[3] = True
                                finally:
                                    show = False
                                    fCount = 0
                    elif event.button == 1:
                        for i in range(len(selection)):
                            if selection[i]:
                                selection[i] = False
                                try:
                                    selection[i + 1] = True
                                except:
                                    selection[0] = True
                                finally:
                                    show = False
                                    fCount = 0
                                    break
                    elif event.button == 11:
                        if selection[0]:
                            screen.fill(white)
                            displayText("Game Updated", red, centerScreen, 75)
                            gameSpeed = 75
                            pygame.display.flip()
                            pygame.time.wait(1000)
                        elif selection[1]:
                            screen.fill(white)
                            displayText("Game Updated", red, centerScreen, 75)
                            gameSpeed = 55
                            pygame.display.flip()
                            pygame.time.wait(1000)
                        elif selection[2]:
                            screen.fill(white)
                            displayText("Game Updated", red, centerScreen, 75)
                            gameSpeed = 40
                            pygame.display.flip()
                            pygame.time.wait(1000)
                        else:
                            difficulty = False
                            selection = [True, False, False, False]
                    elif event.button == 12:
                        difficulty = False
                        selection = [True, False, False, False]

            pygame.time.wait(15)
            pygame.display.flip()


                                    ##################
                                    # Challenge Menu #
                                    ##################
        while challenges:
            screen.fill(white)
            displayText("Challenges", black, [width / 2, 50])

            # Frame count to enable blinking text
            fCount += 1
            if fCount % 10 == 0:
                if show:
                    show = False
                else:
                    show = True

            # Adds the avaliable challengses to the screen.
            tempDistance = 0
            for key, value in activeChallenges.items():
                if key == challengeList[selection]:
                    if show:
                        displayText(key.title() + " : " + str(value), black, [width / 2, 150 + tempDistance], 35)
                else:
                    displayText(key.title() + " : " + str(value), black, [width/2, 150 + tempDistance], 35)
                tempDistance += 50

            # Checks to see if the option is "Back" so that the player is taken back to the options menu
            if challengeList[selection] == "Back":
                if show:
                    displayText("Back", black, [width/2, 150 + tempDistance], 35)
            else:
                displayText("Back", black, [width / 2, 150 + tempDistance], 35)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    elif event.key == pygame.K_DOWN:
                        # Moves the index of selection up one
                        if selection < len(challengeList):
                            selection += 1
                        else:
                            selection = 0

                        fCount = 0

                    elif event.key == pygame.K_UP:

                        # Moves the selection of the index down one
                        if selection > 0:
                            selection -= 1
                        else:
                            selection = len(challengeList) - 1

                        fCount = 0

                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if challengeList[selection] == "Back":
                            # Updates gameInfo so that the active challenges are saved
                            temp = ""
                            for key, value in activeChallenges.items():
                                temp += key + ":" + str(value) + " ; "

                            gameInfo["challenges"] = temp

                            challenges = False
                            fCount = 0
                            selection = [True, False, False, False]
                        else:
                            if activeChallenges[challengeList[selection]]:
                                activeChallenges[challengeList[selection]] = False
                            else:
                                activeChallenges[challengeList[selection]] = True
                    elif event.key == pygame.K_BACKSPACE:
                        # Updates gameInfo so that the active challenges are saved
                        temp = ""
                        for key,value in activeChallenges.items():
                            temp += key + ":" + str(value) + " ; "

                        gameInfo["challenges"] = temp

                        challenges = False
                        fCount = 0
                        selection = [True, False, False, False]

                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:

                        # Moves the selection of the index down one
                        if selection > 0:
                            selection -= 1
                        else:
                            selection = len(challengeList) - 1

                        fCount = 0

                    elif event.button == 1:

                        # Moves the index of selection up one
                        if selection < len(challengeList):
                            selection += 1
                        else:
                            selection = 0

                        fCount = 0

                    elif event.button == 11:

                        if challengeList[selection] == "Back":
                            # Updates gameInfo so that the active challenges are saved
                            temp = ""
                            for key, value in activeChallenges.items():
                                temp += key + ":" + str(value) + " ; "

                            gameInfo["challenges"] = temp

                            challenges = False
                            fCount = 0
                            selection = [True, False, False, False]
                        else:
                            if activeChallenges[challengeList[selection]]:
                                activeChallenges[challengeList[selection]] = False
                            else:
                                activeChallenges[challengeList[selection]] = True
                    elif event.key == pygame.K_BACKSPACE:
                        # Updates gameInfo so that the active challenges are saved
                        temp = ""
                        for key, value in activeChallenges.items():
                            temp += key + ":" + str(value) + " ; "

                        gameInfo["challenges"] = temp

                        challenges = False
                        fCount = 0
                        selection = [True, False, False, False]

                    elif event.button == 12:
                        # Updates gameInfo so that the active challenges are saved
                        temp = ""
                        for key, value in activeChallenges.items():
                            temp += key + ":" + str(value) + " ; "

                        gameInfo["challenges"] = temp

                        challenges = False
                        fCount = 0
                        selection = [True, False, False, False]




            pygame.time.wait(15)
            pygame.display.flip()



                            ##################
                            # Main game loop #
                            ##################
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    gameInfo["keysPressed"] += 1

                if event.key == pygame.K_ESCAPE:
                    quit()
                if event.key == pygame.K_UP:
                    yVelocity = -snakesize
                    xVelocity = 0
                elif event.key == pygame.K_DOWN:
                    yVelocity = snakesize
                    xVelocity = 0
                elif event.key == pygame.K_RIGHT:
                    yVelocity = 0
                    xVelocity = snakesize
                elif event.key == pygame.K_LEFT:
                    yVelocity = 0
                    xVelocity = -snakesize
                elif event.key == pygame.K_p:
                    pause()

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    yVelocity = -snakesize
                    xVelocity = 0
                elif event.button == 1:
                    yVelocity = snakesize
                    xVelocity = 0
                elif event.button == 2:
                    yVelocity = 0
                    xVelocity = -snakesize
                elif event.button == 3:
                    yVelocity = 0
                    xVelocity = snakesize

        screen.fill(white)

        displayText(str(score), (211, 211, 211), centerScreen, int((width + height)/2 * .35))

        # Draws the apples
        for i in range(len(apples) - 1, -1, -1):

            # Checks for snake is eating the apple.
            if snakeBody[0].x == apples[i].x and snakeBody[0].y == apples[i].y:

                gameInfo["totalApples"] += 1

                score += 1
                applecords = newApple()

                # Adds a new part to snake
                if len(snakeBody) == 1:
                        snake = Body(snakeBody[0].x - xVelocity, snakeBody[0].y - yVelocity)
                        snakeBody.append(snake)
                else:
                    snake = Body()
                    snakeBody.append(snake)

                # Checks to make sure that the apple is not spawned on a part of the snake
                for part in snakeBody:
                    if part.x == applecords[0] and part.y == applecords[1]:
                        applecords = newApple()

                apples[i].x = applecords[0]
                apples[i].y = applecords[1]

                if len(apples) > 1:
                    apples.remove(apples[i])
                    continue

                # Algorithm to see if two apples show up.
                if random.random() < doubleChance:
                    a = Body(newApple()[0], newApple()[1])
                    apples.append(a)
                    screen.blit(appleTexture, (apples[-1].x, apples[-1].y))

                # Algorithm to see if a golden apple will appear.
                if random.random() < goldAppleChance:
                    goldApple.append(newApple())

                # Adds a bomb to the screen if the bomb challenge is selected
                if activeChallenges["bombs"]:
                    if random.random() < bombChance:
                        temp = Body(newApple()[0], newApple()[1])
                        bombs.append(temp)

            screen.blit(appleTexture, (apples[i].x, apples[i].y))

        # Draws Gold Apple
        if len(goldApple) > 0:
            for pos in goldApple:
                screen.blit(gapple, pos)
                if snakeBody[0].x == pos[0] and snakeBody[0].y == pos[1]:
                    gameInfo["goldApples"] += 1
                    increment = 0
                    score += 5
                    for i in range(5):
                        snake = Body(x= -(8 * snakesize) + increment, y=height - 1)
                        increment += snakesize
                        snakeBody.append(snake)
                    goldApple.remove(pos)

        # Blits th bombs to the screen and checks for collisions
        if activeChallenges['bombs']:
            for i in range(len(bombs) - 1, -1, -1):
                if snakeBody[0].x == bombs[i].x and snakeBody[0].y == bombs[i].y:
                    lost = True
                    gameInfo["bombsHit"] += 1

                elif (abs(snakeBody[0].x - bombs[i].x) == snakesize and snakeBody[0].y == bombs[i].y) \
                    or (abs(snakeBody[0].y - bombs[i].y) == snakesize  and snakeBody[0].x == bombs[i].x):
                    if not nearmiss:
                        nearmiss = True
                    elif nearmiss and not lost:
                        gameInfo["nearMisses"] += 1
                    else:
                        nearmiss = False

                # Puts the texture on the screen. If it fails there will be a log in the error log.
                try:
                    screen.blit(bomb, (bombs[i].x, bombs[i].y))
                except:
                    error.write("BOMB BLIT ERROR: Texture not initalized\n")

        # Update snake
        for i in range(len(snakeBody)-1, 0, -1):
            snakeBody[i].x = snakeBody[i - 1].x
            snakeBody[i].y = snakeBody[i - 1].y

        snakeBody[0].x += xVelocity
        snakeBody[0].y += yVelocity


        # Checks to see if walls are active and then draws them and reworks the bounds so that if the snake
        # runs into a wall the gane ends
        if activeChallenges["walls"] or (activeChallenges["Top Bottom Walls"] and activeChallenges["Side Walls"]):

            # Blits the brick wall textures to the screen.
            for cordIncrement in range(0, height, snakesize):
                screen.blit(brickWall, (0, cordIncrement))
                screen.blit(brickWall, (width - snakesize, cordIncrement))

            for cordIncrement in range(0, width, snakesize):
                screen.blit(brickWall, (cordIncrement, 0))
                screen.blit(brickWall, (cordIncrement, height - snakesize))

            for i in snakeBody:
                if i.x >= -(8 * snakesize) and i.x < -snakesize - 1:
                    pass
                elif i.x < snakesize:
                    lost = True
                elif i.x >= width - snakesize:
                    lost = True
                if i.y < snakesize:
                    lost = True
                elif i.y >= height - snakesize:
                    lost = True

        elif activeChallenges["Top Bottom Walls"]:

            for cordIncrement in range(0, width, snakesize):
                screen.blit(brickWall, (cordIncrement, 0))
                screen.blit(brickWall, (cordIncrement, height - snakesize))

            for i in snakeBody:
                if i.x >= -(8 * snakesize) and i.x < -snakesize - 1:
                    pass
                elif i.x < 0:
                    i.x = width - snakesize
                elif i.x >= width:
                    i.x = 0
                if i.y < snakesize:
                    lost = True
                elif i.y >= height - snakesize:
                    lost = True

        elif activeChallenges["Side Walls"]:

            for cordIncrement in range(0, height, snakesize):
                screen.blit(brickWall, (0, cordIncrement))
                screen.blit(brickWall, (width - snakesize, cordIncrement))


            for i in snakeBody:
                if i.x >= -(8 * snakesize) and i.x < -snakesize - 1:
                    pass
                elif i.x < snakesize:
                    lost = True
                elif i.x >= width - snakesize:
                    lost = True
                if i.y < 0:
                    i.y = height - snakesize
                elif i.y >= height:
                    i.y = 0

        else:
            for i in snakeBody:
                if i.x >= -(8 * snakesize) and i.x < -snakesize - 1:
                    pass
                elif i.x < 0:
                    i.x = width - snakesize
                elif i.x >= width:
                    i.x = 0
                if i.y < 0:
                    i.y = height - snakesize
                elif i.y >= height:
                    i.y = 0

        # Draws the snake
        for i in range(len(snakeBody)-1, -1, -1):
            # Draws the body with textures
            if i != 0:

                # If i is the last element in the list blit tail image
                if i == len(snakeBody)-1:
                    if (snakeBody[i].x - snakeBody[i-1].x < 0 and snakeBody[i].x - snakeBody[i-1].x > snakesize - width and not(snakeBody[i].x == width - snakesize)) \
                            or (snakeBody[i].x == width - snakesize and snakeBody[i].x - snakeBody[i-1].x > 0) and abs(snakeBody[i].x - snakeBody[i-1].x) != 50:
                        screen.blit(tailL, (snakeBody[i].x, snakeBody[i].y))

                    elif snakeBody[i].x - snakeBody[i-1].x > 0 or (snakeBody[i].x == 0 and snakeBody[i].x - snakeBody[i-1].x < 0):
                        screen.blit(tailR, (snakeBody[i].x, snakeBody[i].y))

                    elif (snakeBody[i].y - snakeBody[i-1].y < 0 and snakeBody[i].y - snakeBody[i-1].y > snakesize - height and not(snakeBody[i].y == height - snakesize)) \
                            or (snakeBody[i].y == height - snakesize and snakeBody[i].y - snakeBody[i-1].y > 0 and abs(snakeBody[i].y - snakeBody[i-1].y) != 50):
                        screen.blit(tailU, (snakeBody[i].x, snakeBody[i].y))

                    else:
                        screen.blit(tailD, (snakeBody[i].x, snakeBody[i].y))

                # Checks body part to the left and right to know if the snake is vertical
                elif snakeBody[i].x == snakeBody[i-1].x and snakeBody[i].x == snakeBody[i+1].x:
                    screen.blit(bodyUD, (snakeBody[i].x, snakeBody[i].y))

                # Checks body part to the left and right to know if the snake is horizontal
                elif snakeBody[i].y == snakeBody[i-1].y and snakeBody[i].y == snakeBody[i+1].y:
                    screen.blit(bodyLR, (snakeBody[i].x, snakeBody[i].y))

                # Since no other cases were true assumes there is a bend in the snake
                else:
                    if i < len(snakeBody)-1:
                        if (snakeBody[i].x > snakeBody[i-1].x and snakeBody[i].y < snakeBody[i+1].y) or (snakeBody[i].y < snakeBody[i-1].y and snakeBody[i].x > snakeBody[i+1].x):
                            screen.blit(bendTR, (snakeBody[i].x, snakeBody[i].y))

                        elif(snakeBody[i].y > snakeBody[i-1].y and snakeBody[i].x < snakeBody[i+1].x) or (snakeBody[i].x < snakeBody[i-1].x and snakeBody[i].y > snakeBody[i+1].y):
                            screen.blit(bendBL, (snakeBody[i].x, snakeBody[i].y))

                        elif(snakeBody[i].x > snakeBody[i-1].x and snakeBody[i].y > snakeBody[i+1].y) or (snakeBody[i].y > snakeBody[i-1].y and snakeBody[i].x > snakeBody[i+1].x):
                            screen.blit(bendBR, (snakeBody[i].x, snakeBody[i].y))

                        else:
                            screen.blit(bendTL, (snakeBody[i].x, snakeBody[i].y))

            # Draws the snakes head with the head texture
            else:

                if yVelocity > 0:
                    screen.blit(headD, (snakeBody[i].x, snakeBody[i].y))

                elif xVelocity != 0:
                    if xVelocity > 0:
                        screen.blit(headR, (snakeBody[i].x, snakeBody[i].y))
                    else:
                        screen.blit(headL, (snakeBody[i].x, snakeBody[i].y))
                else:
                    screen.blit(head, (snakeBody[i].x, snakeBody[i].y))

        # Checks for snake on snake collision
        if not lost:
            lost = checkCollision(snakeBody)

        if lost:
            if gameOpen != None:
                updateAchievements()
            saveGame(gameOpen)

        # Updates display
        if not lost:
            pygame.display.flip()
            pygame.time.wait(gameSpeed)

            gameInfo["distanceTraveled"] += .0001

            if gameInfo["difficulty"] == "moderate":
                gameInfo["timePlayed"] += int(gameSpeed * 1.8)
            elif gameInfo["difficulty"] == "easy":
                gameInfo["timePlayed"] += int(gameSpeed * 1.5)
            elif gameInfo["difficulty"] == "hard":
                gameInfo["timePlayed"] += int(gameSpeed * 2.1)





                                        #############
                                        # Lost loop #
                                        #############

        while lost:
            screen.fill(white)
            displayText("You lost!", red, centerScreen, 75)
            displayText("Score: " + str(score), red, [centerScreen[0], centerScreen[1] + 60])
            displayText("Press enter to play again or esc to exit.", black, [centerScreen[0], height - 40], 35)
            displayText("Press M to go back to the menu.", black, [centerScreen[0], height - 80], 35)

            # Checks if the score is the new highscore
            if score > hs:
                gameInfo["highscore"] = score
                hs = score

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    updateAchievements()
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        restart()
                        gameInfo["gamesPlayed"] += 1
                    elif event.key == pygame.K_m:
                        restart()
                        running = False

            pygame.display.flip()
if gameOpen != None:
    updateAchievements()
saveGame(gameOpen)
error.close()

# When all loops are exited game quits
pygame.quit()
os._exit(1)