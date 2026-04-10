# encoding:utf-8

from enum import Enum

from cowagent.common.log import logger
from cowagent.config import conf


class ReplyType(Enum):
    TEXT = 1  # 文本
    VOICE = 2  # 音频文件
    IMAGE = 3  # 图片文件
    IMAGE_URL = 4  # 图片URL
    VIDEO_URL = 5  # 视频URL
    FILE = 6  # 文件
    CARD = 7  # 微信名片，仅支持ntchat
    INVITE_ROOM = 8  # 邀请好友进群
    INFO = 9
    ERROR = 10
    TEXT_ = 11  # 强制文本
    VIDEO = 12
    MINIAPP = 13  # 小程序

    def __str__(self):
        return self.name


class Reply:
    def __init__(self, type: ReplyType = None, content=None):
        self.type = type
        self.content = content

    def __str__(self):
        return "Reply(type={}, content={})".format(self.type, self.content)


def sanitize_reply(reply: Reply) -> Reply:
    """
    Sanitize reply content to prevent sensitive information (e.g. llm_api_key)
    from being leaked to external messaging channels.

    If the reply content contains the llm_api_key, replace it with a warning message.
    """
    api_key = conf().get("llm_api_key")
    if not api_key:
        return reply

    text_content = None
    if reply.type in (ReplyType.TEXT, ReplyType.ERROR, ReplyType.INFO, ReplyType.TEXT_):
        text_content = reply.content if isinstance(reply.content, str) else str(reply.content)
    elif reply.type == ReplyType.VOICE:
        # voice file path could also contain the key, check string representation
        text_content = str(reply.content) if reply.content else ""

    if text_content and api_key in text_content:
        logger.error(
            "[Security] Reply content contains llm_api_key, blocked from sending. "
            "Reply type: %s",
            reply.type,
        )
        return Reply(type=ReplyType.ERROR, content="消息包含敏感信息，已拦截发送")

    return reply
