from itertools import cycle
import random
import sys
from nn import *
import pygame
from pygame.locals import *
from player import Player
import ga
from const import *
import os.path

previous_score = 0
savedPlayers = []
players = []

def main(arg):
    global robotoFont, bestScoreEver, SCREEN, players, pipes, speed, previous_score, filename, trainningMode
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Flappy Bird')
    robotoFont = pygame.font.SysFont("Roboto", 30)

    brain = None
    filename = arg[1] if len(arg) > 1 else "goodplayer.json"
    if os.path.isfile(filename) :
        with open(filename, 'r') as file :
            brain = NeuralNetwork.fromjson(file.read())

    trainningMode = False
    # Populate with players
    if len(arg) > 2 and arg[2] == "train":
        trainningMode = True
        for i in range(0, MAX_POPULATION):
            p = Player(brain)
            if brain is not None :
                p.brain.mutate(0.1)
            players.append(p)
    else :
        p = Player(brain)
        players.append(p)

        
    # Create pipes
    newPipe = generatePipe()
    pipes = [newPipe]

    bestScoreEver = 0
    speed = 1
    while True:
        handleGameEvents()
        for i in range(0, speed) :
            bestPlayerScore, bestScoreEver = update()
        
        # draw
        # Background
        SCREEN.fill((0,0,0))

        # Pipes
        for pipe in pipes:
            pygame.draw.rect(SCREEN,(255,255,255), (pipe['x'], pipe['top'] - PIPEHEIGHT,PIPEWIDTH,PIPEHEIGHT))
            pygame.draw.rect(SCREEN,(255,255,255), (pipe['x'], pipe['bottom'],PIPEWIDTH,PIPEHEIGHT))

        # Ground
        pygame.draw.rect(SCREEN,(255,255,255), (BASEX, BASEY,SCREENWIDTH,SCREENHEIGHT - BASEY))

        # Players
        for player in players:
            box_surface_circle = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(box_surface_circle, (255, 255, 255, 75), (int(player.width/2), int(player.width/2)),int(player.width/2), 0)
            SCREEN.blit(box_surface_circle, (player.x, player.y))
       
       # Scores
        showScore(bestPlayerScore, (10,0))
        showScore(bestScoreEver, (10, 25))
        showScore(len(players), (SCREENWIDTH - 40, 0))            

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def handleGameEvents() :
    global speed
    for event in pygame.event.get():
        # QUIT
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

        # SPEED UP
        if event.type == KEYDOWN and event.key == K_UP:
            speed += 1
            print("up")
        # SPEED DOWN
        elif event.type == KEYDOWN and event.key == K_DOWN:
            speed -= 1
            print("down")
            
        if speed < 1 :
            speed = 1   
        if speed > 10 : 
            speed = 10

def update():
    global previous_score, bestScoreEver, savedPlayers, players, pipes
    # move pipes to left
    for pipe in pipes:
        pipe['x'] += PIPEVELX

    # add new pipe when last pipe is about to touch left of screen
    if 0 < pipes[- 1]['x'] < SCREENWIDTH / 3:
        newPipe = generatePipe()
        pipes.append(newPipe)

    # remove first pipe if its out of the screen
    if pipes[0]['x'] < -PIPEWIDTH:
        pipes.pop(0)

    # check crash 
    i = 0
    while i < len(players) :
        player = players[i]
        crashTest = checkCrash(player, pipes)
        if crashTest:
            savedPlayers.append(player)
            players.remove(player)
            i -= 1
        i += 1

    bestPlayerScore = 0
    for player in players:
        player.think(pipes)
        player.update()
        bestPlayerScore = max(player.score, bestPlayerScore)
    
    bestScoreEver = max(bestScoreEver, bestPlayerScore)
        
    if len(players) == 0:
        if max(previous_score, bestScoreEver) > previous_score :
            json = savedPlayers[-1].brain.tojson()
            with open(filename, 'w') as file :
                file.write(json)
        
            showBestNN()
            previous_score = max(previous_score, bestScoreEver)

        if trainningMode :
            players = ga.nextGeneration(savedPlayers)
        else :
            players.append(Player(savedPlayers[-1].brain))

        savedPlayers = []        
        # clear pipes
        newPipe = generatePipe()
        pipes = [newPipe]

    return bestPlayerScore, bestScoreEver

def generatePipe():
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY*0.8 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeX = SCREENWIDTH + 10

    return {'x': pipeX, 'top': gapY, 'bottom' : gapY + PIPEGAPSIZE}

def showBestNN():
    if len(savedPlayers) == 0 :
        return

    print("BEST Input-Hidden")
    print(savedPlayers[len(savedPlayers) - 1].brain.weight_ih)
    print("BEST Hidden-Output")
    print(savedPlayers[len(savedPlayers) - 1].brain.weight_ho)
    print("Score :")
    print(savedPlayers[len(savedPlayers) - 1].score)

def showScore(score, pos):
    label = robotoFont.render(str(score), 1, (255,255,255))
    SCREEN.blit(label, pos)

def checkCrash(player, pipes):
    # if player crashes into ground or sky
    if player.y + player.width >= BASEY - 1 or player.y <= 0:
        return True
    else:

        playerRect = pygame.Rect(player.x, player.y, player.width, player.width)

        for pipe in pipes:
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(pipe['x'], pipe['top'] - PIPEHEIGHT, PIPEWIDTH, PIPEHEIGHT)
            lPipeRect = pygame.Rect(pipe['x'], pipe['bottom'], PIPEWIDTH, PIPEHEIGHT)

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect)
            lCollide = pixelCollision(playerRect, lPipeRect)

            if uCollide or lCollide:
                return True

    return False

def pixelCollision(rect1, rect2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    return True

if __name__ == '__main__':
    main(sys.argv)
