#isai-flask.wsgi
import sys
sys.path.insert(0, '/var/www/html/isai-flask')

from app import app as application