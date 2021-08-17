
# -*- coding: utf-8 -*
import util
import sys
import pickle
from datetime import date, timedelta
from math import e
from scheduler import Team, Scheduler, Game
from timeit import default_timer as timer
from optparse import OptionParser

import random
import copy


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

    return s



def randomFalseDate(s,team1,team2,date1,date2):
    """
    find the True date list for both team
    """
    falseDate = []
    for i in range(len(date1)):
        if date1[i] == False and date2[i]==False:
            falseDate.append(i)

    if falseDate == []:
        return 9999
    
    randomDateIndex = random.choice(falseDate)
    
    randomDate = team1.teamCalendar.keys()[randomDateIndex]
    
    count = 0
    while s.tripcheck(team1, randomDate) == False or s.tripcheck(team2, randomDate) == False or s.fourInFivecheck(team2, randomDate) == False or s.fourInFivecheck(team1, randomDate)==False:
        if count >= len(falseDate):
            return 9999
            
        randomDateIndex = random.choice(falseDate)
        randomDate = team1.teamCalendar.keys()[randomDateIndex]
        count = count + 1 
    return randomDate
    
def mutation(s,g):
    """
    Random the new date for game
    """
    #print(s.dateSchedule[g],g,s.nbaSchedule[g][0].name,s.nbaSchedule[g][1].name)

    team1 = s.nbaSchedule[g][0] 
    team2 = s.nbaSchedule[g][1]
    
    s.removeGameAtDate(s.dateSchedule[g],team1.name,team2.name)
    s.removeGameAtDate(s.dateSchedule[g],team2.name,team1.name)
    

    randomDate = randomFalseDate(s,team1,team2,team1.teamCalendar.values(),team2.teamCalendar.values())
    
    #print("len:",len(team1.teamCalendar.values()))
    if randomDate ==9999:
        randomDate = s.dateSchedule[g]
        #print("No change")


    s.dateSchedule[g] = randomDate 
    

    s.nbaSchedule[g][0].schedule.append(Game(randomDate, team2, True))
    s.nbaSchedule[g][1].schedule.append(Game(randomDate, team1, False))
    s.nbaSchedule[g][0].teamCalendar[randomDate] = True
    s.nbaSchedule[g][1].teamCalendar[randomDate] = True
    #s.removeTriples()
    return s

    
def crossover(s1,s2,g):
    """
    Generate the offspring by two parents
    
    """
    #print(s1.dateSchedule[g],s2.dateSchedule[g],g,s1.nbaSchedule[g][0].name,s1.nbaSchedule[g][1].name)
    
    d1 = s2.dateSchedule[g] 
    d2 = s1.dateSchedule[g] 
    s1.removeGameAtDate(d2,s1.nbaSchedule[g][0].name,s1.nbaSchedule[g][1].name)
    s1.removeGameAtDate(d2,s1.nbaSchedule[g][1].name,s1.nbaSchedule[g][0].name)
    s2.removeGameAtDate(d1, s2.nbaSchedule[g][0].name,s2.nbaSchedule[g][1].name)
    s2.removeGameAtDate(d1, s2.nbaSchedule[g][1].name,s2.nbaSchedule[g][0].name)
    
    
    if s1.nbaSchedule[g][0].teamCalendar[d1] == True or s1.nbaSchedule[g][1].teamCalendar[d1] == True or s1.tripcheck(s1.nbaSchedule[g][0],d1) == False or s1.tripcheck(s1.nbaSchedule[g][1],d1) == False or s1.fourInFivecheck(s1.nbaSchedule[g][0],d1) == False or s1.fourInFivecheck(s1.nbaSchedule[g][1],d2) == False:
        d1 = d2

    
    if s2.nbaSchedule[g][0].teamCalendar[d2] == True or s2.nbaSchedule[g][1].teamCalendar[d2] == True or s2.tripcheck(s2.nbaSchedule[g][0],d2) == False or s2.tripcheck(s2.nbaSchedule[g][1],d2) == False or s2.fourInFivecheck(s2.nbaSchedule[g][0],d2) == False or s2.fourInFivecheck(s2.nbaSchedule[g][1],d2) == False:
        d2 = d1

        



    # Add the game, but on new date
    s1.nbaSchedule[g][0].schedule.append(Game(d1, s1.nbaSchedule[g][1], False))
    s1.nbaSchedule[g][0].teamCalendar[d1] = True

    s1.nbaSchedule[g][1].schedule.append(Game(d1, s1.nbaSchedule[g][0], True))
    s1.nbaSchedule[g][1].teamCalendar[d1] = True

    


    # Add the game, but on new date
    s2.nbaSchedule[g][0].schedule.append(Game(d2, s2.nbaSchedule[g][1], False))
    s2.nbaSchedule[g][0].teamCalendar[d2] = True

    s2.nbaSchedule[g][1].schedule.append(Game(d2, s2.nbaSchedule[g][0], True))
    s2.nbaSchedule[g][1].teamCalendar[d2] = True
    
    s1.dateSchedule[g] = d1
    s2.dateSchedule[g] = d2

    return s1,s2    

