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

    def __init__(self, log, callback, stop, dbx_domo_id):
        """ Init TeleinfoMysqlObject
            @param log : log instance
            @param callback : callback
            @param stop : stop
            @param dbx_domo_id : the diabox id (domogik side)
        """
        
        self.log = log
        self._callback = callback # to send and xpl message
        self._stop = stop
        self.log.info("\n\t\t\t\t\t-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
        self.log.info("Starting initialization of plugin_diabox for device {}".format(dbx_name))

        self.dbx_domo_id = dbx_domo_id;
        self.dbx_cfg = diaboxconfig.DiaboxConfig(dbx_domo_id)
        
        if self.dbx_cfg.isValid is not True:
            self.log.error("ERROR DURING DIABOX CONFIGURATION FOR DEVICE \"dbx_domo_id={}\" [config not found !]".format(dbx_domo_id))
            sys.exit(1)
        else:
            self.log.info("Init of plugin \"diabox\" for device \"{}\"-> completed".format(self.dbx_cfg))

    def __del__(self):
       self.log.debug("Nothing to do")

    def stop(self):
        self.log.debug("Nothing to stop")

    def sentDataToDomogik(self, interval):
        """ get the last teleinfo line in database and push to xpl msg""" 
        while not self._stop.isSet():
            try:        
                frame = "test" 
                self.log.debug(frame)
                self._callback(frame)
            except Exception as e :
                self.error.log("Error while sending data for diabox device : {0}".format(self.dbx_cfg.dbx_name))
                self.error.log(e)
            self._stop.wait(interval)


if __name__ == "__main__":
    print("This lib cannot run standalone. Exiting...")
    sys.exit(0)
