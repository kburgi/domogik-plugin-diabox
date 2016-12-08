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
        #if not self.check_configured():
        #    return
        
        self.devices = self.get_device_list(quit_if_no_device = False)

        self.log.debug("---------------------------- HERE ----------------------------------")

        threads = {}
        for dev in self.devices:
            try:
                self.log.debug("--------- INIT DEVICE \"{}\" ------------------".format(dev['name']))
                #print dev
                #print "--------------------"
                #print "dev['{}']={}".format("description", dev['description'])


                # need to now which station to catch right diabox variable in diaboxconfig
                self.log.info("Config : diabox station type \"{}\"".format(dev['device_type_id']))
                self.log.info("Config : diabox description \"{}\"".format(dev['description']))
                #print "dev['{}']={}".format("device_type_id", dev['device_type_id'])


#                self.log.debug("---------- test device configured ---------------")
#                self.log.error("Is device {} configured ?".format(dev['name']))
#                if not self.check_configured():
#                    self.log.error("Device {} is not configured !".format(dev['name']))
#                    return

                dbx_domo_id=dev['id']

                refresh_interval = self.get_parameter(dev,"interval")
                if refresh_interval == None:
                    self.log.error("Interval \"{}\" is invalid for device \"{}\"".format(refresh_interval, dev['name']))                
                    return
                self.log.debug("Dev={}  Config refresh interval = {}".format(dev['name'], refresh_interval))

                self.log.debug("------- Calling manager => DiaboxLib  -------------")
                # note : device_type_id = diabox.minou / diabox.wrach / etc => required for diaboxconfig module
                self._diabox_manager = DiaboxLib(self.log, self.send_xpl, self.get_stop(), dev['device_type_id'], dev["id"], refresh_interval)
                if self._diabox_manager.isConfigured == False:
                    self.log.error("Something went wrent wrong during init of the DiaboxManager for device_type_id=\"{}\"  => I skip it !".format(dev['device_type_id'])) 
                    continue;

                self.add_stop_cb(self._diabox_manager.stop)

                thr_name = "diabox_{}".format(dev['name'])
                self.log.info("[Starting thread {}] Start fetching diabox data".format(thr_name))
                threads[thr_name] = threading.Thread(None,
                                                    self._diabox_manager.get_diabox_data,
                                                    thr_name,
                                                    (),
                                                    {})
                threads[thr_name].start()
                self.register_thread(threads[thr_name])
            except:
                self.log.error("[bin/diabox.py] Exception spotted while creating threads !!")
                self.log.error("{0}".format(traceback.format_exc()))
                self.log.error("[bin/diabox.py][device_type_id={}] Leaving this diabox thread for this device !".format(dev['device-type_id']))
                return  

        self.log.info("Plugin \"diabox\" ready :)")
        self.ready()


    def send_xpl(self, domo_dev_id, dbx_station_name, sensor_name, sensor_type, sensor_value):
        """ send xPL on the network """
        self.log.debug("Will send an xPL msg with a line of diabox data... see line below")
        self.log.debug("[domo_dev_id=\"{}\"][dbx=\"{}\"][type=\"{}\"][val=\"{}\"]"
                        .format(domo_dev_id, dbx_station_name, sensor_type, sensor_value))
        # creation du message xPL
        msg = XplMessage()
        msg.set_type("xpl-stat")
        msg.set_schema("sensor.basic")
        msg.add_data({"device" : domo_dev_id})
        msg.add_data({"type" : sensor_type })
        msg.add_data({"current" : sensor_value})

        try:
            self.log.debug("Now trying to send the xpl msg...")
            self.myxpl.send(msg)
        except XplMessageError: 
            self.log.debug(u"Bad xpl message to send. Xpl message is : {0}".format(str(msg)))
            pass

if __name__ == "__main__":
    DiaboxManager()


