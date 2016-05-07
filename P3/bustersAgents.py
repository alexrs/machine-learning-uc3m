# bustersAgents.py
# ----------------

import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters
import sys

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

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)

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
        
    def printLineData(self,gameState):
    
        '''Observations of the state
        
        print(str(gameState.livingGhosts))
        print(gameState.data.agentStates[0])
        print(gameState.getNumFood())
        print (gameState.getCapsules())
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print(width, height)
        print(gameState.data.ghostDistances)
        print(gameState.data.layout)'''
      
        '''END Observations of the state'''
        
        print gameState
        
        weka_line = ""
        for i in gameState.livingGhosts:
            weka_line = weka_line + str(i) + ","
        weka_line = weka_line + str(gameState.getNumFood()) + "," 
        for i in gameState.getCapsules():
            weka_line = weka_line + str(i[0]) + "," + str(i[1]) + ","
        for i in gameState.data.ghostDistances:
            weka_line = weka_line + str(i) + ","
        weka_line = weka_line + str(gameState.data.score) + "," +\
        str(len(gameState.data.capsules))  + "," + str(self.countFood(gameState)) +\
        "," + str(gameState.data.agentStates[0].configuration.pos[0]) + "," +\
        str(gameState.data.agentStates[0].configuration.pos[0])  +\
        "," + str(gameState.data.agentStates[0].scaredTimer) + "," +\
        self.printGrid(gameState) + "," +\
        str(gameState.data.agentStates[0].numReturned) + "," +\
        str(gameState.data.agentStates[0].getPosition()[0]) + "," +\
        str(gameState.data.agentStates[0].getPosition()[1])+ "," +\
        str(gameState.data.agentStates[0].numCarrying)+ "," +\
        str(gameState.data.agentStates[0].getDirection())
        print(weka_line)
        
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        self.printLineData(gameState)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
        
class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """

        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        "*** YOUR CODE HERE ***"
        return Directions.EAST


from learningAgents import ReinforcementAgent

class P3QLearning(BustersAgent):
    "An agent that charges the closest ghost."

    def __init__(self, index = 0, inference = "ExactInference", ghostAgents = None):
        BustersAgent.__init__(self, index, inference, ghostAgents)
        self.q_table = self.initQTable()
        self.epsilon = 0.7
        self.alpha = 0.6
        self.discount = 0.3
        self.actions = [Directions.NORTH, Directions.WEST, Directions.SOUTH, Directions.EAST]
        self.lastState = None
        self.lastAction = None
        self.numGhosts = 4
        self.lastDistance = 100
        self.turns = 0

        #para cada par q_table[(state, action)] habra un valor. 

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def getAction(self, gameState):
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        if self.turns >= 200:
            print "Exit"
            sys.exit(0)
        state = ""
        ghostDist = []
        for i in range(len(gameState.livingGhosts)):
            if gameState.livingGhosts[i] is True:
                ghostDist.append(gameState.getGhostPosition(i))

        pacmanPosition = gameState.getPacmanPosition()
        print pacmanPosition
        dists = []
        for i in ghostDist:
            dists.append(self.distancer.getDistance(pacmanPosition, i))

        index = dists.index(min(dists))
        vec = (pacmanPosition[0] - ghostDist[index][0], pacmanPosition[1] - ghostDist[index][1])
        if vec[0] > 0:
            if vec[1] > 0:
                #print "down left"
                if vec.index(max(vec)) == 0:
                    state += Directions.SOUTH
                else:
                    state += Directions.WEST
            else:
                #print "up left"
                if vec.index(max(vec)) == 0:
                    state += Directions.NORTH
                else:
                    state += Directions.WEST
        else:
            if vec[1] > 0:
                #print "down right"
                if vec.index(max(vec)) == 0:
                    state += Directions.SOUTH
                else:
                    state += Directions.EAST
            else:
                #print "up right"
                if vec.index(max(vec)) == 0:
                    state += Directions.NORTH
                else:
                    state += Directions.EAST

        state += ","

        state +=\
        str(gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] + 1)) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0] - 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] - 1)) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0] + 1, gameState.getPacmanPosition()[1])) 


        legalActions = self.getLegalActions(state)
        action = None
        if util.flipCoin(self.epsilon):
            action = self.getPolicy(state)
        else:
            action = random.choice(legalActions)

        if self.lastState != None and self.lastAction != None:
            reward = 0
            if sum(gameState.livingGhosts) < self.numGhosts:
                numGhosts = sum(gameState.livingGhosts)
                reward = 100
            self.update(self.lastState, self.lastAction, state, reward)

        self.lastState = state
        self.lastAction = action
        self.turns += 1
        return action

        #return BustersAgent.chooseAction(self, gameState)

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getLegalActions(self, state):
        legalActions = []
        state = state.split(",")[1:]
        for i,s in enumerate(state):
            if s == "False":
                legalActions.append(self.actions[i])
        return legalActions


    def getValue(self, state):
        return self.computeValueFromQValues(state)

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        legalActions = self.getLegalActions(state)
        if len(legalActions)==0:
          return 0.0
        tmp = []
        for action in legalActions:
          tmp.append(self.computeQValueFromValues(state, action))

        return max(tmp)


    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        legalActions = self.getLegalActions(state)
        if len(legalActions)==0:
          return None
        tmp = util.Counter()
        for action in legalActions:
          tmp[action] = self.computeQValueFromValues(state, action)
        return tmp.argMax()

    def computeQValueFromValues(self, state, action):

        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        "*** YOUR CODE HERE ***"
        return self.q_table[(state, action)]


    def initQTable(self):
        table_file = open("qtable.txt", "r")
        table_file.seek(0)
        table = table_file.readlines()
        qvalues = []
        for i, line in enumerate(table):
            qvalues.append(line)
        table_file.close()

        q_table = util.Counter()
        dirs = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        walls = ["True", "False"]
        actions = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        i = 0
        for direction in dirs:
            for wall1 in walls:
                for wall2 in walls:
                    for wall3 in walls:
                        for wall4 in walls:
                            for action in actions:
                                state = direction + "," + wall1 + "," + wall2 + ","+ wall3 + ","+ wall4
                                q_table[(state, action)] = float(qvalues[i])
                                i += 1
        return q_table

    def update(self, state, action, nextState, reward):
        print "Prev", self.q_table[(state,action)]
        self.q_table[(state,action)] = (1-self.alpha)*self.q_table[(state, action)] + self.alpha*(reward + self.discount*self.getValue(nextState))
        print self.q_table[(state,action)]

    def writeQtable(self):
        table_file = open("qtable.txt", "w+")
        for key in self.q_table:
            table_file.write(str(self.q_table[key])+"\n")
        table_file.close()

    def __del__(self):
        self.writeQtable()    
"""
      Q-Learning Agent

      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)

      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions for a state
