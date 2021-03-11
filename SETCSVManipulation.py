import time 
fullTimeStart = time.time()
import os
#import thread
import pandas as pan
#import tkinter
from matplotlib import pyplot as plt

class CSVReadandPlot():

    def __init__(self, fileName, loadNewFile = False):
        startTime = time.time()
        self.fileName = fileName[0:len(fileName)-4]+"_stored.pkl" #the .pkl file where the file worked with is stored
        self.csvFileDF = pan.DataFrame.empty
        self.changedDF = False #used to see if the .pkf file stored needs to be updated or added
        #sees if the store file exists and if the user wants to load the file from storage or not
        if os.path.exists(self.fileName) and not loadNewFile:
            self.csvFileDF = pan.read_pickle(self.fileName)
        else: 
            self.csvFileDF = pan.read_csv(fileName)
            self.changedDF = True
        pan.set_option("display.max.columns", None)
        self.interval = 0
        titles = list(self.csvFileDF.columns)
        #will find the interval rate automatically. When it doesn't work, it'll ask you for it. 
        for i in range(0, len(titles)): #to auto find the interval
            if titles[i] == "Record Length":
                try:
                    self.interval = int(titles[i+1])
                except:
                    print("Cannot get the interval rate. What is it?")
                    self.interval = int(input())
                break
        if self.interval == 0:
            print("Cannot get the interval rate. What is it?")
            self.interval = int(input())
        
        self.numInter = int(self.csvFileDF.iloc[:,0].size/self.interval)

        print("time to load csv", (time.time()-startTime)*1000, "milliseconds")
    
    def plotDataInter(self, DFColTitles, inter, showPlot = True, labelNames = None, fastPlot = False):
        #will allow for the plotting of data, put only the specified interval
        #DFColTitles involves what titles are being handled. It's a list. It goes [x, y]
        #labelNames is arranged like [xlabel, ylabel, title]
        csvData, = plt.plot(self.csvFileDF.loc[(inter*self.interval):(inter*self.interval+self.interval-1), DFColTitles[0]], self.csvFileDF.loc[(inter*self.interval):(inter*self.interval+self.interval-1), DFColTitles[1]], label = str(inter))
        if fastPlot:
            plt.style.use('fast')
        if labelNames:
            plt.xlabel(labelNames[0])
            plt.ylabel(labelNames[1])
            plt.title(labelNames[2])

        if showPlot:
            plt.show()
        return csvData

    def plotDataFull(self, DFColTitles, showPlot = True, labelNames = None, fastPlot = False):
        #will allow for the plotting of data in all of the intervals at once
        #DFColTitles involves what titles are being handled. It's a list. It goes [x, y]
        #labelNames is arranged like [xlabel, ylabel, title, addLegend?]
        csvPlot = plt.plot(self.csvFileDF.loc[:, DFColTitles[0]], self.csvFileDF.loc[:, DFColTitles[1]])
        if fastPlot:
            plt.style.use('fast')
        if labelNames:
            plt.xlabel(labelNames[0])
            plt.ylabel(labelNames[1])
            plt.title(labelNames[2])
            if labelNames[3]:
                plt.legend()
        if showPlot:
            plt.show()

    def clearPlot(self):
       plt.cla()

    def isChanged(self):
        return self.changedDF

    def saveWork(self):
        #save the work done to the .pkf file
        startTime = time.time()
        if self.changedDF:
            self.csvFileDF.to_pickle(self.fileName)
        print("time to save", (time.time()-startTime)*1000, "milliseconds")

    def pullFullDF(self):
        #the full DataFrame
        return self.csvFileDF
    
    def colTitles(self):
        #returns the titles of the pandas columns
        return list(self.csvFileDF.columns)

    def numIntervals(self):
        #returns the number of intervals in the test 
        return self.numInter
    
    def pullInterval(self, intervalIndex):
        #will pull the rows a part of a specified interval value
        #the intervalIndex starts at 0 and ends at the number of intervals-1. 
        #For instance intervalIndex = 0 will give you the first interval of data. 
        return self.csvFileDF.loc[(intervalIndex*self.interval):(intervalIndex*self.interval+self.interval-1), :]

    def pullCol(self, colToPull):
        #allows you to pull a specific column
        return self.csvFileDF.loc[:, colToPull]
    
    def pullCols(self, colsToPull):
        #allows you to pull specific columns
        #for this function, you place in all of the columns to pull
        return self.csvFileDF.loc[:, colsToPull]
    
    def pullRow(self, rowToPull):
        #allows you to pull a specific row 
        try:
            return self.csvFileDF.loc[rowToPull]
        except:
            print("TYPEError: You need to use an integer")

    def addInterval(self, desiredInterval, colTitle, dataToAdd):#untested
        #dataToAdd is a list/tuple
        lengthCol = self.csvFileDF.iloc[:,0].size
        while len(dataToAdd) < self.interval:
            dataToAdd.append(0)
        #print(len(self.csvFileDF.loc[(self.interval*desiredInterval)//lengthCol:((self.interval*desiredInterval)//lengthCol+self.interval), 'Time']))
        #print(len(dataToAdd[0:(len(dataToAdd))]))
        self.csvFileDF.loc[(self.interval*desiredInterval)//lengthCol:((self.interval*desiredInterval)//lengthCol+self.interval-1), colTitle] = dataToAdd[0:(len(dataToAdd))]

    def addCol(self, coltoAdd, colTitle, save = True): #will autosave work, unless directed.
        #add a column
        self.csvFileDF.loc[:, colTitle] = coltoAdd
        if save:
            self.saveWork()

    def addRow(self, rowtoAdd, rowTitle, save = True): #will autosave work, unless directed.
        #add a row
        self.csvFileDF.loc[rowTitle, :] = rowtoAdd
        if save:
            self.saveWork()


class manipulateSETData(CSVReadandPlot):

    def __init__ (self, fileName, loadNewFile=False):
        super().__init__(fileName, loadNewFile)
        

    #all the other functions from CSVReadandPlot are in here. 
    

    def derivativeAll(self, colDy, colToModDx, derColName, windowSize = 1):
        startTime = time.time()
        #finds the derivative of the inputted SET based on the windowSize given. 
        storeNewCol = self.csvFileDF[colToModDx].copy()
        lengthCol = storeNewCol.size
        if windowSize >=self.interval: #error protection 
            print("Your interval is too big")
            self.csvFileDF.loc[:, derColName] = storeNewCol
            return
        #goes through everything and calculates the derivative based on each interval
        #timing: O(N) with no threading. unoptimized
        for i in range(0, lengthCol, self.interval):
            for j in range(i, i+self.interval-windowSize):
                if j % windowSize == 0:
                   #will only calculate the current derivative if the denominator is non-zero. If it is 0, then all discontinuities are just made equal to 0
                    if (self.csvFileDF.loc[j+windowSize, colDy]-self.csvFileDF.loc[j, colDy]) == 0:
                        storeNewCol[j] = 0
                    else:
                        storeNewCol[j] = (storeNewCol[j+windowSize]-storeNewCol[j])/(self.csvFileDF.loc[j+windowSize, colDy]-self.csvFileDF.loc[j, colDy])
                else:
                    #all values outside of the window size will become 0. 
                    storeNewCol[j] = 0
            storeNewCol[i+self.interval-windowSize: i+self.interval] = 0 #loads all the end values as 0, just because. 

        self.csvFileDF.loc[:, derColName] = storeNewCol
        self.changedDF = True
        print("End derivative calc", (time.time()-startTime)*1000, "milliseconds")

    def sumDataAll(self, colToMod, sumBounds = None):   
        startTime = time.time()
        #integralBounds is based off of the minimum and maximum coly value desired. [mincoly, maxcoly] #this is next steps
        #returns the integral of each interval returned as a list
        #preliminary: slow. Technically O(N) because only touches each piece of all the data once
        integrals = [0.0]*self.numInter
        lengthCol = self.csvFileDF.loc[:,colToMod].size
        if not sumBounds:
            for i in range(0, lengthCol, self.interval):
                for j in range(i, i+self.interval):
                    integrals[i//self.interval] += self.csvFileDF.loc[j, colToMod] 
        print("End calculate sum all", (time.time()-startTime)*1000, "milliseconds")
        return integrals       

    def integralAllSquare(self, colx, colToMody, integralBounds = None):   
        startTime = time.time()
        #calculates the integral using squares. NOT DONE

        #integralBounds is based off of the minimum and maximum coly value desired. [mincoly, maxcoly] #this is next steps
        #returns the integral of each interval returned as a list
        #preliminary: slow. Technically O(N) because only touches each piece of all the data once
        integrals = [0.0]*self.numInter
        lengthCol = self.csvFileDF.loc[:,colToMody].size
        if not integralBounds:
            for i in range(0, lengthCol, self.interval):
                for j in range(i, i+self.interval-1):
                    integrals[i//self.interval] += self.csvFileDF.loc[j, colToMody]*(self.csvFileDF.loc[j+1, colx]-self.csvFileDF.loc[j, colx]) #calculates the area of each time stamp Goes on lowest side. 
        print("End calculate integral all", (time.time()-startTime)*1000, "milliseconds")
        return integrals


    
    def outline(self, colToMod, outlineColName): 
        startTime = time.time()
        #will pull the interval number which has the biggest area. 
        #this is done through using 2 metrics:
        #1. finding the maximum value of all intervals, keeping track of which interval piece is biggest
        #2. counting up those max values and return the one interval with the most maximums   
        #will read through the storeNewCol Series and identify the biggest values.
        #in it's current phase, it does not handle when more than one interval has an outline. 
        lengthCol = self.csvFileDF.loc[:,colToMod].size
        #maxIndex = [-1]*self.interval
        maxIndexVal = [-9999999]*self.interval
        countMax = [0]*self.numInter
        for i in range(0, lengthCol, self.interval):
           
            for j in range(i, i+self.interval):
                if self.csvFileDF.loc[j, colToMod] > maxIndexVal[j % (self.interval)]:
                    maxIndexVal[j % (self.interval)] = self.csvFileDF.loc[j, colToMod]
                    #maxIndex[j % self.interval ] = (i)/self.interval
                    countMax[int(((i)/self.interval))] += 1
        maxCount = -1
        maxIndex = -1
        for i in range(0, len(countMax)):
            if countMax[i] > maxCount:
                maxCount = countMax[i]
                maxIndex = i
        print("End outline calc", (time.time()-startTime)*1000, "milliseconds")
        return maxIndex

    def averageFilter(self, coly, colToMod, colTitle, numToAverage):
        pass

#test = manipulateSETData('SET Detector Test.csv', loadNewFile = True)



def seeAllPlotsSep(xPlotName, yPlotName, title='Title'):
    listOPlots = [None]*test.numInter
    for i in range(0, test.numInter-1):
        listOPlots[i] = test.plotDataInter([xPlotName, yPlotName], i, showPlot = False, labelNames=[xPlotName, yPlotName, title])
    listOPlots[test.numInter-1] = test.plotDataInter([xPlotName, yPlotName], test.numInter-1, showPlot = False, labelNames=[xPlotName, yPlotName, title])
    strVal = [""]*test.numInter 
    for i in range(0, test.numInter):
        strVal[i] = str(i)
    plt.legend(handles = listOPlots)
    plt.show()

#seeAllPlotsSep('Time', 'Curr Der 2', 'Fancy')