def getBestSchedule(schedule,fitness):
    """
    Get the best schedule for this round
    """
    bestIndex = sorted(range(len(fitness)), key = lambda k : fitness[k])[:1]
    tmp = copy.deepcopy(schedule[bestIndex[0]])
    bestSchedule = tmp
    return bestSchedule,bestIndex[0]


def getWorseSchedule(schedule,fitness):
    worseIndex = sorted(range(len(fitness)), reverse=True,key = lambda k : fitness[k])[:1]
    worseSchedule = schedule[worseIndex[0]]
    return worseSchedule,worseIndex[0]

def reproduction(schedule,fitness):
    """
    Select the best k% for this round
    """
    reproductionPool = sorted(range(len(fitness)), key = lambda k : fitness[k])[:numReproduction]
    
    scheduleDuplication = []
    # Duplication
    for i in range(0,numChromosome):
        if i in reproductionPool:
            scheduleDuplication.append(schedule[i])
    i = 0        
    while len(scheduleDuplication) != numChromosome:
       
        if i in reproductionPool:
            tmp = copy.deepcopy(schedule[i])
            scheduleDuplication.append(tmp)
            
        i = i + 1
        
        if i== numChromosome-1:
            i = 0
        


      

    return scheduleDuplication
    



def ga(schedule,lastBestSchedule):
    """
    Run GA algorithm
    """
    print("last:",lastBestSchedule.costFn())
    # cacluate fitness
    fitness = []
    for i in range(0,len(schedule)):
        fitness.append(schedule[i].costFn())
        #print("total cost:",schedule[i].costFn(),"total triples:", schedule[i].totalTriples(),"back to back:", util.totalBackToBacks(schedule[i].teams),"four in five:", schedule[i].totalFourInFive(),"total distance:",schedule[i].totalDistanceAll())
   
        
    
    #print('--------Start Reproduction----------')
    schedule = reproduction(schedule,fitness)
    """   
     for i in range(0,numChromosome):
        print("total cost:",schedule[i].costFn(),"total triples:", schedule[i].totalTriples(),"back to back:", util.totalBackToBacks(schedule[i].teams),"four in five:", schedule[i].totalFourInFive(),"total distance:",schedule[i].totalDistanceAll())
    print('------------finidsh reproduction+-------------')
    """
    #crossover
    random.shuffle(schedule)
    for i in range(0,numCrossover,2):
        #select which two gene to be crossover 
        locationCrossover = random.sample(randomCrossover, numCrossoverGene)


        for l in range(0,len(locationCrossover)):
            schedule[i],schedule[i+1] = crossover(schedule[i],schedule[i+1],locationCrossover[l])
    """
    print('--------Finish Crossover----------')
    for i in range(0,numChromosome):
        print("total cost:",schedule[i].costFn(),"total triples:", schedule[i].totalTriples(),"back to back:", util.totalBackToBacks(schedule[i].teams),"four in five:", schedule[i].totalFourInFive(),"total distance:",schedule[i].totalDistanceAll())
    print('--------Start Mutation--------------')
    """
    mutationChromosome = random.sample(randomMutation, numMutation)
    
    
    for i in range(len(mutationChromosome),0,-1):
        mutationGene = random.sample(randomMutationGene, numMutationGene)
        for g in range(0,len(mutationGene)):
            mutation(schedule[i],mutationGene[g])
    """       
    print('--------Finish Mutation----------')
    for i in range(0,numChromosome):
        print("total cost:",schedule[i].costFn(),"total triples:", schedule[i].totalTriples(),"back to back:", util.totalBackToBacks(schedule[i].teams),"four in five:", schedule[i].totalFourInFive(),"total distance:",schedule[i].totalDistanceAll())
    """


    # cacluate fitness
    fitness = []
    for i in range(0,len(schedule)):
        fitness.append(schedule[i].costFn())
        
    
    #Get best schedule of this run
    bestSchedule,bestIndex = getBestSchedule(schedule,fitness)
    print("last:",lastBestSchedule.costFn(),"index",bestIndex,"Best:",bestSchedule.costFn())
    if lastBestSchedule.costFn() < bestSchedule.costFn():
        bestSchedule = lastBestSchedule
        worseSchedule,worseIndex = getWorseSchedule(schedule,fitness)
        del schedule[worseIndex]
        tmp = copy.deepcopy(lastBestSchedule)
        schedule.append(tmp)
        
    print("best schedule","total cost:",bestSchedule.costFn(),"total triples:", bestSchedule.totalTriples(),"back to back:", util.totalBackToBacks(bestSchedule.teams),"four in five:", bestSchedule.totalFourInFive(),"total distance:",bestSchedule.totalDistanceAll())   

    
    COST.append(bestSchedule.costFn())
    TRIPLES.append(bestSchedule.totalTriples())
    B2B.append(util.totalBackToBacks(bestSchedule.teams))
    FIVEin5.append(bestSchedule.totalFourInFive())
    DISTANCE.append(bestSchedule.totalDistanceAll())
    
    
    return schedule,bestSchedule






