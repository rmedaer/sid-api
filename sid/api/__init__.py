# -*- coding: utf-8 -*-

"""Software and infrastructure deployment API

This repository contains an HTTP API for SID project. Its purpose is to manage
configuration repositories. These repositories could contain Ansible or
Stackstorm configurations based on schemas.
"""

__version__ = '0.1.0'
__projects_prefix__ = 'projects/'
__templates_prefix__ = 'templates/'

__public_key__ = open('/tmp/test.pub.pem', 'r').read()
