"""
channel factory
"""

from cowagent.common import const
from .channel import Channel


def create_channel(channel_type) -> Channel:
    """
    create a channel instance
    :param channel_type: channel type code
    :return: channel instance
    """
    ch = Channel()
    if channel_type == "terminal":
        from cowagent.channel.terminal.terminal_channel import TerminalChannel

        ch = TerminalChannel()
    elif channel_type == "web":
        from cowagent.channel.web.web_channel import WebChannel

        ch = WebChannel()
    elif channel_type == "wechatmp":
        from cowagent.channel.wechatmp.wechatmp_channel import WechatMPChannel

        ch = WechatMPChannel(passive_reply=True)
    elif channel_type == "wechatmp_service":
        from cowagent.channel.wechatmp.wechatmp_channel import WechatMPChannel

        ch = WechatMPChannel(passive_reply=False)
    elif channel_type == "wechatcom_app":
        from cowagent.channel.wechatcom.wechatcomapp_channel import WechatComAppChannel

        ch = WechatComAppChannel()
    elif channel_type == const.FEISHU:
        from cowagent.channel.feishu.feishu_channel import FeiShuChanel

        ch = FeiShuChanel()
    elif channel_type == const.DINGTALK:
        from cowagent.channel.dingtalk.dingtalk_channel import DingTalkChanel

        ch = DingTalkChanel()
    elif channel_type == const.WECOM_BOT:
        from cowagent.channel.wecom_bot.wecom_bot_channel import WecomBotChannel

        ch = WecomBotChannel()
    elif channel_type == const.QQ:
        from cowagent.channel.qq.qq_channel import QQChannel

        ch = QQChannel()
    elif channel_type in (const.WEIXIN, "wx"):
        from cowagent.channel.weixin.weixin_channel import WeixinChannel

        ch = WeixinChannel()
        channel_type = const.WEIXIN
    else:
        raise RuntimeError
    ch.channel_type = channel_type
    return ch
