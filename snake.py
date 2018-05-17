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
width = 800
height = 800

# Making some color variables so that they are easy to call
white = (255, 255, 255)
sky_blue = (18,178,238,100)
black = (0, 0, 0)
red = (255, 0, 0)
green = (34, 145, 20)
gold = (255, 215, 0)

centerScreen = [width/2, height/2]

# Initilizing the screen
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
    global width, height
    ax = random.randrange(0, width, snakesize)
    ay = random.randrange(0, height, snakesize)
    for part in snakeBody:
        if part.x == ax and part.y == ay:
            newApple()
    return (ax, ay)

# Opens error file so that if inconsistencies are found they will be printed to a log
error = open("Read Me{}error log.txt".format(osType), "a")
date = str(datetime.datetime.now())
error.write("\n" + date + "\n")

# Initilizes the first apple
applecords = newApple()

ax = applecords[0]
ay = applecords[1]

apple = Body(ax, ay)
apples = [apple]
goldApple = []

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
snakes = False
running = False
lost = False

# Sets all the game loop variables to false. Forces the game to quit
def quit():
    global saveScreen, menu, loaded, options, difficulty, snakes, running, lost
    saveScreen = False
    menu = False
    loaded = False
    options = False
    difficulty = False
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

# Restarts all the game variables
def restart():
    global lost, score, snakeBody, xVelocity, yVelocity, goldApple, apples
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

# Loads in game file
def loadGame(file, seconds = 1):
    global loaded, saveScreen, menu, scoreText, gameInfo, gameOpen, hs, skins
    # Loads saves into a dictionary
    gameSave = open("saves{}".format(osType) + file + ".txt", "r")

    for line in gameSave:
        tempTup = line.strip().split(" = ")
        if tempTup[0] not in gameInfo:
            gameInfo[tempTup[0]] = tempTup[1]

    # Corrects variable types in the dictionary
    for key, value in gameInfo.items():
        try:
            gameInfo[key] = int(value)

        except:
            pass

        if value == "True":
            gameInfo[key] = True
        elif value == "False":
            gameInfo[key] = False


    # Creates a list of all the avaliable texture names
    skins = gameInfo["avaliableSkins"].split(",")
    # skins = dict.fromkeys(keys)


    # Imports the highscore
    hs = int(gameInfo["highscore"])
    scoreText = "Highscore: " + str(gameInfo["highscore"])

    gameSave.close()
    gameOpen = file

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

    # Sets the preview to a pygame image
    def setPreview(self, img):
        if type(img) == pygame.Surface:
            self.preview = img
        else:
            error.write("PREVIEW ERROR: Preview must be a pygame.Surface object\n")



    # Blits the skin preview in the middle of the screen
    def show(self):
        screen.blit(self.preview, (width/2 - 2 * snakesize, height/2 - 2 * snakesize))

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
    global lock, arrowLeft, arrowRight, classic


    lock = pygame.image.load("textures{}options{}snakes{}lockalpha.png".format(osType,osType,osType)).convert_alpha()
    lock = pygame.transform.scale(lock, (4 * snakesize, 4 * snakesize))


    arrowLeft = pygame.image.load("textures{}options{}snakes{}arrow.png".format(osType,osType,osType)).convert()
    arrowLeft = pygame.transform.scale(arrowLeft, (3*snakesize, 3*snakesize))
    arrowRight = pygame.transform.flip(arrowLeft, True, False)

    # Format Line for the addition of future textures
    # Make sure each texture is added in the same order that it is added in the list on avaliableSkins
    # previewnamePreview = pygame.image.load("textures{}options{}snakes{}previewname.png".format(osType,osType,osType)).convert_alpha()
    # previewnamePreview = pygame.transform.scale(previewname, (4*snakesize, 4*snakesize))
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

# Position for skinPreviews list to display
current = 0

