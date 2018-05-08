import pygame
import random
import time
import os
import sys
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
sky_blue = (18,178,238, 100)
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
running = False

# Initializes the sounds
click = pygame.mixer.Sound("audio{}click.wav".format(osType))

# Size of the snake in pixels
snakesize = 50

# Allows for custom textures
texturePath = "textures{}robo{}".format(osType, osType)

# Chance variables
goldAppleChance = .01
doubleChance = .1

# Number of ms in between each frame
gameSpeed = 45

# Snake Direction
xVelocity = 0
yVelocity = 0

# A list of Body types that contains a x and y element
snakeBody = []

# Which file is open
gameOpen = None

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
lost = False

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


menu = False

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

options = False

# Number of snake parts added through out the game
score = 0


# Imports avaliable save files
saves = open("saves{}saves.txt".format(osType), "r")
avaliable = []
for line in saves:
    temp = line.strip()
    avaliable.append(temp)
saves.close()



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
    global loaded, saveScreen, menu, scoreText, gameInfo, gameOpen, hs
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

        if value == "True" or value == "False":
            gameInfo[key] = bool(value)



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


def saveGame(file):
    global gameInfo
    if file == None:
            pass
    else:
        gameSave = open("saves{}".format(osType) + file + ".txt", "w")
        for key, val in gameInfo.items():
            gameSave.write(key + " = " + str(val) + "\n")

# Creates a loading animation for 3 seconds **currently not used**
def loading(seconds = 1):
    for i in range(1,4):
        dots = "." * i
        screen.fill(white)
        displayText("Loading" + dots, black, (centerScreen[0] + len(dots) * 5, centerScreen[1]))
        pygame.display.flip()
        pygame.time.wait(int(1000 * seconds))

saveScreen = True
loaded = False
# Load Game Loop
while saveScreen:
    screen.fill(white)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            saveScreen = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                saveScreen = False
        elif event.type == pygame.MOUSEBUTTONUP:
            click.play()
            pos = pygame.mouse.get_pos()[1]
            if pos < ((height-100)/3) + 100 and pos > 100:
                if avaliable[0] == "New Game":
                    avaliable[0] = "Save 1"
                loadGame(avaliable[0])

            elif pos > ((height-100)/3) + 100 and pos < 2 * (height-100)/3 + 100:
                if avaliable[1] == "New Game":
                    avaliable[1] = "Save 2"
                loadGame(avaliable[1])

            elif pos > 2 * (height-100)/3 + 100:
                if avaliable[2] == "New Game":
                    avaliable[2] = "Save 3"
                loadGame(avaliable[2])
        elif event.type == pygame.JOYBUTTONDOWN:
            controller = True
            if event.button == 0:
                print("up")
            elif event.button == 1:
                print("down")
            elif event.button == 2:
                print("left")
            elif event.button == 3:
                print("right")
            elif event.button == 11:
                print("A")


    # So that the screen does not load the frame after the save names are updated
    if loaded:
        break

    pos = pygame.mouse.get_pos()
    if not (pos[0] == lastKnowsPos[0] and pos[1] == lastKnowsPos[1]):
        lastKnowsPos = pos
        controller = False
    # Checks to see if mouse is in the window based on x pos
    if not controller:
        if pos[0] > 0 and pos[0] < width:
            inWindow = True
        else:
            inWindow = False

        if pos[1] < ((height - 100) / 3) + 100 and pos[1] > 100 and inWindow:
            pygame.draw.rect(screen, sky_blue,(0, 100, width, (height - 100)/3))
        elif pos[1] > ((height - 100) / 3) + 100 and pos[1] < 2 * (height - 100) / 3 + 100 and inWindow:
            pygame.draw.rect(screen, sky_blue, (0, (height - 100)/3 + 100, width, (height - 100) / 3))
        elif pos[1] > 2 * (height - 100) / 3 + 100 and pos[1] < height and inWindow:
            pygame.draw.rect(screen, sky_blue, (0, 2 * (height - 100)/3 + 100, width, (height - 100) / 3))

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

