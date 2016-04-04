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

from distanceCalculator import Distancer

class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable
        self.future_lines = []
        self.list_living_ghosts = []
        self.function_value = []
        self.previousDistances = [0,0,0,0]
        #open or create the file containing the data of the game
        self.f = open('data/game.arff', 'a+')
        #if the file is empty, we write he weka headers
        if os.stat('data/game.arff').st_size == 0:
            self.f.write(self.generateWekaHeaders())


    def generateWekaHeaders(self):
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

        headers = headers + "@attribute prev-distance-ghost1 NUMERIC \n"
        headers = headers + "@attribute prev-distance-ghost2 NUMERIC \n"
        headers = headers + "@attribute prev-distance-ghost3 NUMERIC \n"
        headers = headers + "@attribute prev-distance-ghost4 NUMERIC \n"

        headers = headers + "@attribute posX NUMERIC\n"
        headers = headers + "@attribute posY NUMERIC\n"

        headers = headers + "@attribute direction {North, South, East, West, Stop}\n"

        headers = headers + "@attribute wall-east {True, False}\n"
        headers = headers + "@attribute wall-south {True, False}\n"
        headers = headers + "@attribute wall-west {True, False}\n"
        headers = headers + "@attribute wall-north {True, False}\n"

        headers = headers + "@attribute move {North, South, East, West, Stop}\n\n"

        headers = headers + "@attribute scoreN NUMERIC\n"

        headers = headers + "@attribute ghost1-livingN {True, False}\n"
        headers = headers + "@attribute ghost2-livingN {True, False}\n"
        headers = headers + "@attribute ghost3-livingN {True, False}\n"
        headers = headers + "@attribute ghost4-livingN {True, False}\n"

        headers = headers + "@attribute distance-ghost1N NUMERIC \n"
        headers = headers + "@attribute distance-ghost2N NUMERIC \n"
        headers = headers + "@attribute distance-ghost3N NUMERIC \n"
        headers = headers + "@attribute distance-ghost4N NUMERIC \n"

        headers = headers + "@attribute prev-distance-ghost1N NUMERIC \n"
        headers = headers + "@attribute prev-distance-ghost2N NUMERIC \n"
        headers = headers + "@attribute prev-distance-ghost3N NUMERIC \n"
        headers = headers + "@attribute prev-distance-ghost4N NUMERIC \n"

        headers = headers + "@attribute posXN NUMERIC\n"
        headers = headers + "@attribute posYN NUMERIC\n"

        headers = headers + "@attribute directionN {North, South, East, West, Stop}\n"

        headers = headers + "@attribute wall-eastN {True, False}\n"
        headers = headers + "@attribute wall-southN {True, False}\n"
        headers = headers + "@attribute wall-westN {True, False}\n"
        headers = headers + "@attribute wall-northN {True, False}\n"

        headers = headers + "@attribute moveN {North, South, East, West, Stop}\n\n"

        headers = headers + "@attribute fx NUMERIC\n"


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
        self.distancer = Distancer(gameState.data.layout, False)


    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        #gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
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

    def fx(self, gameState):
        max_distance = (gameState.data.layout.width ** 2 + gameState.data.layout.height ** 2) ** (0.5)
        # maximun distance and # of dead distances
        distances = []
        living = 0
        for i in range(len(gameState.livingGhosts[1:])):
            if gameState.livingGhosts[i] is True:
                if gameState.getPacmanPosition == gameState.getGhostPosition(i):
                    distances.append(0.7)
                else:
                    distances.append(self.distancer.getDistance(gameState.getPacmanPosition(), gameState.getGhostPosition(i)))
                living += 1

        min_distance = min(distances)
        mean = sum(distances) / float(len(distances))

        # maximum number of ghosts
        max_ghost = len(gameState.livingGhosts[1:])

        # formula
        formula_result = 0.5*(max_distance / min_distance) \
        + 0.2*(max_distance / mean) \
        + 0.3*((self.list_living_ghosts[-4] - living) / max_ghost)

        return formula_result

    def printLineData(self,gameState, move):

        '''CREATING THE WEKA LINE'''

        weka_line = ""
        #score
        weka_line += str(gameState.data.score) + ","

        # include the state (dead or alive) of the ghosts
        for i in gameState.livingGhosts[1:]:
            weka_line = weka_line + str(i) + ","

        # include the distances to the ghosts in the current turn
        for i in gameState.data.ghostDistances:
            if i is None:
                weka_line = weka_line + "0" + ","
            else:
                weka_line = weka_line + str(i) + ","

        # include the distances to the ghosts in the previous turn
        for i in self.previousDistances:
            weka_line = weka_line + str(i) + ","

        # store the distances of this turn for the next one
        for i in range(len(gameState.livingGhosts[1:])):
            if gameState.data.ghostDistances[i] is None:
                self.previousDistances[i] = 0
            else:
                self.previousDistances[i] = gameState.data.ghostDistances[i]

        weka_line += \
        str(gameState.data.agentStates[0].getPosition()[0]) + "," +\
        str(gameState.data.agentStates[0].getPosition()[1])+ "," +\
        str(gameState.data.agentStates[0].getDirection()) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0] - 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] - 1)) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0] + 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] + 1)) + "," +\
        str(move)

        self.future_lines.append(weka_line)

        ghost_living = 0
        for i in range(len(gameState.livingGhosts[1:])):
            if gameState.livingGhosts[i] is True:
                ghost_living += 1

        self.list_living_ghosts.append(ghost_living)

        #don't write the line if the length is less than 4
        if len(self.future_lines) < 4:
            return ""

        self.function_value.append(self.fx(gameState))

        if len(self.function_value) > 1 and self.function_value[-1] < self.function_value[-2]:
            return ""

        return self.future_lines[-4] + "," + weka_line + "," + str(self.function_value[-1]) + "\n"

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

