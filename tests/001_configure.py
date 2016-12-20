#!/usr/bin/python

from domogik.tests.common.helpers import configure, delete_configuration
from domogik.common.utils import get_sanitized_hostname


delete_configuration("plugin", "diabox", get_sanitized_hostname())
configure("plugin", "diabox", get_sanitized_hostname(), "configured", True)

