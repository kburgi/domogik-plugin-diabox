#!/usr/bin/python
# -*-coding:Utf-8 -*


"""This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Fetch live weather data from diabox station
See http://data.diabox.com/ for more informations

Implements
==========

This plugin implements the interface between a diabox station
and domogik db.

@author: kbu <kbu@kbulabs.fr>
@copyright: (C) 2007-2016 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import sys
import traceback
import json
import datetime

try:
    import requests
except Exception as e:
    print("--------------------------------------------")
    print("Unable to import requests module for Python !")
    print("Is it installed ? (pip install requests) ")
    print("--------------------------------------------")
    print(e)
    sys.exit(1)
    
try:
    import diaboxconfig as DiaboxConfig
except Exception as e:
    print("--------------------------------------------")
    print("Unable to import diaboxconfig module !!")
    print("=> Check presence and syntax in plugin lib folder ")
    print("--------------------------------------------")
    print(e)
    sys.exit(1)


class DiaboxLib():
    """ Diabox station Manager """

    def __init__(self, log, callback, stop, dbx_dev_type, domogik_dev_id, interval, xpl_uid):
        """ Init Diabox Object
            @param log : log instance
            @param callback : callback
            @param stop : stop
            @param dev_type : domogik device_type_id (ex : diabox.minou / diabox.wrach) configured in info.json
            @param domogik_dev_id : the id of the created device in domogik
            @param interval : the time in seconds between two requests of data for the current diabox station
            @param domogik_xpl_uid : the xpl unique identifier configured for each station (xPL parameters when creating a device). This value MUST be unique !
        """
        
        self.log = log
        self._callback = callback
        self._stop = stop
        self.domogik_dev_id = domogik_dev_id
        self.xpl_uid = xpl_uid;
        self.refresh_interval = interval

        self.cfg = DiaboxConfig.DiaboxConfig(dbx_dev_type, self.log)
        if self.cfg.isValid is not True:
            self.log.error("ERROR DURING DIABOX CONFIGURATION FOR DEVICE \"domo_dev_id={}\" [config not found !]"
                    .format(domogik_dev_id))
            self.isConfigured=False
        else:
            self.log.info("Init of plugin \"diabox\" for dbx_dev_type \"{}\"-> completed".format(self.cfg.station_name))
            self.isConfigured=True

    def __del__(self):
       self.log.debug("[domogik_dev_id={}][xpl_uid={}] Deleting DiaboxLib object ".format(self.domogik_dev_id, self.xpl_uid))

    def stop(self):
        self.log.debug("[domogik_dev_id={}][xpl_uid={}] Stopping my thread !".format(self.domogik_dev_id, self.xpl_uid))

    def get_dbx_temp(self):
        """ Request the current temperature from the diabox station """
        try:
            # do the request
            r = requests.get(self.cfg.sensors_url["temperature"])

            #check if http request is successful [code 200]
            if r.status_code != 200:
                self.log.error("dbx \"{}\" / data type \"{}\" => HTTP REQUEST ERROR [return code : {}]"
                        .format(self.cfg.station_name, "temperature", r.status_code))
                return None
            else:
                #check that content is not null (greater than 5 car. [arbitrary value])
                if r.headers["Content-Length"] < 5:
                    self.log.error("[dbx=\"{}\"][data_type=\"{}\"] http response contains no data !! [\"Content-Length\"='{}']"
                            .format(self.cfg.station_name, "temperature", r.headers["Content-Length"]))
                    return None
        except Exception as e :
            self.log.error("Exception while requesting data \"temperature\" for diabox station \"{}\""
                    .format(self.cfg.station_name))
            self.log.error(e)
            return None

        try:
            json_tab = json.loads(r.content)
            dbx_data = json_tab[0]
            temp = dbx_data["val"]
            self.log.debug("[dbx=\"{}\"] http request OK for data type \"temp\" [get temp={} °C]"
                    .format(self.cfg.station_name, temp))
            return temp
        except Exception as e:
            self.log.error("Exception while processing data \"temperature\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None
            
    def get_dbx_pressure(self):
        """ Request the pressure from the diabox station """
        try:
            # do the request
            r = requests.get(self.cfg.sensors_url["pressure"])

            #check if http request is successful [code 200]
            if r.status_code != 200:
                self.log.error("[dbx=\"{}\"][data_type=\"{}\"] HTTP REQUEST ERROR [return code : {}]"
                        .format(self.cfg.station_name, "pressure", r.status_code))
                return None
            else:
                #check that content is not null (greater than 5 caract.)
                if r.headers["Content-Length"] < 5:
                    self.log.error("[dbx=\"{}\"][data_type=\"{}\"] http response contains no data !! [\"Content-Length\"='{}']"
                            .format(self.cfg.station_name, "pressure", r.headers["Content-Length"]))
                    return None
        except Exception as e :
            self.log.error("Exception while requesting data \"pressure\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None

        try:
            json_tab = json.loads(r.content)
            dbx_data = json_tab[0]
            cur_hpa = dbx_data["val"]
            self.log.debug("[dbx=\"{}\"] http request OK for data type \"pressure\" [get pressure={} hpa]"
                    .format(self.cfg.station_name, cur_hpa))
            return cur_hpa
        except Exception as e:
            self.log.error("Exception while processing data \"pressure\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None
            
    def get_dbx_wind(self):
        """ Request the wind speed (in knots) and direction (in °) from the diabox station

            /!\ Important note /!\ 
            ======================
            url_wind_speed & url_wind_direction is the same in fact ! 
            With one url request, we get a array with both speed and direction information. 
            No need to send 2 requests            
        """

        try:
            # do the request (wind_speed & wind_direction is the same url. Got an array from website)
            r = requests.get(self.cfg.sensors_url["wind_speed_kts"])

            #check if http request is successful [code 200]
            if r.status_code != 200:
                self.log.error("[dbx=\"{}\"][data_type=\"{}\"] HTTP REQUEST ERROR [return code : {}]"
                        .format(self.cfgi.station_name, "wind_data", r.status_code))
                return None
            else:
                #check that content is not null (greater than 5 caract.)
                if r.headers["Content-Length"] < 5:
                    self.log.error("[dbx=\"{}\"][data_type=\"{}\"] http response contains no data !! [\"Content-Length\"='{}']"
                            .format(self.cfg.station_name, "wind_data", r.headers["Content-Length"]))
                    return None
        except Exception as e :
            self.log.error("Exception while requesting data \"wind_data\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error("Exception is : {}".format(e))
            return None

        try:
            json_tab = json.loads(r.content)
            dbx_data = json_tab[0]
            cur_wind_direction = dbx_data["dir"]
            cur_wind_kts = dbx_data["force"]
            self.log.debug("[dbx=\"{}\"] http request OK for data type \"wind\" [get dir={}° and speed={} kts]"
                    .format(self.cfg.station_name, cur_wind_direction, cur_wind_kts))
            cur_wind_data={}
            cur_wind_data["speed"]=cur_wind_kts
            cur_wind_data["direction"]=cur_wind_direction
            return cur_wind_data
        except Exception as e:
            self.log.error("Exception while processing data \"Wind\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None
            
    def get_dbx_humidity(self):
        """ Request the humidty from the diabox station """
        try:
            # do the request
            r = requests.get(self.cfg.sensors_url["humidity"])

            #check if http request is successful [code 200]
            if r.status_code != 200:
                self.log.error("[dbx=\"{}\"][data_type=\"{}\"] HTTP REQUEST ERROR [return code : {}]"
                        .format(self.cfg.station_name, "humidity", r.status_code))
                return None
            else:
                #check that content is not null (greater than 5 caract.)
                if r.headers["Content-Length"] < 5:
                    self.log.error("[dbx=\"{}\"][data_type=\"{}\"] http response contains no data !! [\"Content-Length\"='{}']"
                            .format(self.cfg.station_name, "humidity", r.headers["Content-Length"]))
                    return None
        except Exception as e :
            self.log.error("Exception while requesting data \"humidity\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None

        try:
            json_tab = json.loads(r.content)
            dbx_data = json_tab[0]
            cur_hum = dbx_data["val"]
            self.log.debug("[dbx=\"{}\"] http request OK for data type \"humidity\" [get humidity={}%]"
                    .format(self.cfg.station_name, cur_hum))
            return cur_hum
        except Exception as e:
            self.log.error("Exception while processing data \"humidity\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None
    
    def get_dbx_rainrate(self):
        """ Request the rain rate from the diabox station """
        try:
            # do the request
            r = requests.get(self.cfg.sensors_url["rain_rate"])

            #check if http request is successful [code 200]
            if r.status_code != 200:
                self.log.error("[dbx=\"{}\"][data_type=\"{}\"] HTTP REQUEST ERROR [return code : {}]"
                        .format(self.cfg.station_name, "rain_rate", r.status_code))
                return None
            else:
                #check that content is not null (greater than 5 caract.)
                if r.headers["Content-Length"] < 5:
                    self.log.error("[dbx=\"{}\"][data_type=\"{}\"] http response contains no data !! [\"Content-Length\"='{}']"
                            .format(self.cfg.station_name, "rain_rate", r.headers["Content-Length"]))
                    return None
        except Exception as e :
            self.log.error("Exception while requesting data \"rain_rate\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None

        try:
            json_tab = json.loads(r.content)
            dbx_data = json_tab[0]
            cur_rain = dbx_data["val"]
            self.log.debug("[dbx= \"{}\"] http request OK for data type \"rain_rate\" [get rain_rate={} mm/h]"
                    .format(self.cfg.station_name, cur_rain))
            return cur_rain
        except Exception as e:
            self.log.error("Exception while processing data \"rain_rate\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None
            

    def get_diabox_data(self):
        """ this function is responsible to fetch all live data and to push them to domogik via xPL """
        while not self._stop.isSet(): 
            try:
                ###### temperature #######
                if "temperature" in self.cfg.sensors_url:
                    cur_temp = self.get_dbx_temp()
                    if cur_temp == None:
                        self.log.error("Oh Oh : Strange ! No data for sensor temp for diabox \"{}\""
                                .format(self.cfg.station_name))
                    else:
                        cur_temp = round(cur_temp, 1)
                        self.log.debug("Trying to send a \"temp\" for diabox station \"{}\""
                                .format(self.cfg.station_name))
                        self.sentDataToDomogik("Temperature", "temperature", cur_temp) #try to auto this ?
                else:
                    sys.log.debug("No temperature sensor for diabox station \"{}\"".format(self.cfg.station_name))
                
                ###### pressure #######
                if "pressure" in self.cfg.sensors_url:
                    cur_hpa = self.get_dbx_pressure()
                    if cur_hpa == None:
                        self.log.error("Oh Oh : Strange ! No data for sensor pressure for diabox \"{}\""
                                .format(self.cfg.station_name))
                    else:
                        cur_hpa = round(cur_hpa)
                        self.log.debug("Trying to send a \"pressure\" for diabox station \"{}\""
                                .format(self.cfg.station_name))
                        self.sentDataToDomogik("Pressure", "pressure", cur_hpa) #try to auto this ?
                else:
                    sys.log.debug("No pressure sensor for diabox station \"{}\"".format(self.cfg.station_name))
                
                ###### wind data #######
                if "wind_speed_kts" in self.cfg.sensors_url:
                    cur_wind_data = self.get_dbx_wind()
                    if cur_wind_data == None:
                        self.log.error("Oh Oh : Strange ! No data received for wind sensor for diabox \"{}\""
                                .format(self.cfg.station_name))
                    else:
                        cur_wind_speed_kts = round(cur_wind_data["speed"], 1)
                        cur_wind_direction = round(cur_wind_data["direction"], 1)
                        self.log.debug("Trying to send some \"wind data\" for diabox station \"{}\""
                                .format(self.cfg.station_name))

                        self.sentDataToDomogik("Wind speed", "windspeed", cur_wind_speed_kts) #try to auto this ?
                        self.sentDataToDomogik("Wind direction", "winddirection", cur_wind_direction) #try to auto this ?
                else:
                    sys.log.debug("No wind sensor for diabox station \"{}\"".format(self.cfg.station_name))
                
                ###### humidity #######
                if "humidity" in self.cfg.sensors_url:
                    cur_hum = self.get_dbx_humidity()
                    if cur_hum == None:
                        self.log.error("Oh Oh : Strange ! No data for humidity sensor for diabox \"{}\""
                                .format(self.cfg.station_name))
                    else:
                        cur_hum = round(cur_hum, 1)
                        self.log.debug("Trying to send a \"humidity\" for diabox station \"{}\""
                                .format(self.cfg.station_name))
                        self.sentDataToDomogik("Humidity", "humidity", cur_hum) #try to auto this ?
                else:
                    sys.log.debug("No humidity sensor for diabox station \"{}\"".format(self.cfg.station_name))
                    
                ###### rain rate #######
                if "rain_rate" in self.cfg.sensors_url:
                    cur_rain = round(self.get_dbx_rainrate(), 1)
                    if cur_rain == None:
                        self.log.error("Oh Oh : Strange ! No data for rain_rate sensor for diabox \"{}\""
                                .format(self.cfg.station_name))
                    else:
                        cur_rain = round(cur_rain, 1)
                        self.log.debug("Trying to send a \"rain_rate\" for diabox station \"{}\""
                                .format(self.cfg.station_name))
                        self.sentDataToDomogik("Rain rate", "rainrate", cur_rain) #try to auto this ?
                else:
                    sys.log.debug("No rain_rate sensor for diabox station \"{}\"".format(self.cfg.station_name))

            except Exception as e :
                self.log.error("!!! EXCEPTION WHILE GETTING/SENDING DIABOX DATA [dbx=\"{}\"][xpl_uid=\"{}\"]!!!"
                        .format(self.cfg.station_name, self.xpl_uid))
                self.log.error(e)

            # waiting
            self._stop.wait(self.refresh_interval)


    def sentDataToDomogik(self, sensor_name, sensor_type, cur_val):
        """ send the cur_val for sensor_name to domogik as a xpl msg"""             
        self._callback(self.domogik_dev_id, self.xpl_uid, self.cfg.station_name, sensor_name, sensor_type, cur_val)


if __name__ == "__main__":
    print("This lib cannot run standalone. Exiting...")
    sys.exit(0)
