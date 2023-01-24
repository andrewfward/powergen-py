# A.W. and E.S.
# 24/1/23
# This file contains the application factory

import os

from flask import Flask

import random

import customer_clustering as cc

import matplotlib.pyplot as plt

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # instance_relative_config tells Flask that filenames are relative to the instance folder
    app.config.from_mapping(
        SECRET_KEY='dev',  # this should be changed to a random value when the GUI is being deployed
        DATABASE=os.path.join(app.instance_path, 'powergen_flask.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/powergen')
    def hello():
        return 'Welcome to PowerGen GUI'

    #registering the input blueprint from the app factory
    from . import input
    app.register_blueprint(input.bp)

    return app
