"""
channel factory
"""

from cowagent.common import const


def create_bot(bot_type):
    """
    create a bot_type instance
    :param bot_type: bot type code
    :return: bot instance
    """
    if bot_type == const.BAIDU:
        # 替换Baidu Unit为Baidu文心千帆对话接口
        # from cowagent.models.baidu.baidu_unit_bot import BaiduUnitBot
        # return BaiduUnitBot()
        from cowagent.models.baidu.baidu_wenxin import BaiduWenxinBot

        return BaiduWenxinBot()

    elif bot_type == const.DEEPSEEK:
        from cowagent.models.deepseek.deepseek_bot import DeepSeekBot

        return DeepSeekBot()

    elif bot_type in (const.OPENAI, const.CHATGPT):  # OpenAI-compatible API
        from cowagent.models.chatgpt.chat_gpt_bot import ChatGPTBot

        return ChatGPTBot()

    elif bot_type == const.OPEN_AI:
        # OpenAI 官方对话模型API
        from cowagent.models.openai.open_ai_bot import OpenAIBot

        return OpenAIBot()

    elif bot_type == const.CHATGPTONAZURE:
        # Azure chatgpt service https://azure.microsoft.com/en-in/products/cognitive-services/openai-service/
        from cowagent.models.chatgpt.chat_gpt_bot import AzureChatGPTBot

        return AzureChatGPTBot()

    elif bot_type == const.XUNFEI:
        from cowagent.models.xunfei.xunfei_spark_bot import XunFeiBot

        return XunFeiBot()

    elif bot_type == const.LINKAI:
        from cowagent.models.linkai.link_ai_bot import LinkAIBot

        return LinkAIBot()

    elif bot_type == const.CLAUDEAPI:
        from cowagent.models.claudeapi.claude_api_bot import ClaudeAPIBot

        return ClaudeAPIBot()
    elif bot_type in (const.QWEN, const.QWEN_DASHSCOPE):
        from cowagent.models.dashscope.dashscope_bot import DashscopeBot

        return DashscopeBot()
    elif bot_type == const.GEMINI:
        from cowagent.models.gemini.google_gemini_bot import GoogleGeminiBot

        return GoogleGeminiBot()

    elif (
        bot_type == const.ZHIPU_AI or bot_type == "glm-4"
    ):  # "glm-4" kept for backward compatibility
        from cowagent.models.zhipuai.zhipuai_bot import ZHIPUAIBot

        return ZHIPUAIBot()

    elif bot_type == const.MOONSHOT:
        from cowagent.models.moonshot.moonshot_bot import MoonshotBot

        return MoonshotBot()

    elif bot_type == const.MiniMax:
        from cowagent.models.minimax.minimax_bot import MinimaxBot

        return MinimaxBot()

    elif bot_type == const.MODELSCOPE:
        from cowagent.models.modelscope.modelscope_bot import ModelScopeBot

        return ModelScopeBot()

    elif bot_type == const.DOUBAO:
        from cowagent.models.doubao.doubao_bot import DoubaoBot

        return DoubaoBot()

    raise RuntimeError
