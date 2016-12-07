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
                #check that content is not null
                if r.headers["Content-Length"] == '0':
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
            

    def get_diabox_data(self):
        """ this function is responsible to fetch data and to push them to domogik """
        while not self._stop.isSet(): 
            try:
                temp = self.get_dbx_temp();
                if temp == None:
                    self.log.info("No data for sensor temp for diabox \"{}\"".format(self.cfg.station_name))
                else:
                    self.log.debug("Trying to send a \"temp\" for diabox station \"{}\""
                            .format(self.cfg.station_name))
                    self.sentDataToDomogik("Temperature", "temperature", temp) #try to auto this ?


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