# Animates the skin previews to move off the screen and the new one onto the screen
def animate(direction):
    global current, skinPreviews
    direction = direction.lower()
    if direction == "left":
        for i in range(0, int(width/2 + 6 * snakesize), int(snakesize/10)):
            screen.fill(white)
            if current < len(skinPreviews) - 1:
                screen.blit(skinPreviews[current].preview, (width/2 - 2 * snakesize - i, height/2 - 2 * snakesize))
                screen.blit(skinPreviews[current + 1].preview, (width + 4 * snakesize - i, height/2 - 2 * snakesize))
            else:
                screen.blit(skinPreviews[current].preview, (width / 2 - 2 * snakesize - i, height / 2 - 2 * snakesize))
                screen.blit(skinPreviews[0].preview, (width + 4 * snakesize - i, height / 2 - 2 * snakesize))

            displayText("Back", black, (50, 25), 40)
            pygame.draw.rect(screen, black, (0, 50, 100, 2))
            pygame.draw.rect(screen, black, (100, 0, 2, 52))

            screen.blit(arrowLeft, (0, height / 2 - (3 * snakesize) / 2))
            screen.blit(arrowRight, (width - 3 * snakesize, height / 2 - (3 * snakesize) / 2))

            pygame.time.wait(1)
            pygame.display.flip()

    elif direction == "right":
        for i in range(0, int(width/2 + 6 * snakesize), int(snakesize/10)):
            screen.fill(white)
            if current > 0:
                screen.blit(skinPreviews[current].preview, (width/2 - 2 * snakesize + i, height/2 - 2 * snakesize))
                screen.blit(skinPreviews[current-1].preview, (-8 * snakesize, height/2 - 2 * snakesize))
            else:
                screen.blit(skinPreviews[current].preview, (width / 2 - 2 * snakesize + i, height / 2 - 2 * snakesize))
                screen.blit(skinPreviews[len(skinPreviews) - 1].preview, (-8 * snakesize, height / 2 - 2 * snakesize))

            displayText("Back", black, (50, 25), 40)
            pygame.draw.rect(screen, black, (0, 50, 100, 2))
            pygame.draw.rect(screen, black, (100, 0, 2, 52))

            screen.blit(arrowLeft, (0, height / 2 - (3 * snakesize) / 2))
            screen.blit(arrowRight, (width - 3 * snakesize, height / 2 - (3 * snakesize) / 2))

            pygame.time.wait(1)
            pygame.display.flip()
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
if gameOpen != None:
    texturePath = "textures{}".format(osType)+ gameInfo["texture"]+ "{}".format(osType)

    ######################
    # Initalize Textures #
    ######################
        # Heads
    head = pygame.image.load(texturePath + "head.png").convert()
    head = pygame.transform.scale(head, (snakesize, snakesize))
    headL = pygame.transform.rotate(head, 90)
    headR = pygame.transform.rotate(head, -90)
    headD = pygame.transform.flip(head, False, True)

        # Body
    bodyUD = pygame.image.load(texturePath + "body.png").convert()
    bodyUD = pygame.transform.scale(bodyUD, (snakesize, snakesize))
    bodyLR = pygame.transform.rotate(bodyUD, 90)

        # Bend
    bendBL = pygame.image.load(texturePath + "bend.png").convert()
    bendBL = pygame.transform.scale(bendBL, (snakesize, snakesize))
    bendBR = pygame.transform.flip(bendBL, True, False)
    bendTL = pygame.transform.flip(bendBL, False, True)
    bendTR = pygame.transform.flip(bendBR, False, True)

        # Tail
    tailD = pygame.image.load(texturePath + "tail.png").convert()
    tailD = pygame.transform.scale(tailD, (snakesize, snakesize))
    tailU = pygame.transform.flip(tailD, False, True)
    tailL = pygame.transform.rotate(tailU, 90)
    tailR = pygame.transform.rotate(tailD, 90)

        # Gold Apple
    gapple = pygame.image.load(texturePath + "goldapple.png").convert()
    gapple = pygame.transform.scale(gapple, (snakesize, snakesize))

        # Apple
    appleTexture = pygame.image.load(texturePath + "apple.png").convert()
    appleTexture = pygame.transform.scale(appleTexture, (snakesize, snakesize))


                                    #############
                                    # Menu loop #
                                    #############


