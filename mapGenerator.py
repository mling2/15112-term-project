import copy, time, random

# Generic Backtracking Puzzle Solver copied from 
# https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html
# with modifications
class BacktrackingPuzzleSolver(object):
    def solve(self, checkConstraints=True):
        self.moves = [ ]
        self.states = set()
        # If checkConstraints is False, then do not check the backtracking
        # constraints as we go (so instead do an exhaustive search)
        self.checkConstraints = checkConstraints
        self.solutionState = self.solveFromState(self.startState)
        self.solution = list(str(self.solutionState))
        self.solutionMoves = []
        chars = ['(',')',' ', '[', ']', ',']
        for char in chars:
            while char in self.solution:
                self.solution.remove(char)
        for i in range(0, len(self.solution), 2):
            self.solutionMoves.append((int(self.solution[i]), int(self.solution[i+1])))
        return self.solutionMoves

    def solveFromState(self, state):
        if state in self.states:
            # we have already seen this state, so skip it
            return None
        self.states.add(state)
        if self.isSolutionState(state):
            # we found a solution, so return it!
            return state
        else:
            for move in self.getLegalMoves(state):
                # 1. Apply the move
                childState = self.doMove(state, move)
                # 2. Verify the move satisfies the backtracking constraints
                #    (only proceed if so)
                if ((self.stateSatisfiesConstraints(childState)) or
                    (not self.checkConstraints)):
                    # 3. Add the move to our solution path (self.moves)
                    self.moves.append(move)
                    # 4. Try to recursively solve from this new state
                    result = self.solveFromState(childState)
                    # 5. If we solved it, then return the solution!
                    if result != None:
                        return result
                    # 6. Else we did not solve it, so backtrack and
                    #    remove the move from the solution path (self.moves)
                    self.moves.pop()
            return None

    # You have to implement these:

    def __init__(self):
        # Be sure to set self.startArgs and self.startState here
        pass

    def stateSatisfiesConstraints(self, state):
        # return True if the state satisfies the solution constraints so far
        raise NotImplementedError

    def isSolutionState(self, state):
        # return True if the state is a solution
        raise NotImplementedError

    def getLegalMoves(self, state):
        # return a list of the legal moves from this state (but not
        # taking the solution constraints into account)
        raise NotImplementedError

    def doMove(self, state, move):
        # return a new state that results from applying the given
        # move to the given state
        raise NotImplementedError

##############################################
# Generic State Class
#
# Subclass this with the state required by your problem.
# Note that this is a bit hacky with __eq__, __hash__, and __repr__
# (it's fine for 112, but after 112, you should take the time to
# write better class-specific versions of these)
##############################################

class State(object):
    def __eq__(self, other): return (other != None) and self.__dict__ == other.__dict__
    def __hash__(self): return hash(str(self.__dict__)) # hack but works even with lists
    def __repr__(self): return str(self.__dict__)


class MapGeneratorState(State):
    def __init__(self, tilePositions, rows, cols):
        self.tilePositions = tilePositions
        self.startCoords = tilePositions[0]
        self.rows = rows
        self.cols = cols
    def __repr__(self):
        return str(self.tilePositions)

class MapGenerator(BacktrackingPuzzleSolver):
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.startArgs = (rows, cols)
        startCoords = self.getStartCoords()
        self.startState = MapGeneratorState([startCoords], rows, cols)
        self.numTilesMin = 20
    
    def getStartCoords(self):
        orient = random.randint(0,1) #start from left or top
        if orient == 0: # start from left
            return (0, random.randint(0, self.rows-1))
        else: # start from top
            return (random.randint(0, self.cols-1), 0)

    def stateSatisfiesConstraints(self,state):
        # check that there are no squares of four tiles
        for tile in state.tilePositions:
            (x,y) = tile
            if (((x+1,y) in state.tilePositions) and
               ((x,y+1) in state.tilePositions) and 
               ((x+1,y+1) in state.tilePositions)):
               return False
        return True

    def isSolutionState(self,state):
        # too few tiles for an interesting map
        if len(state.tilePositions) < self.numTilesMin: return False
        # check if there is a tile in two ends
        left = right = bottom = top = False
        first = state.tilePositions[0]
        last = state.tilePositions[-1]
        x0, y0, x1, y1 = first[0], first[1], last[0], last[1]
        if (x0 == 0): left = True
        if (x1 == self.cols-1): right = True
        if (y0 == 0): top = True
        if (y1 == self.rows-1): bottom = True
        if ((top and bottom) or  
            (top and right) or 
            (left and right) or 
            (left and bottom)):
            return True
        return False   

    def getLegalMoves(self,state):
        tile = state.tilePositions[-1] # get the row and col of previous tile
        x, y = tile[0], tile[1]
        directions = [(1,0), (0,1), (-1,0), (0,-1)]
        legals = []
        for dir in directions:
            if (((x+dir[0], y+dir[1]) not in state.tilePositions) and 
               (x+dir[0] < self.cols) and 
               (x+dir[0] >= 0) and 
               (y+dir[1] < self.rows) and
               (y+dir[1] >= 0)):
                legals.append(dir)
        random.shuffle(legals)
        return legals

    def doMove(self,state,move):
        newTilePositions = copy.copy(state.tilePositions)
        tile = newTilePositions[-1]
        x, y = tile[0], tile[1]
        x, y = x+move[0], y+move[1]
        newTilePositions.append((x,y))
        return MapGeneratorState(newTilePositions, self.rows, self.cols)

def generateMap(rows, cols):
    solution = MapGenerator(rows,cols).solve()
    if solution != None:
        return solution
    return None