# Menu loop
while menu:

    screen.fill(white)
    displayText("Snake", green, [width / 2, 50])

    fCount += 1

    # Checks for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu = False
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
                    running = True
                elif selection[1]:
                    options = True
                    selection = [True, False, False, False]
                else:
                    menu = False

    # Causes the selected menu option to fade in and out
    if fCount % 25 == 0:
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

        displayText("Difficulity", black, centerScreen)
        displayText("Exit", black, exitPos)

    elif selection[1]:
        displayText("Start Game", black, startGame)
        if show:
            displayText("Difficulity", black, centerScreen)

        displayText("Exit", black, exitPos)

    elif selection[2]:
        displayText("Start Game", black, startGame)
        displayText("Difficulity", black, centerScreen)

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

    # Options loop
    while options:
        screen.fill(white)

        fCount += 1

        if fCount % 25 == 0:
            if show:
                show = False
            else:
                show = True

        displayText("Options", black, [width / 2, 50])

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
                menu = False
                options = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu = False
                    running = True
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
                        options = False
                        selection = [True, False, False]

        pygame.time.wait(15)
        pygame.display.flip()

    # Main game loop
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                menu = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    menu = False
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

        for i in snakeBody:
            if i.x < 0:
                i.x = width - snakesize
            elif i.x >= width:
                i.x = 0
            if i.y < 0:
                i.y = height - snakesize
            elif i.y >= height:
                i.y = 0

        # snakeBody[0].x += xVelocity
        # snakeBody[0].y += yVelocity

        screen.fill(white)

        # Draws the apples
        for i in range(len(apples) - 1, -1, -1):
            screen.blit(appleTexture, (apples[i].x, apples[i].y))

            # Checks for snake is eating the apple.
            if snakeBody[0].x == apples[i].x and snakeBody[0].y == apples[i].y:

                score += 1
                applecords = newApple()

                if len(snakeBody) == 1:
                        snake = Body(snakeBody[0].x - xVelocity, snakeBody[0].y - yVelocity)
                        snakeBody.append(snake)
                else:
                    snake = Body()
                    snakeBody.append(snake)
                for part in snakeBody:
                    if part.x == applecords[0] and part.y == applecords[1]:
                        applecords = newApple()
                apples[i].x = applecords[0]
                apples[i].y = applecords[1]

                if len(apples) > 1:
                    apples.remove(apples[i])

                if random.random() < doubleChance:
                    a = Body(newApple()[0], newApple()[1])
                    apples.append(a)

                if random.random() < goldAppleChance:
                    goldApple.append(newApple())

        # Draws Gold Apple
        if len(goldApple) > 0:
            for pos in goldApple:
                screen.blit(gapple, pos)
                if snakeBody[0].x == pos[0] and snakeBody[0].y == pos[1]:
                    increment = 0
                    score += 5
                    for i in range(5):
                        snake = Body(x=increment, y=height - 1)
                        increment += snakesize
                        snakeBody.append(snake)
                    goldApple.remove(pos)


        # Draws the snake
        times = 0
        for i in range(len(snakeBody)-1, -1, -1):
            times += 1
            # Draws the body with textures
            if i != 0:

                # If i is the last element in the list blit tail image
                if i == len(snakeBody)-1:
                    print('tail')
                    if snakeBody[i].x - snakeBody[i-1].x < 0:
                        screen.blit(tailL, (snakeBody[i - 1].x, snakeBody[i - 1].y))
                        print("1")
                    elif snakeBody[i].x - snakeBody[i-1].x > 0:
                        screen.blit(tailR, (snakeBody[i - 1].x, snakeBody[i - 1].y))
                        print("2")
                    elif snakeBody[i].y - snakeBody[i-1].y < 0:
                        screen.blit(tailU, (snakeBody[i - 1].x, snakeBody[i - 1].y))
                        print("3")
                    else:
                        screen.blit(tailD, (snakeBody[i-1].x, snakeBody[i-1].y))
                        print("4")

                # Checks body part to the left and right to know if the snake is horizontal
                elif snakeBody[i].x == snakeBody[i-1].x and snakeBody[i].x == snakeBody[i+1].x:
                    screen.blit(bodyUD, (snakeBody[i-1].x, snakeBody[i-1].y))

                # Checks body part to the left and right to know if the snake is vertical
                elif snakeBody[i].y == snakeBody[i-1].y and snakeBody[i].y == snakeBody[i+1].y:
                    screen.blit(bodyLR, (snakeBody[i - 1].x, snakeBody[i - 1].y))

                # Since no other cases were true assumes there is a bend in the snake
                else:
                    if i < len(snakeBody)-1:
                        if (snakeBody[i].x > snakeBody[i-1].x and snakeBody[i].y < snakeBody[i+1].y) or (snakeBody[i].y < snakeBody[i-1].y and snakeBody[i].x > snakeBody[i+1].x):
                            screen.blit(bendTR, (snakeBody[i - 1].x, snakeBody[i - 1].y))

                        elif(snakeBody[i].y > snakeBody[i-1].y and snakeBody[i].x < snakeBody[i+1].x) or (snakeBody[i].x < snakeBody[i-1].x and snakeBody[i].y > snakeBody[i+1].y):
                            screen.blit(bendBL, (snakeBody[i - 1].x, snakeBody[i - 1].y))

                        elif(snakeBody[i].x > snakeBody[i-1].x and snakeBody[i].y > snakeBody[i+1].y) or (snakeBody[i].y > snakeBody[i-1].y and snakeBody[i].x > snakeBody[i+1].x):
                            screen.blit(bendBR, (snakeBody[i - 1].x, snakeBody[i - 1].y))

                        else:
                            screen.blit(bendTL, (snakeBody[i - 1].x, snakeBody[i - 1].y))


                # Gives each body part the location of the body part infront of it.
                snakeBody[i].x = snakeBody[i-1].x
                snakeBody[i].y = snakeBody[i-1].y


            # Draws the snakes head with the head texture
            else:

                snakeBody[0].x += xVelocity
                snakeBody[0].y += yVelocity

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
        pygame.display.flip()
        pygame.time.wait(gameSpeed)

        # Lost loop
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
                    running = False
                    lost = False
                    menu = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        lost = False
                        menu = False
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        restart()
                    elif event.key == pygame.K_m:
                        restart()
                        running = False

            pygame.display.flip()


saveGame(gameOpen)

# When all loops are exited game quits
pygame.quit()
os._exit(1)