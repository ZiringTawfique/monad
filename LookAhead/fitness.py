# -*- coding: utf-8 -*-
"""
Copyright 2015 Ericsson AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

"""
from dbConnection import DB
from datetime import datetime
import datetime
from datetime import timedelta
from datetime import date


class Fitness():

    # Main [class] variables
    diffMinutes = 0
    formatString = '%d-%m-%Y %H:%M'
    formatTime = '%H:%M'
    secondMinute = 60.0
    firstMinute = "00:00"
    lastMinute = "23:59"
    requests = []
    routes = []
    request = []
    requestIndex = []
    requestOut = []
    requestIndexOut = []
    # yesterday = date.today() - timedelta(13)
    x = 0
    yesterday = datetime(2015, 11, 11)



# A decorator is a function that can accept another function as
# a parameter to be able to modify or extend it
    def __init__(self):
        self.runOnce()

    def decorator(afunction):
        # A wrapper function is used to wrap functionalites you want around the original function
        def wrapper(*args):
            # Checks whether or not the original function as been executed once
            if not wrapper.has_run:
                wrapper.has_run = True
                return afunction(*args)
            else:

                pass
        wrapper.has_run = False
        return wrapper

    @decorator
    def runOnce(self):
        db = DB()
        # Setting the start time boundary of request that we want
        startTime = datetime.datetime.combine(Fitness.yesterday, datetime.datetime.strptime(Fitness.firstMinute, Fitness.formatTime).time())
        # Setting the end time boundary of request that we want
        endTime = datetime.combine(Fitness.yesterday, datetime.strptime(Fitness.lastMinute, Fitness.formatTime).time())
        # Create index for the people going on the bus
        Fitness.request = db.grpReqByBusstopAndTime(startTime, endTime)
        self.createRequestIndex(Fitness.request)
        # Create index for the people going down the bus
        Fitness.requestOut = db.getReqCountByEndBusStop(startTime, endTime)
        self.createRequestIndexOut(Fitness.requestOut)

 #<--------------------------------Functions for new encoding including multiple line---------------------------------->

        for x in db.timeSliceArray:
            start = datetime.datetime.combine(Fitness.yesterday,datetime.time(x[0], 0, 0))
            end = datetime.datetime.combine(Fitness.yesterday, datetime.time(x[1], 59, 59))
            requestBetweenTimeSlices = db.getTravelRequestBetween(start, end)

            for count in enumerate(requestBetweenTimeSlices, start=1):
                countingNoOfRequest = (count[0])

            finalNoReqBetweenTimeSlice = countingNoOfRequest

 #<--------------------------------END END END END END----------------------------------------------------------------->



    def timeDiff(self, time1, time2):
        ''' Evaluates the difference between two times.

        Args: time1 and time2 in datetime format, time1 > time2
        Returns: the timedelta between time1 and time2.
        '''
        return datetime.strptime(time1, Fitness.formatTime) - datetime.strptime(time2, Fitness.formatTime)

    def getMinutes(self, td):
        return (td.seconds//Fitness.secondMinute) % Fitness.secondMinute

    def createRequestIndex(self, request):
        ''' Creates a structure that stores the hour, the minute and the position on the request array for this particular time
        
        @param: request (array): Structure that stores the requests grouped by bus stop, hour and minute. It also includes a COUNT column
        '''
        # requestTime = 0
        Fitness.requestIndex.append([request[0]["_id"]["RequestTime"], 0])
        requestTime = request[0]["_id"]["RequestTime"]
        for i in range(1, len(request)):
            if request[i]["_id"]["RequestTime"] != requestTime:
                # Fitness.requestIndex.append([request[i]["_id"]["RequestTime"].day, request[i]["_id"]["RequestTime"].hour, request[i]["_id"]["RequestTime"].minute, i])
                Fitness.requestIndex.append([request[i]["_id"]["RequestTime"], i])
                requestTime = request[i]["_id"]["RequestTime"]

    def searchRequest(self, initialTime, finalTime, busStop, line):
        ''' Search on the request array based on an inital time, a final time and a particular bus stop

        @param: initialTime (datetime): Initial time to perform the request's search
        @param: finalTime (datetime): Final time to perform the request's search
        @param: busStop (string): Bus stop name used on the request's search
        '''
        result = []
        index = self.searchRequestIndex(Fitness.requestIndex, initialTime, finalTime)
        if index != False:
            request = Fitness.request[index[0]:index[1]]
            for i in range(len(request)):
                if request[i]["_id"]["BusStop"] == busStop and request[i]["_id"]["line"] == line:
                    result.append(request[i])
        return result

    def searchRequestIndex(self, index, initialDate, finalDate):
        ''' Search the index to get the position on the request array for a specific time frame
        
        @param: index (array): Structure that stores hour, minute and the request's array position for this time
        @param: initialHour (int): Initial hour to perform the search over the index
        @param: initialMinute (int): Final minute to perform the search over the index
        @param: finalHour (int): Final hour to perform the search over the index
        @param: finalMinute (int): Final minute to perform the search over the index
        '''
        result = []
        position = 0
        # Look for the first index on the search
        for i in range(len(index)):
            if index[i][0] >= initialDate and index[i][0] < finalDate:
                result.append(index[i][1])
                indexDate = index[i][0]
                position = i
                break
            if index[i][0] >= finalDate:
                result.append(False)
                break
        if len(result) == 0:
            result.append(False)
        # Evaluate if the first index was found
        if result[0] != False:
            # If found, look for the second index, however the index has to go backwards
            for j in reversed(range(position, len(index))):
                if index[j][0] > indexDate and index[j][0] <= finalDate:
                    result.append(index[j][1])
                    break
                if index[i][0] <= indexDate:
                    result.append(False)
                    break
        # Check if both values were generated, if not return an array with false values
        if result[0] == False or result[1] == False:
            return False
        else:
            return result
        '''
            if index[i][0] >= initialDate and index[i][1] >= initialDate.hour and index[i][2] >= initialDate.minute:
                result.append(index[i][1])
                break
        # TODO: Watch out with MIDNIGHT trips !!!!
        if len(result) == 0:
            result.append(len(Fitness.request)-1)

        try:
            for i in range(i, len(index)):
                if index[i][0] >= finalDate.day and index[i][1] >= finalDate.hour and index[i][2] >= finalDate.minute:
                    result.append(index[i][3])
                    break
        except UnboundLocalError:
            print "Length of index is " + str(len(index))

        # TODO: Watch out with MIDNIGHT trips !!!!
        if len(result) == 1:
            result.append(len(Fitness.request)-1)
        return result
        '''

    def createRequestIndexOut(self, request):
        ''' Creates a structure that stores the hour, the minute and the position on the request array for this particular time

        @param: request (array): Structure that stores the requests grouped by bus stop, hour and minute. It also includes a COUNT column
        '''
        minute = 0
        for i in range(len(request)):
            if request[i]["_id"]["endTime"].minute != minute or i == 0:
                Fitness.requestIndexOut.append([request[i]["_id"]["endTime"].day, request[i]["_id"]["endTime"].hour, request[i]["_id"]["endTime"].minute, i])
                minute = request[i]["_id"]["endTime"].minute

    def searchRequestIndexOut(self, index, initialDate, finalDate):
        ''' Search the index to get the position on the request array for a specific time frame

        @param: index (array): Structure that stores hour, minute and the request's array position for this time
        @param: initialDate (datetime): Initial datetime to perform the search over the index
        @param: finalDate (finalDate): Final datetime to perform the search over the index
        '''
        result = []
        for i in range(len(index)):
            if index[i][0] >= initialDate.day and index[i][1] >= initialDate.hour and index[i][2] >= initialDate.minute:
                result.append(index[i][3])
                break
        # TODO: Watch out with MIDNIGHT trips !!!!
        if len(result) == 0:
            result.append(len(Fitness.requestOut))

        try:
            for i in range(i, len(index)):
                if index[i][0] >= finalDate.day and index[i][1] >= finalDate.hour and index[i][2] >= finalDate.minute:
                    result.append(index[i][3])
                    break
        except UnboundLocalError:
            print "Length of index is " + str(len(index))

        # TODO: Watch out with MIDNIGHT trips !!!!
        if len(result) == 1:
            result.append(len(Fitness.requestOut))
        return result

    def searchRequestOut(self, initialTime, finalTime, busStop, line):
        ''' Search on the request array based on an inital time, a final time and a particular bus stop

        @param: initialTime (datetime): Initial time to perform the request's search
        @param: finalTime (datetime): Final time to perform the request's search
        @param: busStop (string): Bus stop name used on the request's search
        '''
        result = []
        index = self.searchRequestIndexOut(Fitness.requestIndexOut, initialTime, finalTime)
        request = Fitness.requestOut[index[0]:index[1]]
        for i in range(len(request)):
            if request[i]["_id"]["busStop"] == busStop and request[i]["_id"]["line"] == line:
                result.append(request[i])
        return result

    def getMinutesNextTrip(self, phenotype, currentTime, busStop):
        ''' Find the next earlier time a bus will be on a particular bus stop

        @return: The difference of minutes between the current time and the time for the next trip
        '''
        for gene in phenotype:
            if gene[0] == busStop:
                futureTime = gene[1]
                break
        return self.getMinutesFromTimedelta(futureTime - currentTime)

    def getMinutesFromTimedelta(td):
        return (td.seconds//60) % 60

    def calculateCost(self, individual, totalWaitingTime, penaltyOverCapacity):
        ''' Calculate cost for an individual in the population. 

        @param  individual: individual in the population; 
                totalWaitingTime: total waiting time for that individual
                penaltyOverCapacity: a positive integer to represent a large cost to individual if capacity cannot handle all request of that trip
        @return cost: positive integer for this individual, if input param is out of range, cost will be -1

        Less cost, better individual
        Assume one minute's waiting per person equals to 1kr
        '''
        cost = 0
        costOfBus = [[20, 1000], [60, 1200], [120, 1400]]
        waitingCostPerMin = 1
        busCost = 0
        if penaltyOverCapacity < 0 or individual is None or totalWaitingTime < 0:
            cost = -1
        else:
            for i in range(len(individual)):
                busCapacity = individual[i][1]
                for j in range(len(costOfBus)):
                    if busCapacity == costOfBus[j][0]:
                        busCost = busCost + costOfBus[j][1]
                        break
            waitingCost = totalWaitingTime * waitingCostPerMin
            cost = busCost + waitingCost + penaltyOverCapacity
        return cost
