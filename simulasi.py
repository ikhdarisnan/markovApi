#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 16:11:06 2019

@author: ikhdarisnan
"""
#Run this file with virutal environtment flask /home/myMarkovProject/TA_Markov/
from flask import Flask, jsonify
from flask_mysqldb import MySQL
#import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import ast, requests, json

app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_kasir_pulsa'

mysql = MySQL(app)

@app.route('/')
def index():
    return '<h1>This Site already used for Kasir Pulsa App. Mari doakan kelulusan idar! </h1> <h2>Thank you for visiting this site</h2>'
    
    
    
    
@app.route('/getModelMarkov/<string:waktu>', methods=['GET'])
def route(waktu):
    global resultdataTotal, resultdataTrainState, resultdataTestState, resultmyState, resultlastState, resultanomalyDetected, resultnormalDetected
    global fintCurrentState , fintransitionMatrix, finmyTrain, finmyTest, finmyStates, fintime, finlabelAnomay, finlabelNormal 
    global response 

    url = "http://cintanegaraku.id/getMarkov.php"
    result = requests.get(url)
    #print(result.text)
    finresult = json.loads(result.text)
    
    if finresult != 0:    
        for row in finresult:
            resultdataTotal = row['dataTotal']
            resultdataTrainState = row['dataTrainState']
            resultdataTestState = row['dataTestState']
            resultmyState= row['myState']
            resultlastState = row['lastState']
            resultanomalyDetected = row['anomalyDetected']
            resultnormalDetected = row['normalDetected']
    else:
        response = {'code':0, 'message':"rows not available"}
        return jsonify(response)
        
    #START MARKOV CHAIN
    #Convert String list to list array
    tempTransitionMatrix = ast.literal_eval((resultdataTotal))
    myTrain = ast.literal_eval(resultdataTrainState)
    myTest = ast.literal_eval(resultdataTestState)
    #myStates = ast.literal_eval(resultmyState)
    lastState = resultlastState
    labelAnomaly = ast.literal_eval(resultanomalyDetected)
    labelNormal = ast.literal_eval(resultnormalDetected)
    
    time = waktu
    myTest.append(time)
    
    def convertToFloat():
        for i in range (len(myTrain)):
            myTrain[i] = float(myTrain[i])
        for j in range (len(myTest)):
            myTest[j] = float(myTest[j])
    
    def findMaxStates():
        global max_state
        max_state = 0
        
        for i in range(0,len(myTrain)):
            if float(myTrain[i]) > max_state:
                max_state = float(myTrain[i])
                
        for j in range(0,len(myTest)):
            if (float(myTest[j]) > max_state):
                max_state = float(myTest[j])
                    
        return max_state
    
    def initState(max):
        #Get 1st digit decimal value
        global myStates
        global transitionMatrix 
        transitionMatrix = []
        myStates = []
        
        for i in np.arange(0,max+0.1,0.1):
            slicer = ("{0:.1f}".format(i))
            myStates.append(slicer)
            
        #Initiate Matrix nxn
        for cCS in range(0,(int(max*10))+1):
            temperatur=[]  
            for cNS in range(0,(int(max*10)+1)):
                for cTLength in range (0,len(myStates)):
                        temp = 0
                temperatur.append(temp)      
            transitionMatrix.append(temperatur)
        
        for n in range(0, len(tempTransitionMatrix)):
            for k in range(0, len(tempTransitionMatrix)):
                transitionMatrix[n][k] = tempTransitionMatrix[n][k]
            
    def markovStart():
        global tCurrentState, status
        anomx = []
        anomy = []
        normx = []
        normy = []
        tCurrentState = str(lastState)
        
        for naon in range(0,len(myTest)):
            tNextState = str(myTest[naon])
            for tcounter in range (len(myStates)):
                if myStates[tcounter] == tCurrentState:
                    idxCS = myStates.index(tCurrentState)
                if myStates[tcounter] == tNextState:
                    idxNS = myStates.index(tNextState)
            if transitionMatrix[idxCS][idxNS] == 0:
                labelAnomaly.append(tNextState)
                anomx.append(float(tCurrentState))
                anomy.append(float(tNextState))
                status = "anomaly"
            else:
                labelNormal.append(tNextState)
                tCurrentState = myTest[naon]
                normx.append(float(tCurrentState))
                normy.append(float(tNextState))
                status = "normal"
                
        return status
    
    
    #Start Method
    findMaxStates()
    initState(findMaxStates())
    markovStart()
    
    response = {'code':1, 'value': time, 'message':markovStart()}
    convertToFloat()
    
    for k in range(len(myStates)):
        myStates[k] = float(myStates[k])
    for l in range (len(labelAnomaly)):
        labelAnomaly[l] = float(labelAnomaly[l])
    for m in range (len(labelNormal)):
        labelNormal[m] = float(labelNormal[m])
            
    #Convert All array object to String
    fintCurrentState = str(tCurrentState)
    fintransitionMatrix = str(transitionMatrix)
    finmyTrain = str(myTrain)
    finmyTest = str(myTest)
    finmyStates = str(myStates)
    fintime = str(time)
    finlabelAnomaly = str(labelAnomaly)
    finlabelNormal = str(labelNormal)
    
    def update():
#        identity = '1'
        dataTotal = fintransitionMatrix
        dataTrainState = finmyTrain
        dataTestState = finmyTest
        myState = finmyStates
        LastState = fintCurrentState
        anomalyDetected = finlabelAnomaly
        normalDetected = finlabelNormal
        insertedData = fintime
        
        data = {'dataTotal': dataTotal, 'dataTrainState': dataTrainState, 'dataTestState': dataTestState, 'myState': myState, 'lastState': LastState, 'anomalyDetected': anomalyDetected, 'normalDetected': normalDetected, 'insertedData':insertedData}
        postUrl ="http://cintanegaraku.id/updateMarkov.php"
        myUpdate = requests.post(postUrl, data)
        print(myUpdate.status_code)
    #update database
    update()
    
    #return markov result
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)