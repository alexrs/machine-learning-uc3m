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
    "Stop" : 4.0,
    "North" : 0.0,
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

        score = gameState.data.score
        posX = gameState.data.agentStates[0].getPosition()[0]
        posY = gameState.data.agentStates[0].getPosition()[1]
        distance_ghost1 = gameState.data.ghostDistances[0]
        if distance_ghost1 is None:
            distance_ghost1 = 0
        distance_ghost2 = gameState.data.ghostDistances[1]
        if distance_ghost2 is None:
            distance_ghost2 = 0
        distance_ghost3 = gameState.data.ghostDistances[2]
        if distance_ghost3 is None:
            distance_ghost3 = 0
        distance_ghost4 = gameState.data.ghostDistances[3]
        if distance_ghost4 is None:
            distance_ghost4 = 0
        direction = gameState.data.agentStates[0].getDirection()
        wall_north = gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] + 1)
        wall_south = gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] - 1)
        wall_east = gameState.hasWall(gameState.getPacmanPosition()[0] - 1, gameState.getPacmanPosition()[1])
        wall_west = gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] + 1)
        score5 = 0
        #rule1
        if score <= 80.5 and posY <= 12.5:
            score5 = -6.4085 * score - 6.7661 * distance_ghost1 - 4.154 * distance_ghost2 - 7.7257 * distance_ghost3 - 3.8383 * distance_ghost4 - 0.126 * posY + 2.4542 * move_to_num[direction]+ 2.1865 * move_to_num["West"] - 0.8438 * False + 292.0432

        #rule2
        elif score > 452.5:
            score5 = 0.9306 * score - 0.9068 * distance_ghost1 - 0.0953 * distance_ghost2 - 0.598 * distance_ghost3 - 0.4234 * distance_ghost4 - 0.1318 * posY + 5.5361 * move_to_num["West"] - 1.0844 * True - 0.7155 * False + 39.7805

        #rule 3
        elif score > 193.5 and distance_ghost3 <= 6.5:
            score5 = 0.0416 * score - 12.834 * distance_ghost1 - 0.3527 * distance_ghost2 - 7.3647 * distance_ghost3 - 1.1317 * distance_ghost4 - 0.1088 * posX - 9.5995 * posY + 51.7836 * move_to_num["West"] - 3.0172 * True - 0.9718 * False + 590.7974

        #rule 4
        elif score > 267.5 and distance_ghost4 > 7.5:
            score5 = 0.8563 * score - 1.9181 * False - 1.9429 * distance_ghost2 - 1.1917 * distance_ghost4 + 0.3026 * posX - 0.7279 * posY + 3.8523 * move_to_num["North"]+ 3.8523 * move_to_num["West"] + 73.6666 

        #rule 5
        elif score > 80.5:
            score5 = 0.8159 * score - 199.498 * False - 119.4729 * False - 162.2071 * False - 18.8855 * distance_ghost1 - 9.0657 * distance_ghost2 - 6.8953 * distance_ghost4 + 0.2597 * posX - 0.3477 * posY + 508.3079 
        #rule 6
        else:
            score5 = 1 * score - 5

        score2 = 0
        #rule 1
        if score > 452.5:
            score2 = 0.9557 * score - 0.7703 * distance_ghost1 - 0.4388 * distance_ghost2 - 0.3848 * distance_ghost3 - 0.3099 * distance_ghost4 - 0.0889 * posX - 0.0352 * posY + 0.3226 * move_to_num["East"]+ 3.8023 * move_to_num["West"] - 0.4516 * True + 25.9408 
        elif score > 80.5:
            score2 = 0.4695 * score - 9.2286 * distance_ghost1 - 6.4035 * distance_ghost2 - 4.2593 * distance_ghost3 - 3.793 * distance_ghost4 - 1.8325 * posX - 0.0932 * posY + 0.4761 * move_to_num["East"] + 53.3827 * move_to_num["West"] + 339.6266
        elif posY <= 11.5:
            score2 = -6.2023 * score - 6.0336 * distance_ghost1 - 5.535 * distance_ghost3 - 3.9829 * distance_ghost4 + 2.7181 * move_to_num["East"] + 175.0467 
        else:
            score2 = 1 * score - 3 

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
