#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

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

Fetch live weather data from diabox.
See http://data.diabox.com/

Implements
==========

This plugin implements the interface between the diabox site
and domogik

@author: kbu <kbu@kbulabs.fr>
@copyright: (C) 2007-2016 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.xpl.common.xplmessage import XplMessage
from domogik.xpl.common.plugin import XplPlugin

from domogik_packages.plugin_diabox.lib.diabox import Diabox

import threading
import traceback

class DiaboxManager(XplPlugin):
    """ Bin part of the diabox plugin """

    def __init__(self):
        """ The constructor of your class. This function  will be called when the class is instantiated.
        """
        XplPlugin.__init__(self, name='diabox')

        # check if the plugin is configured. If not, this will stop the plugin and log an error
        if not self.check_configured():
            return
        
        self.devices = self.get_device_list(quit_if_no_device = False)

        mysql_host = self.get_config("mysql_host")
        if mysql_host == None:
            self.log.error("Mysql_host seems to be missconfigured ! Check it please ! :-/")
            return

        #put a hard interval
        #interval = 30     
        
        threads = {}
        for dev in self.devices:
            try:
                if not self.check_configured():
                    self.log.error("Device {} is not configured !".format(dev['name']))
                    return
                interval = self.get_parameter(dev, "interval")
                if interval == None:
                    self.log.error("Interval \"{}\" is invalid for device \"{}\"".format(interval, dev['name']))
                    return

                self._timysql_manager = TeleinfoMysql(self.log, self.send_xpl, self.get_stop(), mysql_host, mysql_db, mysql_table, mysql_login, mysql_pwd )
                self.add_stop_cb(self._timysql_manager.stop)

                thr_name = "dev_{}".format(dev['id'])
                self.log.info("[Starting thread {}] Start fetching teleinfo data from mysql for device {}".format(thr_name, dev['name']))
                threads[thr_name] = threading.Thread(None,
                                                    self._timysql_manager.get_last_teleinfo,
                                                    thr_name,
                                                    (interval,),
                                                    {})
                threads[thr_name].start()
                self.register_thread(threads[thr_name])
            except:
                self.log.error("{0}".format(traceback.format_exc()))
                self.log.error("ERROR : exit plugin timysql")
                return

        self.log.info("Plugin \"diabox\" ready :)")
        self.ready()


    def send_xpl(self, teleinfo):
        """ send xPL on the network """
        self.log.debug("Send xPL msg with a line of diabox data")

        #print "callback : receive frame is : \n\n"
        #print teleinfo
        #print "\n\n"

        # creation du message xPL
        msg = XplMessage()
        msg.set_type("xpl-stat")
        #msg.set_schema("sensor.basic")
        msg.set_schema("teleinfo.basic")
        #msg.add_data({"timestamp" : teleinfo["timestamp"]})

        try:
            self.myxpl.send(msg)
        except XplMessageError: 
            self.log.debug(u"Bad xpl message to send. Xpl message is : {0}".format(str(msg)))
            pass

if __name__ == "__main__":
    DiaboxManager()