from weka.clusterers import Clusterer


class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def __init__(self, index = 0, inference = "ExactInference", ghostAgents = None):
        BustersAgent.__init__(self, index, inference, ghostAgents)
        self.previousDistances = [0,0,0,0]
        jvm.start(max_heap_size="512m")
        self.loader = Loader(classname="weka.core.converters.ArffLoader")
        self.data = self.loader.load_file("data/game_toCluster.arff")
        self.clusterer = Clusterer(classname="weka.clusterers.SimpleKMeans", options=["-N", "10"])
        self.clusterer.build_clusterer(self.data)
        self.clustered_data = self.classifyData('data/clustered.txt')
        self.inst = ""


    def classifyData(self, filename):
        self.data_clust = [[],[],[],[],[],[],[],[],[],[]]
        with open(filename, "r") as f:
            for line in f:
                cluster_name = line.split(",")[-1]
                if cluster_name == "cluster1\n":
                    self.data_clust[0].append(line)
                elif cluster_name == "cluster2\n":
                    self.data_clust[1].append(line)
                elif cluster_name == "cluster3\n":
                    self.data_clust[2].append(line)
                elif cluster_name == "cluster4\n":
                    self.data_clust[3].append(line)
                elif cluster_name == "cluster5\n":
                    self.data_clust[4].append(line)
                elif cluster_name == "cluster6\n":
                    self.data_clust[5].append(line)
                elif cluster_name == "cluster7\n":
                    self.data_clust[6].append(line)
                elif cluster_name == "cluster8\n":
                    self.data_clust[7].append(line)
                elif cluster_name == "cluster9\n":
                    self.data_clust[8].append(line)
                elif cluster_name == "cluster10\n":
                    self.data_clust[9].append(line)
        return self.data_clust

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

        headers = headers + "@attribute prev-distance-ghost1 NUMERIC \n"
        headers = headers + "@attribute prev-distance-ghost2 NUMERIC \n"
        headers = headers + "@attribute prev-distance-ghost3 NUMERIC \n"
        headers = headers + "@attribute prev-distance-ghost4 NUMERIC \n"

        headers = headers + "@attribute posX NUMERIC\n"
        headers = headers + "@attribute posY NUMERIC\n"

        headers = headers + "@attribute direction {North, South, East, West, Stop}\n"

        headers = headers + "@attribute wall-east {True, False}\n"
        headers = headers + "@attribute wall-south {True, False}\n"
        headers = headers + "@attribute wall-west {True, False}\n"
        headers = headers + "@attribute wall-north {True, False}\n"

        headers = headers + "@data\n\n\n"

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

        # include the distances to the ghosts in the previous turn
        for i in self.previousDistances:
            line = line + str(i) + ","

         # store the distances of this turn for the next one
        for i in range(len(gameState.livingGhosts[1:])):
            if gameState.data.ghostDistances[i] is None:
                self.previousDistances[i] = 0
            else:
                self.previousDistances[i] = gameState.data.ghostDistances[i]

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
            pred = self.clusterer.cluster_instance(inst)
            self.inst = inst
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
        move = self.getMove(GreedyBustersAgent.getInstance(self, gameState))
        if move in gameState.getLegalActions(0):
            return move

        randMove = self.randomMove(move)
        while(randMove not in gameState.getLegalActions(0)):
            randMove = self.randomMove(move)
        return randMove

    def getMove(self, clusterNum):
        #get the closest instance
        values = []
        for instance in self.clustered_data[clusterNum]:
            values.append(self.getSimilarity(instance))

        inst = values.index(max(values))
        #return the movement
        return self.clustered_data[clusterNum][inst].split(",")[-2]

    def getSimilarity(self, instance):
        attrs_known_inst = instance.split(",")
        attrs_new_inst = str(self.inst).split(",")
        similar = 0
        for i in range(len(attrs_new_inst)):
            if attrs_new_inst[i] == attrs_known_inst[i]:
                similar += 1
        return similar



