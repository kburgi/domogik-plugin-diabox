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

from domogik_packages.plugin_diabox.lib.diaboxlib import DiaboxLib

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

        threads = {}
        for dev in self.devices:
            try:
                if not self.check_configured():
                    self.log.error("Device {} is not configured !".format(dev['name']))
                    return

                dbx_domo_id=dev['id']

                refresh_interval = self.get_parameter(dev,"interval")
                if refresh_interval == None:
                    self.log.error("Interval \"{}\" is invalid for device \"{}\"".format(refresh_interval, dev['name']))                
                    return

                self._diabox_manager = DiaboxLib(self.log, self.send_xpl, self.get_stop(), dbx_domo_id )
                self.add_stop_cb(self._diabox_manager.stop)

                thr_name = "diabox_{}".format(dev['name'])
                self.log.info("[Starting thread {}] Start fetching diabox data".format(thr_name))
                threads[thr_name] = threading.Thread(None,
                                                    self._diabox_manager.get_diabox_data,
                                                    thr_name,
                                                    (refresh_interval,),
                                                    {})
                threads[thr_name].start()
                self.register_thread(threads[thr_name])
            except:
                self.log.error("{0}".format(traceback.format_exc()))
                self.log.error("ERROR : exit plugin diabox")
                return

        self.log.info("Plugin \"diabox\" ready :)")
        self.ready()


    def send_xpl(self, dbx_dev, dbx_type, dbx_value):
        """ send xPL on the network """
        self.log.debug("Send xPL msg with a line of diabox data")
        self.log.debug("with value : {}  {}  {}".format(dbx_dev, dbx_type, dbx_value))
        # creation du message xPL
        msg = XplMessage()
        msg.set_type("xpl-stat")
        msg.set_schema("sensor.basic")
        #msg.add_data({"timestamp" : teleinfo["timestamp"]})
        msg.add_data({"device" : dbx_dev})
        msg.add_data({"type" : dbx_type })
        msg.add_data({"current" : dbx_value})

        try:
            self.myxpl.send(msg)
        except XplMessageError: 
            self.log.debug(u"Bad xpl message to send. Xpl message is : {0}".format(str(msg)))
            pass

if __name__ == "__main__":
    DiaboxManager()