def giveGameDate(s):
    index = 0
    for g in s.nbaSchedule:

        #print(s.nbaSchedule_name[index])
        index = index + 1

        randomDate = random.choice(s.teams['Denver Nuggets'].teamCalendar.keys())
        while g[0].teamCalendar[randomDate]== True or g[1].teamCalendar[randomDate]== True:
            randomDate = random.choice(s.teams['Denver Nuggets'].teamCalendar.keys())
            
            
        # add game to schedule of both teams
        g[0].schedule.append(Game(randomDate, g[1], True))
        g[1].schedule.append(Game(randomDate, g[0], False))
        # turn value to True
        g[1].teamCalendar[randomDate] = True
        g[0].teamCalendar[randomDate] = True
        s.dateSchedule.append(randomDate) 
        
        
        
        
COST = []
TRIPLES = []
B2B = []
FIVEin5 = []
DISTANCE = []  
RUN = []        
        
    
run = 100
numChromosome = 50
rateReproduction = 0.8
rateCrossover = 0.7
rateMutation = 0.3
rateMutationGene = 0.5
numIters = 50000
numReproduction = int(numChromosome * rateReproduction)
numCrossover = int(numChromosome * rateCrossover)
numCrossoverGene = 615
numMutation = int(numChromosome * rateMutation)
numMutationGene = int(1230 * rateMutationGene)

randomCrossover = [n for n in range(0,1229)]
randomMutation = [n for n in range(0,numChromosome)]
randomMutationGene = [n for n in range(0,1229)]


# Time the method
start = timer()
nba = []

fitness = []
for i in range(0,numChromosome):
    s = Scheduler()
    s.randomStart()
    giveGameDate(s)
    #s.removeTriples()
    #print("Add",i,"Chromosome")
    nba.append(s)
    fitness.append(nba[i].costFn())
   # print("total cost:",s.costFn())




    


#Get best schedule of this run
lastBestSchedule,bestIndex = getBestSchedule(nba,fitness)
result,lastBestSchedule = ga(nba,lastBestSchedule)

countStop = 0

while run > 0 :
    stop = lastBestSchedule
    RUN.append(run)
    print('-------------------------------',run,'----------------------------------')
    result,lastBestSchedule = ga(result,lastBestSchedule)
    if stop.costFn() == lastBestSchedule.costFn():
        countStop = countStop + 1
    
    else:
        countStop = 0
    
    if countStop >= 15:
        break
    
    print("outside",lastBestSchedule.costFn())
    run = run - 1


    
best = hillClimbing(lastBestSchedule, numIters, numSwaps=1)
        
COST.append(best.costFn())
TRIPLES.append(best.totalTriples())
B2B.append(util.totalBackToBacks(best.teams))
FIVEin5.append(best.totalFourInFive())
DISTANCE.append(best.totalDistanceAll())

best.removeTriples()        
end = timer()
print "Total time:", end - start

print("total triples:", best.totalTriples())
print("back to back:", util.totalBackToBacks(best.teams))
print("four in five:", best.totalFourInFive())
print("total distance:",best.totalDistanceAll())
print("total cost:",best.costFn())

print(run,numChromosome,rateReproduction ,rateCrossover,rateMutation,rateMutationGene,numIters)
fileName = 'HC && GA__'+'('+str(best.totalTriples())+',' + str(util.totalBackToBacks(best.teams))+',' + str(best.totalFourInFive())+')'
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

