# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import util
import os
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters
import operator

move_to_num  = {
    "Stop" : 0.0,
    "North" : 1.0,
    "South" : 1.0,
    "West" : 2.0,
    "East" : 3.0
};

num_to_move = {
    4.0 : Directions.STOP,
    0.0 : Directions.NORTH,
    1.0 : Directions.SOUTH,
    2.0 : Directions.WEST,
    3.0 : Directions.EAST
};

class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable
        self.future_lines = []
        self.future_score = []
        #open or create the file containing the data of the game
        self.f = open('data/game.arff', 'a+')
        #if the file is empty, we write he weka headers
        if os.stat('data/game.arff').st_size == 0:
            self.f.write(self.generateWekaHeaders())


    def generateWekaHeaders(self):
        headers = ""
        headers = headers + "@relation prueba\n\n"

        headers = headers + "@attribute score5 NUMERIC\n"
        headers = headers + "@attribute score2 NUMERIC\n" 
        headers = headers + "@attribute score NUMERIC\n"

        headers = headers + "@attribute ghost0-living {True, False}\n"
        headers = headers + "@attribute ghost1-living {True, False}\n"
        headers = headers + "@attribute ghost2-living {True, False}\n"
        headers = headers + "@attribute ghost3-living {True, False}\n"
        headers = headers + "@attribute ghost4-living {True, False}\n"

        headers = headers + "@attribute distance-ghost1 NUMERIC \n"
        headers = headers + "@attribute distance-ghost2 NUMERIC \n"
        headers = headers + "@attribute distance-ghost3 NUMERIC \n"
        headers = headers + "@attribute distance-ghost4 NUMERIC \n"

        headers = headers + "@attribute posX NUMERIC\n"
        headers = headers + "@attribute posY NUMERIC\n"

        headers = headers + "@attribute direction {North, South, East, West, Stop}\n"

        headers = headers + "@attribute wall-east {True, False}\n"
        headers = headers + "@attribute wall-south {True, False}\n"       
        headers = headers + "@attribute wall-west {True, False}\n"       
        headers = headers + "@attribute wall-north {True, False}\n"

        headers = headers + "@attribute move {North, South, East, West, Stop}\n\n"

        headers = headers + "@data\n\n\n"
    
        return headers

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        for index, inf in enumerate(self.inferenceModules):
            if not self.firstMove and self.elapseTimeEnable:
                inf.elapseTime(gameState)
            self.firstMove = False
            if self.observeEnable:
                inf.observeState(gameState)
            self.ghostBeliefs[index] = inf.getBeliefDistribution()
        self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

    def printLineData(self,gameState, move):

        weka_line = ""
        for i in gameState.livingGhosts:
            weka_line = weka_line + str(i) + ","
        for i in gameState.data.ghostDistances:
            if i is None:
                weka_line = weka_line + "0" + ","
            else:
                weka_line = weka_line + str(i) + ","

        weka_line = weka_line +\
        str(gameState.data.agentStates[0].getPosition()[0]) + "," +\
        str(gameState.data.agentStates[0].getPosition()[1])+ "," +\
        str(gameState.data.agentStates[0].getDirection()) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0] - 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] - 1)) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0] + 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] + 1)) + "," +\
        str(move) + "\n"

        self.future_lines.append(weka_line)
        self.future_score.append(gameState.data.score)

        if len(self.future_score) < 6:
            return ""

        scores = "" 
        scores = scores + str(self.future_score[-1]) + "," +\
        str(self.future_score[-3]) + "," +\
        str(self.future_score[-6]) + ","
        result = scores + self.future_lines[-6]
        return result

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        move = KeyboardAgent.getAction(self, gameState)
        self.f.write(BustersAgent.printLineData(self, gameState, move))
        return move

from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food

    ''' Print the layout'''
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move


import weka.core.jvm as jvm
from weka.core.converters import Loader, Saver
from weka.classifiers import Classifier, Evaluation
from weka.core.classes import Random
from weka.core.dataset import Attribute, Instance, Instances
import weka.core.serialization as serialization
import weka.classifiers as classifiers


