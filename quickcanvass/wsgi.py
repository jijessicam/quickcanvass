"""
WSGI config for quickcanvass project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append(" C:\Users\jessica\\anaconda2\lib\site-packages")

path = 'C:/Users/Jessica/quickcanvass'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quickcanvass.settings")

application = get_wsgi_application()
