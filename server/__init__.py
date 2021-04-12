import os
from importlib import import_module

from flask import Flask

app = Flask(__name__)

# init app
app.config.setdefault('DATABASE', os.environ.get('AVDC_DATABASE'))
app.config.setdefault('TOKEN', os.environ.get('AVDC_TOKEN'))

# init module
import_module('.views', package=__name__)
