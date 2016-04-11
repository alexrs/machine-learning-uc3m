# valueIterationAgents.py
# -----------------------


import mdp, util

from learningAgents import ValueEstimationAgent

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.qTable = readQtable()

        # Write value iteration code here
        "*** YOUR CODE HERE ***"

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

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        # the action is the max(self.qTable[state])
        print state
        util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

    def readQtable(self):
        #open the file with the q_table and read it
        f = open('data/q_table.txt', 'r')
        lines = f.readLines();
        #create a matrix to store the values of the q_table
        qTable = [[0 for i in range(len(lines))] for j in range(len(lines[0].split(',')))]
        #update the values of the qTable
        for i in range(len(lines)):
          for j in range(len(lines[i].split(','))):
            qTable[i][j] = lines[i].split(',')[j]

        f.close()
        return qTable

    def writeQtable(self, qTable):
        f = open('data/q_table.txt', 'w')
        f.truncate()
        for i in range(len(qTable)):
            for j in range(len(qTable[i])):
                f.write(str(qTable[i][j]) + ',')
            f.write('\n')

