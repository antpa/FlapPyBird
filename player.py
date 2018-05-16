from nn import NeuralNetwork
from numpy import array
from const import *

class Player:
    def __init__(self, brain = None):
        self.x = 64
        self.y = int(SCREENHEIGHT / 2)
        self.width = 20

         # player velocity, max velocity, downward accleration, accleration on flap
        self.velY    =  0
        self.gravity =  0.7
        self.lift    = -12
        self.flapped = False

        self.score = 0
        self.fitness = 0

        if(brain) :
            self.brain = brain.copy()
        else:
            self.brain = NeuralNetwork(6,6,2)

    def think(self, pipes) :
        closestIndex = 0
        closestDistance = SCREENWIDTH
        for i in range (0,len(pipes)) :
            # d1 = pipes[i]["x"] - self.x
            d = (pipes[i]["x"] + PIPEWIDTH) - self.x
            # d = (d1 + d2) / 2
            if d < closestDistance and d > 0: 
                closestIndex = i
                closestDistance = d

        inputs = []
        inputs.append(float(self.y / SCREENHEIGHT))
        # the y of the lower side of the upper pipe is
        # the actual Y of the pipes - the PIPEHEIGHT
        inputs.append(float(pipes[closestIndex]["top"] / SCREENHEIGHT))
        inputs.append(float(pipes[closestIndex]["bottom"]  /SCREENHEIGHT))
        inputs.append(float(pipes[closestIndex]["x"] / SCREENWIDTH)) 
        inputs.append(float(self.velY / VELYMAX)) 
        inputs.append(float((pipes[closestIndex]["x"] + PIPEWIDTH) / SCREENWIDTH)) 
        # print(inputs)

        h, output = self.brain.predict(array(inputs))
        # print(str(output[0][0]) + " > " +str(output[1][0]))
        if output[0][0] > output[1][0]:
            self.jump()

    def update(self):
        self.score += 1

        self.velY += self.gravity
        self.y += self.velY

        if self.y > BASEY:
            self.y = BASEY
            self.velY = 0

        if self.y < 0 :
            self.y = 0
            self.velY = 0
        
        self.flapped = False
    
    def jump(self) :
        if not self.flapped  and self.velY + self.lift > VELYMAX:
            self.velY += self.lift
            self.flapped = True
        