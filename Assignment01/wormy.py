# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys,math
from pygame.locals import *

class WormControls:
    def __init__(self, up, down, left, right, shoot, die):
        self.UP = up
        self.DOWN = down
        self.LEFT = left
        self.RIGHT = right
        self.SHOOT = shoot
        self.DIE = die


FPS = 5
WINDOWWIDTH = 640 * 2
WINDOWHEIGHT = 480 * 2
CELLSIZE = 20
RADIUS = math.floor(CELLSIZE/2.5)
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
LIGHTGRAY = (83, 83, 83)
YELLOW = (255,255,0)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

ALIVE = 1 # Basic Enum for Worm Status
DEAD = 0

HEAD = 0 # syntactic sugar: index of the worm's head
NUM_APPLES = 20 # number of apples to generate
NUM_WORMS = 2 # number of worms to generate, keep below 6
KEY_BINDS = [WormControls(up=K_UP, down=K_DOWN, left=K_LEFT, right=K_RIGHT, shoot=K_RSHIFT, die=K_RCTRL), WormControls(up=K_w, down=K_s, left=K_a, right=K_d, shoot=K_LSHIFT, die=K_LCTRL)] # list of controls for each worm
GLOBAL_KEYS = WormControls(up=K_KP8, down=K_KP2, left=K_KP4, right=K_KP6, shoot=K_KP0, die=K_KP_PERIOD) # Global Keybinds, Control All Worms at Once
assert NUM_WORMS <= len(KEY_BINDS)

