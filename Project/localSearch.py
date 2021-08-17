import util
import sys
import pickle

from math import e
from scheduler import Team, Scheduler, Game
from timeit import default_timer as timer
from optparse import OptionParser


infinity = float('inf')

# in an earlier version of our project we incorrectly called our hill climbing algorithm
# gradient descent, so GD.txt pickle files were created using the hill climbing algorithm


COST = []
TRIPLES = []
B2B = []
FIVEin5 = []
DISTANCE = []  
RUN = []        
        






"""
    Perform greedy hillClimbing on the schedule
"""
def hillClimbing(s, numIters=50000, numSwaps=1):

    # Remove all triples from the schedule (3 games in a row)
    rmTrips = s.removeTriples()
    print "Removed Triples: " + str(rmTrips[0]) + " iterations."

    # Intiailize cost
    cost = s.costFn()

    # Track iterations and iterations without improvement (i)
    i = 0
    iterations = 0
    successes = 0

    # Perform hillClimbing until numIters iterations doesn't produce a cost decrease
    while iterations < numIters:
        COST.append(s.costFn())
        TRIPLES.append(s.totalTriples())
        B2B.append(util.totalBackToBacks(s.teams))
        FIVEin5.append(s.totalFourInFive())
        DISTANCE.append(s.totalDistanceAll())
        print(iterations,s.costFn())
        
        # Perform random swap (random game to new random date)
        infos = s.multiSwap(numSwaps)

        # Cost after swap
        newCost = s.costFn()

        # Check if newCost is better, reset i=0 if so
        if newCost < cost:
            cost = newCost
            i = 0
            successes += 1
        else:
            s.undoMultiSwap(infos)
            i += 1

        iterations += 1
        if iterations % 100000 == 0:
            print iterations, cost

        # Add cost to trace to track progress
        s.trace.append(cost)

    # Print some useful information
    print
    print "Hill Climbing:"
    print " Iterations:", iterations
    print " Back to Backs:", util.totalBackToBacks(s.teams)
    print " Successes Percentage:", successes/float(iterations)
    return cost



# Make testing easier --> gives us options so we don't have to change code
def readCommands(argv):
    # Create OptionParser
    parser = OptionParser()
    # Add some options for what we can pass in command line
    parser.add_option("-m", "--method", dest="method",
                  help="use METHOD to conduct local search (HC or SA)",
                  default="HC")
    parser.add_option("-n", "--numIters", dest="numIters",
                    help="specify the number of iterations to run for", type="int",
                    default=50000)
    parser.add_option("-t", "--numTimes", dest="numTimes",
                    help="number of times to run algorithm", type="int",
                    default=1)
    parser.add_option("-f", "--fileName", dest="fileName",
                    help="pickle FILE to run hillClimbing on", default="")
    parser.add_option("-s", "--numSwaps", dest="numSwaps", type="int",
                    help="numSwaps per iteration, usually just 1", default=1)
    (options, args) = parser.parse_args(argv)
    return options

if __name__ == '__main__':
    # Time the method
    start = timer()

    # Get the options and make variables with them
    options = readCommands(sys.argv[1:])
    method = options.method
    numIters = options.numIters
    numTimes = options.numTimes
    fileName = options.fileName
    numSwaps = options.numSwaps

    bestCost = infinity
    # Run chosen method numTimes number of times
    for i in xrange(numTimes):

        # Get a valid initialization
        if fileName != "":
            try:#
                s = pickle.load(open("pickles/" + fileName, 'rb'))
            except IOError:
                print "Could not open file: " + fileName
        else:
        	s = Scheduler()
        	s.randomStart()

        # Run chosen method
        if method == 'SA':
            new = simulatedAnnealing(s, times=numIters)
            end = timer()
        elif method == 'HC':
            new = hillClimbing(s, numIters, numSwaps)
            end = timer()


        print "Ending Cost:", new
        print

        # Update bestCost and schedule if better
        if new < bestCost:
            bestCost = new
            bestSch = s

    print "Best Cost:", bestCost
    print "Total time:", end - start

    COST.append(bestSch.costFn())
    TRIPLES.append(bestSch.totalTriples())
    B2B.append(util.totalBackToBacks(bestSch.teams))
    FIVEin5.append(bestSch.totalFourInFive())
    DISTANCE.append(bestSch.totalDistanceAll())
    
    
    fileName = 'HC __'+'('+str(bestSch.totalTriples())+',' + str(util.totalBackToBacks(bestSch.teams))+',' + str(bestSch.totalFourInFive())+')'
    fileName = fileName + '.txt'
    fileObject = open(fileName, 'w')

    fileObject.write("Triple")
    fileObject.write('\n')
    for t in TRIPLES:
        fileObject.write(str(t))
        fileObject.write('\n')

    fileObject.write("Back to Back")
    fileObject.write('\n')
    for t in B2B:
        fileObject.write(str(t))
        fileObject.write('\n')

    fileObject.write("Four in Five")
    fileObject.write('\n')
    for t in FIVEin5:
        fileObject.write(str(t))
        fileObject.write('\n')

    fileObject.write("Cost")    
    fileObject.write('\n')
    for t in COST:
        fileObject.write(str(t))
        fileObject.write('\n')

    fileObject.write("Distance")
    fileObject.write('\n')
    for t in DISTANCE:
        fileObject.write(str(t))
        fileObject.write('\n')

    fileObject.close()