"""

class QLearningAgent(BustersAgent, ReinforcementAgent):
    "An agent that charges the closest ghost."
    """
        These default parameters can be changed from the pacman.py command line.
        For example, to change the exploration rate, try:
           
        QTable   - QTable
        alpha    - learning rate
        epsilon  - exploration rate
        gamma    - discount factor
        numTraining - number of training episodes, i.e. no learning after these many episodes
        """
        
    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable
        
        
    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()
    
    def chooseAction(self, gameState):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        util.raiseNotDefined()
        
    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          NOTE: You should never call this function,
          it will be called on your behalf
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()
        
    def getPolicy(self, state):
        return self.chooseAction(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.chooseAction(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)


class PacmanQAgent(QLearningAgent):
    "Exactly the same as QLearningAgent, but with different default parameters"

    def __init__(self, **args):
        self.index = 0  # This is always Pacman
        QLearningAgent.__init__(self, **args)

    def getAction(self, state):
        """
        Simply calls the getAction method of QLearningAgent and then
        informs parent of action for Pacman.  Do not change or remove this
        method.
        """
        action = QLearningAgent.chooseAction(self,state)
        self.doAction(state,action)
        return action
    def chooseAction(self, gameState):
        action = QLearningAgent.chooseAction(self,gameState)
        return action

class ApproximateQAgent(PacmanQAgent):
    """
       ApproximateQLearningAgent

       You should only have to overwrite getQValue
       and update.  All other QLearningAgent functions
       should work as is.
    """
    def __init__(self, extractor='IdentityExtractor', **args):
        self.featExtractor = util.lookup(extractor, globals())()
        PacmanQAgent.__init__(self, **args)
        self.weights = util.Counter()

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def update(self, state, action, nextState, reward):
        """
           Should update your weights basedPaca on transition
        """
        "*** YOUR CODE HERE ***"
        feats = self.featExtractor.getFeatures(state, action)
        for f in feats: 
          self.weights[f] = self.weights[f] + self.alpha * feats[f]*((reward + self.discount * self.computeValueFromQValues(nextState)) - self.getQValue(state, action))

        # util.raiseNotDefined()

    def final(self, state):
        "Called at the end of each game."
        # call the super-class final method
        PacmanQAgent.final(self, state)

        # did we finish training?
        if self.episodesSoFar == self.numTraining:
            # you might want to print your weights here for debugging
            "*** YOUR CODE HERE ***"
            pass
