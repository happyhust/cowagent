from .event import *
from .plugin import *
from .plugin_manager import PluginManager

instance = PluginManager()

# Alias for plugin manager instance - plugins use `plugins.register` as decorator
plugins = instance

register = instance.register
# load_plugins                = instance.load_plugins
# emit_event                  = instance.emit_event
