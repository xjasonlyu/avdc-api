from importlib import import_module

from flask import Flask

app = Flask(__name__)

# init
import_module('.views', package=__name__)