class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def __init__(self, index = 0, inference = "ExactInference", ghostAgents = None):
        BustersAgent.__init__(self, index, inference, ghostAgents)
        jvm.start(max_heap_size="512m")
        self.loader = Loader(classname="weka.core.converters.ArffLoader")
        self.data = self.loader.load_file("data/game.arff")
        self.data.class_is_last()
        self.cls = Classifier(classname="weka.classifiers.trees.REPTree", options=["-M", "2","-V", "0.001","-N", "3", "-S", "1", "-L", "-1"])
        self.cls.build_classifier(self.data)
        serialization.write("data/out.model", self.cls)


    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)

    def getInstance(self, gameState):

        headers = ""
        headers = headers + "@relation prueba\n\n"

        headers = headers + "@attribute score NUMERIC\n"

        headers = headers + "@attribute ghost1-living {True, False}\n"
        headers = headers + "@attribute ghost2-living {True, False}\n"
        headers = headers + "@attribute ghost3-living {True, False}\n"
        headers = headers + "@attribute ghost4-living {True, False}\n"

        headers = headers + "@attribute distance-ghost1 NUMERIC \n"
        headers = headers + "@attribute distance-ghost2 NUMERIC \n"
        headers = headers + "@attribute distance-ghost3 NUMERIC \n"
        headers = headers + "@attribute distance-ghost4 NUMERIC \n"

        headers = headers + "@attribute posX NUMERIC\n"
        headers = headers + "@attribute posY NUMERIC\n"

        headers = headers + "@attribute direction {North, South, East, West, Stop}\n"

        headers = headers + "@attribute wall-east {True, False}\n"
        headers = headers + "@attribute wall-south {True, False}\n"       
        headers = headers + "@attribute wall-west {True, False}\n"       
        headers = headers + "@attribute wall-north {True, False}\n"

        headers = headers + "@attribute move {North, South, East, West, Stop}\n\n"

        headers = headers + "@data\n\n\n"

        objects = serialization.read_all("data/out.model")
        cls = [
            classifiers.Classifier("weka.classifiers.trees.REPTree"),
            classifiers.Classifier("weka.classifiers.functions.LinearRegression"),
            classifiers.Classifier("weka.classifiers.functions.SMOreg"),
        ]
        cls = Classifier()
        file = open('data/instances.arff', 'w+')
        file.write(headers)

        line = ""
        line = line + str(gameState.data.score) + ","


        for i in gameState.livingGhosts[1:]: #discard the first value, as it is PacMan
            line = line + str(i) + ","

        for i in gameState.data.ghostDistances:
            if i is None:
                line = line + "0" + ","
            else:
                line = line + str(i) + ","

        line = line +\
        str(gameState.data.agentStates[0].getPosition()[0]) + "," +\
        str(gameState.data.agentStates[0].getPosition()[1])+ "," +\
        str(gameState.data.agentStates[0].getDirection()) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0] - 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] - 1)) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0] + 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] + 1)) + ",?"


        file.write(line)
        file.close()

        loader = Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file("data/instances.arff")
        data.class_is_last()   # set class attribute
        for index, inst in enumerate(data):
            pred = cls.classify_instance(inst)

        return pred

    def randomMove(self, move):
        rand = random.randint(0, 2)
        
        if move == Directions.NORTH:
            if rand == 0:
                return Directions.EAST
            return Directions.WEST
        elif move == Directions.SOUTH:
            if rand == 0:
                return Directions.EAST
            return Directions.WEST
        elif move == Directions.EAST:
            if rand == 0:
                return Directions.NORTH
            return Directions.SOUTH
        elif move == Directions.WEST:
            if rand == 0:
                return Directions.NORTH
            return Directions.SOUTH
        return Directions.SOUTH

    def chooseAction(self, gameState):
        move = num_to_move[GreedyBustersAgent.getInstance(self, gameState)]
        if move in gameState.getLegalActions(0):
            return move

        randMove = self.randomMove(move)        
        while(randMove not in gameState.getLegalActions(0)):
            randMove = self.randomMove(move)
        return randMove