COOLDOWN_TIMER = 5 # Cooldown for Worms Gun Attack

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Squirmy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # Starts all Worms Next to Each Other in a Random Location
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormList = [[{'x': startx,     'y': starty - 2 * i},
                  {'x': startx - 1, 'y': starty - 2 * i},
                  {'x': startx - 2, 'y': starty - 2 * i}] for i in range(NUM_WORMS)]



    # Sets Initial State
    wormsState = [ALIVE for i in range(NUM_WORMS)]
    directions = [RIGHT for i in range(NUM_WORMS)]
    newDirections = [RIGHT for i in range(NUM_WORMS)]

    # Start the apples in a random place.
    apples = [getRandomLocation() for i in range(NUM_APPLES)]

    scores = [0 for i in range(NUM_WORMS)]
    gunCoolDowns = [0 for i in range(NUM_WORMS)]
    bullets = []
    corpses = []


    while True: # main game loop

        # Checks if Game Should Continue
        for i in range(len(wormList)):
            if wormsState[i]:
                break # At Least One Worm Alive, Keep Going
        else:
            return # No Worms Left, Game Over

        for event in pygame.event.get(): # event handling loop

            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                for i in range(NUM_WORMS):
                    if (event.key == KEY_BINDS[i].UP or event.key == GLOBAL_KEYS.UP) and directions[i] != DOWN:
                        newDirections[i] = UP
                    elif (event.key == KEY_BINDS[i].DOWN or event.key == GLOBAL_KEYS.DOWN) and directions[i] != UP:
                        newDirections[i] = DOWN
                    elif (event.key == KEY_BINDS[i].LEFT or event.key == GLOBAL_KEYS.LEFT) and directions[i] != RIGHT:
                        newDirections[i] = LEFT
                    elif (event.key == KEY_BINDS[i].RIGHT or event.key == GLOBAL_KEYS.RIGHT) and directions[i] != LEFT:
                        newDirections[i] = RIGHT
                    elif (event.key == KEY_BINDS[i].SHOOT or event.key == GLOBAL_KEYS.SHOOT) and gunCoolDowns[i] == 0 and wormsState[i]:
                        gunCoolDowns[i] = COOLDOWN_TIMER
                    elif (event.key == KEY_BINDS[i].DIE or event.key == GLOBAL_KEYS.DIE) and wormsState[i]:
                        gunCoolDowns[i] = COOLDOWN_TIMER + 1
                    elif event.key == K_ESCAPE:
                        terminate()

        # Spawns Bullets When Gun is Fired or The Worm Commits Suicide
        for i, coolDown in enumerate(gunCoolDowns):
            if coolDown == COOLDOWN_TIMER:
                if directions[i] != UP:
                    bullets.append({'x': wormList[i][HEAD]['x'], 'y': wormList[i][HEAD]['y'] + 1, 'direction': DOWN})
                if directions[i] != DOWN:
                    bullets.append({'x': wormList[i][HEAD]['x'], 'y': wormList[i][HEAD]['y'] - 1, 'direction': UP})
                if directions[i] != LEFT:
                    bullets.append({'x': wormList[i][HEAD]['x'] + 1, 'y': wormList[i][HEAD]['y'], 'direction': RIGHT})
                if directions[i] != RIGHT:
                    bullets.append({'x': wormList[i][HEAD]['x'] - 1, 'y': wormList[i][HEAD]['y'], 'direction': LEFT})

            # Kamikaze Mode, Worm Attempts to Take Down Another at the Cost of Its Life
            elif coolDown > COOLDOWN_TIMER:
                for fragment in wormList[i]:
                    for direction in [UP, DOWN, LEFT, RIGHT]:
                        bullets.append({'x': fragment['x'], 'y': fragment['y'], 'direction': direction})
                wormsState[i] = DEAD
                gunCoolDowns[i] = 0

        # Updates Directions After Event Loop, to Allow Only One Direction Change Per Game Loop
        for i in range(len(directions)):
            directions[i] = newDirections[i]


        # Sets Up the Board and Static Objects
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        for apple in apples:
            drawApple(apple)


        # check edge cases for each worm
        for wormId, wormCoords in enumerate(wormList):
            # check if the worm has hit itself or the edge or another live/dead worm
            if wormsState[wormId]:
                # Worm-Map Collision
                if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or \
                        wormCoords[HEAD]['y'] == CELLHEIGHT:
                    wormsState[wormId] = DEAD

                # Worm-Self Collision
                for wormBody in wormCoords[1:]:
                    if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                        wormsState[wormId] = DEAD

                # Worm-Worm Collision
                for testWorm in wormList:
                    if testWorm != wormCoords:
                        for wormBody in testWorm:
                            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                                wormsState[wormId] = DEAD

                # Worm-Fragment Collision
                for corpse in corpses:
                    for segment in corpse:
                        if segment['x'] == wormCoords[HEAD]['x'] and segment['y'] == wormCoords[HEAD]['y']:
                            wormsState[wormId] = DEAD

                # Worm-Bullet Collision
                for fragmentID, wormBody in enumerate(wormCoords):
                    for bullet in bullets:
                        if bullet['x'] == wormBody['x'] and bullet['y'] == wormBody['y']:
                            if fragmentID == HEAD:
                                wormsState[wormId] = DEAD
                            else:
                                wormList[wormId] = wormCoords[:fragmentID]
                                corpses.append(wormCoords[fragmentID:])

        # MOves the Worms
        for wormId, wormCoords in enumerate(wormList):
            if wormsState[wormId]:

                # checks for all apples
                fed = False
                for index, apple in enumerate(apples):
                    # check if worm has eaten an apply
                    if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
                        # don't remove worm's tail segment
                        apples[index] = getRandomLocation() # set a new apple somewhere
                        fed = True
                        break

                # move each worm by adding a segment in the direction it is moving
                if directions[wormId] == UP:
                    newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
                elif directions[wormId] == DOWN:
                    newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
                elif directions[wormId] == LEFT:
                    newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
                elif directions[wormId] == RIGHT:
                    newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
                wormCoords.insert(0, newHead)   #have already removed the last segment
                if not fed:
                    del wormCoords[-1]
                drawWorm(wormCoords)
                scores[wormId] = len(wormCoords) - 3

                # Tick Down Gun Timer
                if gunCoolDowns[wormId] > 0:
                    gunCoolDowns[wormId] -= 1
            else:
                drawStones(wormCoords[1:])

        # Moves the Bullets and Deletes Out of Bounds Bullets
        for bullet in bullets:
            if bullet['direction'] == UP:
                bullet['y'] -= 1
            if bullet['direction'] == DOWN:
                bullet['y'] += 1
            if bullet['direction'] == LEFT:
                bullet['x'] -= 1
            if bullet['direction'] == RIGHT:
                bullet['x'] += 1

        for bullet in bullets:
            if bullet['x'] == -1 or bullet['x'] == CELLWIDTH or bullet['y'] == -1 or bullet['y'] == CELLHEIGHT:
                bullets.remove(bullet)


        drawBullets(bullets)
        drawScores(scores)
        for corpse in corpses:
            drawStones(corpse)



        pygame.display.update()
        FPSCLOCK.tick(FPS)

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, YELLOW)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Beebo Inc', True, YELLOW, BLACK)
    titleSurf2 = titleFont.render('Squirmy', True, YELLOW)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(GREEN)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (math.floor(WINDOWWIDTH / 2), math.floor(WINDOWHEIGHT / 2))
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (math.floor(WINDOWWIDTH / 2), math.floor(WINDOWHEIGHT / 2))
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (math.floor(WINDOWWIDTH / 2), 10)
    overRect.midtop = (math.floor(WINDOWWIDTH / 2), gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScores(scores):
    startX = WINDOWWIDTH - 120
    startY = 10
    player = 1
    for score in scores:
        scoreSurf = BASICFONT.render(f'Score (p{player}):  {score}', True, WHITE)
        scoreRect = scoreSurf.get_rect()
        scoreRect.topleft = (startX, startY)
        DISPLAYSURF.blit(scoreSurf, scoreRect)
        startX -= 120
        player += 1


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    xcenter = coord['x'] * CELLSIZE + math.floor(CELLSIZE/2)
    ycenter = coord['y'] * CELLSIZE+ math.floor(CELLSIZE/2)
    #appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    #pygame.draw.rect(DISPLAYSURF, RED, appleRect)
    pygame.draw.circle(DISPLAYSURF, RED,(xcenter,ycenter),RADIUS)

def drawStones(stones):
    for stone in stones:
        x = stone['x'] * CELLSIZE
        y = stone['y'] * CELLSIZE
        stoneRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, LIGHTGRAY, stoneRect)
        stoneInnerRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, DARKGRAY, stoneInnerRect)

def drawBullets(bullets):
    for bullet in bullets:
        x = bullet['x'] * CELLSIZE
        y = bullet['y'] * CELLSIZE
        bulletRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, YELLOW, bulletRect)
        bulletInnerRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, RED, bulletInnerRect)



def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()