while menu:

    screen.fill(white)
    displayText("Snake", green, [width / 2, 50])

    fCount += 1

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
                            selection[2] = True
                        finally:
                            show = False
                            fCount = 0
                            break
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if selection[0]:
                    gameInfo["gamesPlayed"] += 1
                    running = True
                elif selection[1]:
                    options = True
                    selection = [True, False, False]
                else:
                    quit()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                for i in range(len(selection)):
                    if selection[i]:
                        selection[i] = False
                        try:
                            selection[i - 1] = True
                        except:
                            selection[2] = True
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
                    selection = [True, False, False]
                else:
                    quit()


    # Causes the selected menu option to fade in and out
    if fCount % 10 == 0:
        if show:
            show = False
        else:
            show = True

    displayText("Recreation by Stefan Tobler", black, creditsLocation, 35)

    displayText(scoreText, black, scoreLocation, 35)

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
            displayText("Back", black, exitPos)

        elif selection[1]:
            displayText("Snakes", black, startGame)
            if show:
                displayText("Difficulty", black, centerScreen)

            displayText("Back", black, exitPos)

        elif selection[2]:
            displayText("Snakes", black, startGame)
            displayText("Difficulty", black, centerScreen)

            if show:
                displayText("Back", black, exitPos)

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
                                selection[2] = True
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
                    else:
                        options = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    for i in range(len(selection)):
                        if selection[i]:
                            selection[i] = False
                            try:
                                selection[i - 1] = True
                            except:
                                selection[2] = True
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
                    else:
                        options = False

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

            displayText("Back", black, (50,25), 40)
            pygame.draw.rect(screen, black, (0,50,100,2))
            pygame.draw.rect(screen, black, (100,0,2,52))

            screen.blit(arrowLeft, (0, height/2 - (3*snakesize)/2))
            screen.blit(arrowRight, (width - 3 * snakesize, height/2 - (3*snakesize)/2))

            skinPreviews[current].show()
            if gameInfo[skins[current]]:
                skinPreviews[current].showInfo()
            else:
                skinPreviews[current].showUnlock()
                screen.blit(lock, (width/2 - 2 * snakesize, height/2 - 2 * snakesize))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    click.play()
                    # If player clicks in the back box then the snake menu will end
                    if pos[0] < 100 and pos[1] < 52 and inWindow:
                        snakes = False
                        selection = [True, False, False]
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    elif event.key == pygame.K_RIGHT:
                        # Updates which snake skin should be displayed
                        if current < len(skinPreviews) - 1:
                            animate("left")
                            current += 1
                        else:
                            animate("left")
                            current = 0

                    elif event.key == pygame.K_LEFT:
                        # Updates which snake skin should be displayed
                        if current > 0:
                            animate("right")
                            current -= 1
                        else:
                            animate("right")
                            current = len(skinPreviews)

                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if selection[0]:
                            pass
                        elif selection[1]:
                            pass
                        else:
                            snakes = False
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 2:
                        # Updates which snake skin should be displayed
                        if current > 0:
                            animate("right")
                            current -= 1
                        else:
                            animate("right")
                            current = len(skinPreviews)

                    elif event.button == 3:
                        if current < len(skinPreviews) - 1:
                            animate("left")
                            current += 1
                        else:
                            animate("left")
                            current = 0

                    elif event.button == 11:
                        if selection[0]:
                            pass
                        elif selection[1]:
                            pass
                        else:
                            snakes = False


            pygame.time.wait(11)
            pygame.display.flip()

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
                                    selection[3] = True
                                finally:
                                    show = False
                                    fCount = 0
                                    break
                    # Returns "Game Updated" on the screen and changes the delay per frame
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
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
                            selection = [True, False, False]

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
                            selection = [True, False, False]

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

        # Draws the apples
        for i in range(len(apples) - 1, -1, -1):

            # Checks for snake is eating the apple.
            if snakeBody[0].x == apples[i].x and snakeBody[0].y == apples[i].y:

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

                if random.random() < doubleChance:
                    a = Body(newApple()[0], newApple()[1])
                    apples.append(a)
                    screen.blit(appleTexture, (apples[-1].x, apples[-1].y))

                if random.random() < goldAppleChance:
                    goldApple.append(newApple())

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
                        snake = Body(x=increment, y=height - 1)
                        increment += snakesize
                        snakeBody.append(snake)
                    goldApple.remove(pos)

        # Update snake
        for i in range(len(snakeBody)-1, 0, -1):
            snakeBody[i].x = snakeBody[i - 1].x
            snakeBody[i].y = snakeBody[i - 1].y

        snakeBody[0].x += xVelocity
        snakeBody[0].y += yVelocity

        for i in snakeBody:
            if i.x < 0:
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
        lost = checkCollision(snakeBody)

        # Updates display
        if not lost:
            pygame.display.flip()
            pygame.time.wait(gameSpeed)




                                        #############
                                        # Lost loop #
                                        #############

        while lost:
            screen.fill(white)
            displayText("You lost!", red, centerScreen, 75)
            displayText("Score: " + str(score), red, [centerScreen[0], centerScreen[1] + 60])
            displayText("Press enter to play again or esc to exit.", black, [centerScreen[0], height - 40], 35)
            displayText("Press m to go back to the menu.", black, [centerScreen[0], height - 80], 35)

            # Checks if the score is the new highscore
            if score > hs:
                gameInfo["highscore"] = score

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