#!/usr/bin/python
# -*-coding:Utf-8 -*

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

    def __init__(self, log, callback, stop, dbx_dev_type, domogik_dev_id, interval):
        """ Init TeleinfoMysqlObject
            @param log : log instance
            @param callback : callback
            @param stop : stop
            @param dev_type : domogik device_type_id (diabox.minou / diabox.wrach) configured in info.json
        """
        
        self.log = log
        self._callback = callback # to send and xpl message
        self._stop = stop
        self.domogik_dev_id = domogik_dev_id
        self.refresh_interval = interval
        self.log.info("\n\t\t\t\t\t-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
        self.log.info("Starting initialization of plugin_diabox for device type {}".format(dbx_dev_type))

#        self.dbx_domo_id = dbx_domo_id;
        self.cfg = DiaboxConfig.DiaboxConfig(dbx_dev_type, self.log)
        
        if self.cfg.isValid is not True:
            self.log.error("ERROR DURING DIABOX CONFIGURATION FOR DEVICE \"dbx_domo_id={}\" [config not found !]".format(dbx_domo_id))
            sys.exit(1)
        else:
            self.log.info("Init of plugin \"diabox\" for station \"{}\"-> completed".format(self.cfg.station_name))

    def __del__(self):
       self.log.debug("Nothing to do")

    def stop(self):
        self.log.debug("Nothing to stop")

    def get_dbx_temp(self):
        try:
            # do the request
            r = requests.get(self.cfg.url_temperature)

            #check if http request is successful [code 200]
            if r.status_code != 200:
                self.log.error("dbx \"{}\" / data type \"{}\" => HTTP REQUEST ERROR [return code : {}]".format(self.cfg.station_name, "temperature", r.status_code))
                return None
            else:
                #check that content is not null (greater than 5 car.)
                if r.headers["Content-Length"] < 5:
                    self.log.error("dbx \"{}\" / data type \"{}\" => http response contains no data !! [\"Content-Length\"='{}']".format(self.cfg.station_name, "temperature", r.headers["Content-Length"]))
                    return None
        except Exception as e :
            self.log.error("Exception while requesting data \"temperature\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None

        try:
            json_tab = json.loads(r.content)
            dbx_data = json_tab[0]
            temp = dbx_data["val"]
            self.log.debug("station {} => http request OK for data type \"temp\" [get temp={} °C]"
                    .format(self.cfg.station_name, temp))
            return temp
        except Exception as e:
            self.log.error("Exception while processing data \"temperature\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None
            
    def get_dbx_pressure(self):
        try:
            # do the request
            r = requests.get(self.cfg.url_pressure)

            #check if http request is successful [code 200]
            if r.status_code != 200:
                self.log.error("dbx \"{}\" / data type \"{}\" => HTTP REQUEST ERROR [return code : {}]".format(self.cfg.station_name, "pressure", r.status_code))
                return None
            else:
                #check that content is not null (greater than 5 caract.)
                if r.headers["Content-Length"] < 5:
                    self.log.error("dbx \"{}\" / data type \"{}\" => http response contains no data !! [\"Content-Length\"='{}']".format(self.cfg.station_name, "pressure", r.headers["Content-Length"]))
                    return None
        except Exception as e :
            self.log.error("Exception while requesting data \"pressure\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None

        try:
            json_tab = json.loads(r.content)
            dbx_data = json_tab[0]
            cur_hpa = dbx_data["val"]
            self.log.debug("station {} => http request OK for data type \"pressure\" [get pressure={} hpa]"
                    .format(self.cfg.station_name, cur_hpa))
            return cur_hpa
        except Exception as e:
            self.log.error("Exception while processing data \"pressure\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None
            
    def get_dbx_wind(self):
        """ getting the wind live data... /!\ : url_wind_speed & url_wind_direction in in fact the same ! We get a array with both information, so no need to send 2 requests, but I code in this way in case of... maybe one day it'll be useful """

        try:
            # do the request (wind_speed & wind_direction is the same url. Get an array from website)
            r = requests.get(self.cfg.url_wind_speed)

            #check if http request is successful [code 200]
            if r.status_code != 200:
                self.log.error("dbx \"{}\" / data type \"{}\" => HTTP REQUEST ERROR [return code : {}]".format(self.cfgi.station_name, "wind_data", r.status_code))
                return None
            else:
                #check that content is not null (greater than 5 caract.)
                if r.headers["Content-Length"] < 5:
                    self.log.error("dbx \"{}\" / data type \"{}\" => http response contains no data !! [\"Content-Length\"='{}']".format(self.cfg.station_name, "wind_data", r.headers["Content-Length"]))
                    return None
        except Exception as e :
            self.log.error("Exception while requesting data \"wind_data\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None

        try:
            json_tab = json.loads(r.content)
            dbx_data = json_tab[0]
            cur_wind_direction = dbx_data["dir"]
            cur_wind_kts = dbx_data["force"]
            self.log.debug("station {} => http request OK for data type \"wind\" [get dir={}° and speed={} kts]"
                    .format(self.cfg.station_name, cur_wind_direction, cur_wind_kts))
            cur_wind_data={}
            cur_wind_data["speed"]=cur_wind_kts
            cur_wind_data["direction"]=cur_wind_direction
            return cur_wind_data
        except Exception as e:
            self.log.error("Exception while processing data \"pressure\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None
            
    def get_dbx_humidity(self):
        try:
            # do the request
            r = requests.get(self.cfg.url_humidity)

            #check if http request is successful [code 200]
            if r.status_code != 200:
                self.log.error("dbx \"{}\" / data type \"{}\" => HTTP REQUEST ERROR [return code : {}]".format(self.cfg.station_name, "humidity", r.status_code))
                return None
            else:
                #check that content is not null (greater than 5 caract.)
                if r.headers["Content-Length"] < 5:
                    self.log.error("dbx \"{}\" / data type \"{}\" => http response contains no data !! [\"Content-Length\"='{}']".format(self.cfg.station_name, "humidity", r.headers["Content-Length"]))
                    return None
        except Exception as e :
            self.log.error("Exception while requesting data \"humidity\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None

        try:
            json_tab = json.loads(r.content)
            dbx_data = json_tab[0]
            cur_hum = dbx_data["val"]
            self.log.debug("station {} => http request OK for data type \"humidity\" [get humidity={}%]"
                    .format(self.cfg.station_name, cur_hum))
            return cur_hum
        except Exception as e:
            self.log.error("Exception while processing data \"humidity\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None
    
    def get_dbx_rainrate(self):
        try:
            # do the request
            r = requests.get(self.cfg.url_rain_rate)

            #check if http request is successful [code 200]
            if r.status_code != 200:
                self.log.error("dbx \"{}\" / data type \"{}\" => HTTP REQUEST ERROR [return code : {}]".format(self.cfg.station_name, "rain_rate", r.status_code))
                return None
            else:
                #check that content is not null (greater than 5 caract.)
                if r.headers["Content-Length"] < 5:
                    self.log.error("dbx \"{}\" / data type \"{}\" => http response contains no data !! [\"Content-Length\"='{}']".format(self.cfg.station_name, "rain_rate", r.headers["Content-Length"]))
                    return None
        except Exception as e :
            self.log.error("Exception while requesting data \"rain_rate\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None

        try:
            json_tab = json.loads(r.content)
            dbx_data = json_tab[0]
            cur_rain = dbx_data["val"]
            self.log.debug("station {} => http request OK for data type \"rain_rate\" [get rain_rate={} mm/h]"
                    .format(self.cfg.station_name, cur_rain))
            return cur_rain
        except Exception as e:
            self.log.error("Exception while processing data \"rain_rate\" for diabox station \"{}\"".format(self.cfg.station_name))
            self.log.error(e)
            return None
            

    def get_diabox_data(self):
        """ this function is responsible to fetch data and to push them to domogik """
        while not self._stop.isSet(): 
            try:
                ###### temperature #######
                cur_temp = self.get_dbx_temp();
                if cur_temp == None:
                    self.log.info("No data for sensor temp for diabox \"{}\"".format(self.cfg.station_name))
                else:
                    self.log.debug("Trying to send a \"temp\" for diabox station \"{}\""
                            .format(self.cfg.station_name))
                    self.sentDataToDomogik("Temperature", "temperature", cur_temp) #try to auto this ?
                
                ###### pressure #######
                cur_hpa = self.get_dbx_pressure();
                if cur_hpa == None:
                    self.log.info("No data for sensor pressure for diabox \"{}\"".format(self.cfg.station_name))
                else:
                    self.log.debug("Trying to send a \"pressure\" for diabox station \"{}\""
                            .format(self.cfg.station_name))
                    self.sentDataToDomogik("Pressure", "pressure", cur_hpa) #try to auto this ?
                
                ###### wind data #######
                cur_wind_data = self.get_dbx_wind();
                if cur_wind_data == None:
                    self.log.info("No data for wind sensor for diabox \"{}\"".format(self.cfg.station_name))
                else:
                    self.log.debug("Trying to send some \"wind data\" for diabox station \"{}\""
                            .format(self.cfg.station_name))

                    self.sentDataToDomogik("Wind speed", "windspeed", cur_wind_data["speed"]) #try to auto this ?
                    self.sentDataToDomogik("Wind direction", "winddirection", cur_wind_data["direction"]) #try to auto this ?
                ###### humidity #######
                cur_hum = self.get_dbx_humidity();
                if cur_hum == None:
                    self.log.info("No data for humidity sensor for diabox \"{}\"".format(self.cfg.station_name))
                else:
                    self.log.debug("Trying to send a \"humidity\" for diabox station \"{}\""
                            .format(self.cfg.station_name))
                    self.sentDataToDomogik("Humidity", "humidity", cur_hum) #try to auto this ?
                    
                ###### rain rate #######
                cur_rain = self.get_dbx_rainrate();
                if cur_rain == None:
                    self.log.info("No data for rain_rate sensor for diabox \"{}\"".format(self.cfg.station_name))
                else:
                    self.log.debug("Trying to send a \"rain_rate\" for diabox station \"{}\""
                            .format(self.cfg.station_name))
                    self.sentDataToDomogik("Rain rate", "rainrate", cur_rain) #try to auto this ?

            except Exception as e :
                self.log.error("!!! EXCEPTION WHILE GETTING/SENDING DIABOX DATA !!!")
                self.log.error(e)

            self._stop.wait(self.refresh_interval)


    def sentDataToDomogik(self, sensor_name, sensor_type, cur_val):
        """ send the cur_val for sensor_name to domogik as a xpl msg"""             
        self._callback(self.domogik_dev_id, self.cfg.station_name, sensor_name, sensor_type, cur_val)


if __name__ == "__main__":
    print("This lib cannot run standalone. Exiting...")
    sys.exit(0)
