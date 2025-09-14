from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask_app import app  # Your Flask app is defined here

from pyramid.config import Configurator
from pyramid.response import Response
import os

def hello_world(request):
    name = os.environ.get('NAME', 'world')
    return Response(f"Hello, {name}!\n")

# Create Pyramid app
with Configurator() as config:
    config.add_route('hello', '/')
    config.add_view(hello_world, route_name='hello')
    pyramid_app = config.make_wsgi_app()

# Combine Pyramid and Flask apps
application = DispatcherMiddleware(app, {
    '/hello': pyramid_app
})