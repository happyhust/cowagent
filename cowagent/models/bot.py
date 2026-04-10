"""
Auto-replay chat robot abstract class
"""

from cowagent.bridge.context import Context
from cowagent.bridge.reply import Reply


class Bot(object):
    def reply(self, query, context: Context = None) -> Reply:
        """
        bot auto-reply content
        :param req: received message
        :return: reply content
        """
        raise NotImplementedError
