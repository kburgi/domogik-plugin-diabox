#!/usr/bin/python
# -*- coding: utf-8 -*-


from domogik.tests.common.testdevice import TestDevice
from domogik.common.utils import get_sanitized_hostname


if __name__ == "__main__":

    client_id = "plugin-diabox.{0}".format(get_sanitized_hostname())
    td = TestDevice()
    params = td.get_params(client_id, "diabox.minou")

    # fill in the params
    params["device_type"] = "diabox.minou"
    params["name"] = "TestDiaboxMinou"
    params["reference"] = "RefTestDiaboxMinou"
    params["description"] = "DescTestDiaboxMinoux"
    for idx, val in enumerate(params['global']):
        params['global'][idx]['value'] = 60
    for idx, val in enumerate(params['xpl']):
        params['xpl'][idx]['value'] = 'ref_dbx_Minou'

    # go and create
    td.create_device(params)


