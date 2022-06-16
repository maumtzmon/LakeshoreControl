#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 10:45:33 2019  @author: Mauricio
updated on Tue May 17 13:11:00 2022  @author: Mauricio

def setSensors/def setCurves
OK->def Read configuration file/def get data V1.0/
OK->main()->read config_file and get data from Model218 and 335 every cycle and print
in the same line



"""

import serial
import time


#get configuration from file
def getDictFromConfigFile(configFileName):
    ConfigDict={}
    for line in open(configFileName):
        if line[0] == "#" :
            #print("skipping comment")
            continue
        if line[0] == "\n" :
            #print("skipping comment")
            continue
        List=line.split(":")
        ConfigDict.setdefault(List[0],List[1].strip()) #strip() quita espacios 
    return ConfigDict

#Simple data acquisition rutine, ask for all the channels and print the result
def getData(Ch,port):
    str2port='KRDG? '+str(Ch)+'\r\n'
    port.write(str2port.encode())
    datos=port.read(79)
    #print(datos )
    datos=datos.decode().strip('\r\n')
    return datos

#Define channel sensor status On/Off
def setSensOn(Config): 
    Ch=1
    out={}
    for key in Config:
        if key[0]=='S':  #Sensor 
            if key[7]=='S':  #Status On/Off
                #set On/Off
                str2port='INPUT '+str(Ch)+','+str(Config.get(key))+'\r\n'
                port.write(str2port.encode())
                time.sleep(.1)
                #read status 
                str2port='INPUT? '+str(Ch)+'\r\n'
                port.write(str2port.encode())
                out.setdefault('Sens '+str(Ch),port.read(79).decode().strip())
                time.sleep(.1)
                Ch=Ch+1
            continue
        continue
    print('Status\r')  #Print On/Iff Settings       
    print(out)
    return 'Done\r\n'


#Set type of curve (from user or standar) in Ch channel
def setCurves(Config): 
    Ch=1
    out={}
    for key in Config:
        if key[0]=='C':   #Curve
            if key[1]=='P':  #Parameter
                #Set curve in Ch channel
                str2port='INCRV '+str(Ch)+','+ str(Config.get(key))+'\r\n'
                port.write(str2port.encode())
                time.sleep(.2)
                #read curve value
                str2port='INCRV? '+str(Ch)+'\r\n'
                port.write(str2port.encode())
                out.setdefault(key,port.read(79).decode().strip())
                time.sleep(.2)
                Ch=Ch+1
            continue
        continue
    print('Curves\r') #Print Curve Settings
    print(out)
    return   'Done\r\n'

#Define type of sensors for Group A (ch 1-4) and B (ch 5-8)
def setSensType(Config): 
    Grupos=['A','B']
    Ch=0
    out={}
    for key in Config:
        if key[0]=='S':#Sensor 
            if key[7]=='T':#Type
                #Set Sensor Type
                str2port='INTYPE '+str(Grupos[Ch])+ ','+ str(Config.get(key))+'\r\n'
                port.write(str2port.encode())
                time.sleep(.1)
                #Read Type Value
                str2port='INTYPE? '+str(Grupos[Ch])+'\r\n'
                port.write(str2port.encode())
                out.setdefault(Grupos[Ch],port.read(79).decode().strip())
                time.sleep(.1)
                Ch=Ch+1
            continue
        continue
    print('Type Gpoups\r') #Print Sensor Type
    print(out)
    return   'Done\r\n'

#get Curve points from sensor file curve .dat
def getDictFromCurveFile(file):
    ConfigDict={} 
    for line in open(file): 
        if line[0] == "S" : 
            if line[7] == "M" :
                List=line.split(":")
                ConfigDict.setdefault(List[0],List[1].strip())
                continue
            if line[7] == "N" :
                List=line.split(":")
                ConfigDict.setdefault(List[0],List[1].strip())
                continue
            if line[9] == "L" :
                List=line.split(":")
                ConfigDict.setdefault(List[0],'{:.5}'.format(List[1].strip()))
                continue
            continue    
        
        if line[0] == "D" : 
            if line[5] == "F" :
                List=line.split(":")
                ConfigDict.setdefault(List[0],'{:.1}'.format(List[1].strip()))
                continue
            continue
            
        if line[0] == "T" :
            if line[12] == "c" :
                List=line.split(":")
                ConfigDict.setdefault(List[0],'{:.1}'.format(List[1].strip()))
                continue
            continue      
                        
        if line[0] == "\n" : 
            continue
        
        if line[0] == "N" :
            continue
        
        else: 
            List=line.split("       ") 
            #print(List)
            List[0]=List[0].split("  ")
            ConfigDict.setdefault(List[0][-1],List[1].strip()) #strip() quita espacios  
        #list 0=kelvin, list 1=ohms
    return ConfigDict

#send curve data to Model 218
def addCurve(CurveDict,Ch,index=1):
             #CRVHDR <Ch 21-28>, <sensName>, <SN>, <format>, <limit value>, <coefficient>
    str2port='CRVHDR '+str(Ch)+','+str(CurveDict['Sensor Model'])+','\
    +str(CurveDict['Serial Number'])+','+str(CurveDict['Data Format'])+','\
    +str(CurveDict['SetPoint Limit'])+','+str(CurveDict['Temperature coefficient'])+'\r\n'
    port.write(str2port.encode())
    time.sleep(.1)
    
    for key in CurveDict:
        
        if key.replace('.','').isdigit() == True :
            #CRVPT <Ch 21-28>, <index>, <units value>, <temp value>
            str2port='CRVPT '+str(Ch)+','+str(index)+','+str(key)+','\
            +str(CurveDict.get(key))+'\r\n'
            index=index+1 
            port.write(str2port.encode())
            time.sleep(.1)
            continue
        
        
    
    return 'Done'

def LocalTime():
    LocalTime = time.strftime("%H:%M:%S  %Y-%m-%d", time.localtime())
    return LocalTime


#-----------------------
#       main
#-----------------------
#Read Conifig File
def main():
    print('####Temp monitor lite####\n\nWatch the sensor control live.\nNOTE:To stop monitoring "Ctrl+C"\n')
    try:
        ConfigDict_218=getDictFromConfigFile('config_file')
        ok218Flag=True
    except:
        print('no config for 218 detected')
        ok218Flag=False
    try:
        ConfigDict_335=getDictFromConfigFile('ConfigFile_M335')
        ok335Flag=True
    except:
        print('no config for 335 detected')
        ok335Flag=False

    #print(ConfigDict) #Check If all parameters are in the Dictionary
    ConfigDict={}



    #config Serial Port with config_file settings
    try:
        port_218= serial.Serial(ConfigDict_218['Port'], ConfigDict_218['BaudRate'], serial.SEVENBITS,\
                    serial.PARITY_ODD, serial.STOPBITS_ONE, float(ConfigDict_218['TimeOut']))
        ok218Flag=True
    except:
        print('no model 218 detected') #else
        ok218Flag=False

    try:
        port_335= serial.Serial(ConfigDict_335['Port'], ConfigDict_335['BaudRate'], serial.SEVENBITS,\
                    serial.PARITY_ODD, serial.STOPBITS_ONE, float(ConfigDict_335['TimeOut']))
        ok335Flag=True
    except:
        print('no model 335 detected')    #else
        ok335Flag=False

    #Run Configuration Functions.
    # print a list with settings and "Done" at the end of each one

    #print(setSensType(ConfigDict))
    #print(setCurves(ConfigDict))
    #print(setSensOn(ConfigDict))
    #CurveDict=getDictFromCurveFile('X133491\X133491.340')
    #print(addCurve(CurveDict,26))
    #CurveDict=getDictFromCurveFile('X133492\X133492.340')
    #print(addCurve(CurveDict,25))

    ##
    date=time.strftime("%Y%b%d", time.localtime())

    file=open('history_'+date+'.txt', 'a')
    file.close()

    while ok218Flag or ok335Flag:    
        with open('history_'+date+'.txt', 'a', encoding="utf-8") as file:

            try:
                if ok218Flag:
                    ConfigDict=ConfigDict_218
                    string_218=getData(ConfigDict['Channels'],port_218)
                if ok335Flag:
                    ConfigDict=ConfigDict_335
                    string_A=getData(ConfigDict['Channel 1'],port_335)
                    string_B=getData(ConfigDict['Channel 2'],port_335)
                    string_335=string_A+', '+string_B
                if ok218Flag and ok335Flag:
                    print(LocalTime()+','+string_218+','+string_335, end='\r')
                elif ok218Flag:
                    print(LocalTime()+','+string_218, end='\r')
                elif ok335Flag:
                    data2print=LocalTime()+', '+string_335
                    print(data2print, end='\r')
                    file.write(data2print+'\n')
                else:
                    print('no sensors are conected')
            except KeyboardInterrupt:
                print('proceso interrumpido')
                break

if __name__ == "__main__":
    main()

