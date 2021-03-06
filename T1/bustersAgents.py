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
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters
import operator

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

    def printLineData(self,gameState):
        weka_line = ""
        for i in gameState.livingGhosts:
            weka_line = weka_line + str(i) + ","
        for i in gameState.data.ghostDistances:
            weka_line = weka_line + str(i) + ","
        weka_line = weka_line + str(gameState.data.score) +\
        str(gameState.data.agentStates[0].getPosition()[0]) + "," +\
        str(gameState.data.agentStates[0].getPosition()[1])+ "," +\
        str(gameState.data.agentStates[0].getDirection()) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0] - 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] - 1)) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0] + 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasWall(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] + 1)) + "," +\
        str(gameState.hasFood(gameState.getPacmanPosition()[0] - 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasFood(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] - 1)) + "," +\
        str(gameState.hasFood(gameState.getPacmanPosition()[0] + 1, gameState.getPacmanPosition()[1])) + "," +\
        str(gameState.hasFood(gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1] + 1)) + "\n"

        return(weka_line)

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

        #print gameState

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
        str(gameState.data.agentStates[0].getDirection()) + "\n"
        return(weka_line)

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

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    previousDistances = []

    def randomMove(self):
        move = Directions.SOUTH
        move_random = random.randint(0, 3)
        if ( move_random == 0 ) : move = Directions.WEST
        elif ( move_random == 1 ) : move = Directions.EAST
        elif ( move_random == 2 ) : move = Directions.NORTH
        return move


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

        ''' AGENT FOR BERKELEY IMPLEMENTATION

        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]

        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]

        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman

        # STEP 1: Compute closest ghost

            # Obtain the positions with the highest probability

        ghost = [0 for i in range(len(livingGhostPositionDistributions))]

        for i, x in enumerate(livingGhostPositionDistributions):
            ghost[i] = max(x.items(), key=operator.itemgetter(1))[0]

            # Compute the closest ghost among our obtained likely positions

        candidate = ghost[0]
        for i in range(1, len(ghost)):
            if self.distancer.getDistance(pacmanPosition, ghost[i]) < self.distancer.getDistance(pacmanPosition, candidate):
                candidate = ghost[i]

        # STEP 2: Choose the convenient action to get closer to the ghost

        if pacmanPosition[0] < candidate[0] and Directions.EAST in legal: move = Directions.EAST
        elif pacmanPosition[0] > candidate[0] and Directions.WEST in legal: move = Directions.WEST
        elif pacmanPosition[1] < candidate[1] and Directions.NORTH in legal: move = Directions.NORTH
        elif pacmanPosition[1] > candidate[1] and Directions.SOUTH in legal: move = Directions.SOUTH

        # print "Candidate seems to be in: " + str(candidate) + " and pacman is in: " + str(pacmanPosition)
        # print "Chosen action is: " + str(move)

        END OF AGENT FOR BERKELEY '''

        '*** AGENT FOR UC3M ***'

        # Initialize the action to be returned
        move = None

        # Info about PacMan
            # PacMan position
        pacmanPosition = gameState.getPacmanPosition()
            # PacMan last action
        pacmanDirection = gameState.data.agentStates[0].getDirection()
            # PacMan legal moves
        legal = [a for a in gameState.getLegalPacmanActions()]

        # Info we can count on about the ghosts
        ghostDistances = gameState.data.ghostDistances

        # Action decision

        if len(self.previousDistances) > 0:
            if min(i for i in self.previousDistances if i is not None) < \
                min(i for i in ghostDistances if i is not None):
                # Choose another action when ours had a bad effect
                move = self.randomMove()
                while(move not in legal or move == pacmanDirection):
                    move = self.randomMove()
            else:
                # Keep our direction while the ghost is not getting away when legal
                move = pacmanDirection
                while(move not in legal):
                    move = self.randomMove()
        else:
            # First movement is blind, so we choose it randomly among the legal moves
            move = self.randomMove()
            while(move not in legal):
                move = self.randomMove()

        self.previousDistances = ghostDistances

        "*** END OF AGENT FOR UC3M***"

        return move
