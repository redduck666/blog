"""Pylons environment configuration"""
import os

from jinja2 import ChoiceLoader, Environment, FileSystemLoader
from pylons.configuration import PylonsConfig

import blog.lib.app_globals as app_globals
import blog.lib.helpers
from blog.config.routing import make_map

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    config = PylonsConfig()
    
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='blog', paths=paths)

    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = blog.lib.helpers
    
    # Setup cache object as early as possible
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)
    

    # Create the Jinja2 Environment
    config['pylons.app_globals'].jinja2_env = Environment(loader=ChoiceLoader(
            [FileSystemLoader(path) for path in paths['templates']]))
    # Jinja2's unable to request c's attributes without strict_c
    config['pylons.strict_tmpl_context'] = True

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    
    return config
