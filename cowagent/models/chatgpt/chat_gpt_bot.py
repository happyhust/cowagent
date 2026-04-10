# encoding:utf-8

import time

from openai import OpenAI, AzureOpenAI
from cowagent.models.openai.openai_compat import (
    RateLimitError,
    Timeout,
    APIError,
    APIConnectionError,
)
import requests
from cowagent.common import const
from cowagent.models.bot import Bot
from cowagent.models.openai_compatible_bot import OpenAICompatibleBot
from cowagent.models.chatgpt.chat_gpt_session import ChatGPTSession
from cowagent.models.openai.open_ai_image import OpenAIImage
from cowagent.models.session_manager import SessionManager
from cowagent.bridge.context import ContextType
from cowagent.bridge.reply import Reply, ReplyType
from cowagent.common.log import logger
from cowagent.common.token_bucket import TokenBucket
from cowagent.config import conf, load_config
from cowagent.models.baidu.baidu_wenxin_session import BaiduWenxinSession


# OpenAI对话模型API (可用)
class ChatGPTBot(Bot, OpenAIImage, OpenAICompatibleBot):
    def __init__(self):
        super().__init__()
        self.api_key = conf().get("llm_api_key")
        self.api_base = conf().get("llm_api_base")
        self.proxy = conf().get("proxy")
        self.client = self._build_client()

        if conf().get("rate_limit_chatgpt"):
            self.tb4chatgpt = TokenBucket(conf().get("rate_limit_chatgpt", 20))
        conf_model = conf().get("llm_model") or "gpt-3.5-turbo"
        self.sessions = SessionManager(
            ChatGPTSession, model=conf().get("llm_model") or "gpt-3.5-turbo"
        )
        # o1相关模型不支持system prompt，暂时用文心模型的session

        self.args = {
            "model": conf_model,
            "temperature": conf().get("temperature", 0.9),
            "top_p": conf().get("top_p", 1),
            "frequency_penalty": conf().get("frequency_penalty", 0.0),
            "presence_penalty": conf().get("presence_penalty", 0.0),
        }
        # 部分模型暂不支持一些参数，特殊处理
        if conf_model in [
            const.O1,
            const.O1_MINI,
            const.GPT_5,
            const.GPT_5_MINI,
            const.GPT_5_NANO,
        ]:
            remove_keys = [
                "temperature",
                "top_p",
                "frequency_penalty",
                "presence_penalty",
            ]
            for key in remove_keys:
                self.args.pop(key, None)
            if conf_model in [
                const.O1,
                const.O1_MINI,
            ]:
                self.sessions = SessionManager(
                    BaiduWenxinSession, model=conf().get("llm_model") or const.O1_MINI
                )

    def _build_client(self, api_key=None, api_base=None, proxy=None):
        kwargs = {}
        if api_key:
            kwargs["api_key"] = api_key
        elif self.api_key:
            kwargs["api_key"] = self.api_key
        if api_base:
            kwargs["base_url"] = api_base
        elif self.api_base:
            kwargs["base_url"] = self.api_base
        p = proxy or self.proxy
        if p:
            import httpx
            kwargs["http_client"] = httpx.Client(proxy=p)
        return OpenAI(**kwargs)

    def _model_to_dict(self, obj):
        if isinstance(obj, dict):
            return obj
        return obj.model_dump() if hasattr(obj, "model_dump") else obj

    def get_api_config(self):
        return {
            "api_key": conf().get("llm_api_key"),
            "api_base": conf().get("llm_api_base"),
            "model": conf().get("llm_model", "gpt-3.5-turbo"),
            "default_temperature": conf().get("temperature", 0.9),
            "default_top_p": conf().get("top_p", 1.0),
            "default_frequency_penalty": conf().get("frequency_penalty", 0.0),
            "default_presence_penalty": conf().get("presence_penalty", 0.0),
        }

    def reply(self, query, context=None):
        if context.type == ContextType.TEXT:
            logger.info("[CHATGPT] query={}".format(query))

            session_id = context["session_id"]
            reply = None
            clear_memory_commands = conf().get("clear_memory_commands", ["#清除记忆"])
            if query in clear_memory_commands:
                self.sessions.clear_session(session_id)
                reply = Reply(ReplyType.INFO, "记忆已清除")
            elif query == "#清除所有":
                self.sessions.clear_all_session()
                reply = Reply(ReplyType.INFO, "所有人记忆已清除")
            elif query == "#更新配置":
                load_config()
                reply = Reply(ReplyType.INFO, "配置已更新")
            if reply:
                return reply
            session = self.sessions.session_query(query, session_id)
            logger.debug("[CHATGPT] session query={}".format(session.messages))

            api_key = context.get("openai_api_key")
            model = context.get("gpt_model")
            new_args = None
            if model:
                new_args = self.args.copy()
                new_args["model"] = model

            reply_content = self.reply_text(session, api_key, args=new_args)
            logger.debug(
                "[CHATGPT] new_query={}, session_id={}, reply_cont={}, completion_tokens={}".format(
                    session.messages,
                    session_id,
                    reply_content["content"],
                    reply_content["completion_tokens"],
                )
            )
            if (
                reply_content["completion_tokens"] == 0
                and len(reply_content["content"]) > 0
            ):
                reply = Reply(ReplyType.ERROR, reply_content["content"])
            elif reply_content["completion_tokens"] > 0:
                self.sessions.session_reply(
                    reply_content["content"], session_id, reply_content["total_tokens"]
                )
                reply = Reply(ReplyType.TEXT, reply_content["content"])
            else:
                reply = Reply(ReplyType.ERROR, reply_content["content"])
                logger.debug("[CHATGPT] reply {} used 0 tokens.".format(reply_content))
            return reply

        elif context.type == ContextType.IMAGE_CREATE:
            ok, retstring = self.create_img(query, 0)
            reply = None
            if ok:
                reply = Reply(ReplyType.IMAGE_URL, retstring)
            else:
                reply = Reply(ReplyType.ERROR, retstring)
            return reply
        elif context.type == ContextType.IMAGE:
            logger.info("[CHATGPT] Image message received")
            reply = self.reply_image(context)
            return reply
        else:
            reply = Reply(
                ReplyType.ERROR, "Bot不支持处理{}类型的消息".format(context.type)
            )
            return reply

    def reply_image(self, context):
        import base64
        import os

        try:
            image_path = context.content
            logger.info(f"[CHATGPT] Processing image: {image_path}")

            if not os.path.exists(image_path):
                logger.error(f"[CHATGPT] Image file not found: {image_path}")
                return Reply(ReplyType.ERROR, "图片文件不存在")

            with open(image_path, "rb") as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode("utf-8")

            extension = os.path.splitext(image_path)[1].lower()
            mime_type_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }
            mime_type = mime_type_map.get(extension, "image/jpeg")

            model = context.get("gpt_model") or conf().get("llm_model", "gpt-4o")
            api_key = context.get("openai_api_key") or conf().get("llm_api_key")
            api_base = conf().get("llm_api_base")

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请描述这张图片的内容"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            },
                        },
                    ],
                }
            ]

            logger.info(f"[CHATGPT] Calling vision API with model: {model}")

            client = self._build_client(api_key=api_key, api_base=api_base)
            response = client.chat.completions.create(
                model=model, messages=messages, max_tokens=1000
            )

            content = response.choices[0].message.content
            logger.info(f"[CHATGPT] Vision API response: {content[:100]}...")

            try:
                os.remove(image_path)
                logger.debug(f"[CHATGPT] Removed temp image file: {image_path}")
            except Exception:
                pass

            return Reply(ReplyType.TEXT, content)

        except Exception as e:
            logger.error(f"[CHATGPT] Image processing error: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return Reply(ReplyType.ERROR, f"图片识别失败: {str(e)}")

    def reply_text(
        self, session: ChatGPTSession, api_key=None, args=None, retry_count=0
    ) -> dict:
        try:
            if conf().get("rate_limit_chatgpt") and not self.tb4chatgpt.get_token():
                raise RateLimitError("RateLimitError: rate limit exceeded")
            if args is None:
                args = self.args

            if api_key:
                client = self._build_client(api_key=api_key)
            else:
                client = self.client

            response = client.chat.completions.create(
                messages=session.messages, **args
            )
            response_dict = self._model_to_dict(response)
            logger.info(
                "[ChatGPT] reply={}, total_tokens={}".format(
                    response_dict["choices"][0]["message"]["content"],
                    response_dict["usage"]["total_tokens"],
                )
            )
            return {
                "total_tokens": response_dict["usage"]["total_tokens"],
                "completion_tokens": response_dict["usage"]["completion_tokens"],
                "content": response_dict["choices"][0]["message"]["content"],
            }
        except Exception as e:
            need_retry = retry_count < 2
            result = {"completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            logger.error(
                f"[CHATGPT] reply_text error | model={self.args.get('model')} | "
                f"session_id={session.session_id} | retry={retry_count} | "
                f"message_count={len(session.messages)} | error_type={type(e).__name__} | "
                f"error={e}",
                exc_info=isinstance(e, (RateLimitError, Timeout, APIError, APIConnectionError)),
            )
            if isinstance(e, RateLimitError):
                logger.warn("[CHATGPT] RateLimitError: {}".format(e))
                result["content"] = "提问太快啦，请休息一下再问我吧"
                if need_retry:
                    time.sleep(20)
            elif isinstance(e, Timeout):
                logger.warn("[CHATGPT] Timeout: {}".format(e))
                result["content"] = "我没有收到你的消息"
                if need_retry:
                    time.sleep(5)
            elif isinstance(e, APIError):
                logger.warn("[CHATGPT] Bad Gateway: {}".format(e))
                result["content"] = "请再问我一次"
                if need_retry:
                    time.sleep(10)
            elif isinstance(e, APIConnectionError):
                logger.warn("[CHATGPT] APIConnectionError: {}".format(e))
                result["content"] = "我连接不到你的网络"
                if need_retry:
                    time.sleep(5)
            else:
                logger.exception("[CHATGPT] Exception: {}".format(e))
                need_retry = False
                self.sessions.clear_session(session.session_id)

            if need_retry:
                logger.warn("[CHATGPT] 第{}次重试".format(retry_count + 1))
                return self.reply_text(session, api_key, args, retry_count + 1)
            else:
                return result


class AzureChatGPTBot(ChatGPTBot):
    def __init__(self):
        super().__init__()
        self.azure_api_version = conf().get("azure_api_version", "2023-06-01-preview")
        self.azure_deployment_id = conf().get("azure_deployment_id")
        self.client = self._build_azure_client()
        self.args["deployment_id"] = self.azure_deployment_id

    def _build_azure_client(self, api_key=None, api_base=None):
        kwargs = {}
        if api_key:
            kwargs["api_key"] = api_key
        elif self.api_key:
            kwargs["api_key"] = self.api_key
        if api_base:
            kwargs["azure_endpoint"] = api_base
        elif self.api_base:
            kwargs["azure_endpoint"] = self.api_base
        kwargs["api_version"] = self.azure_api_version
        return AzureOpenAI(**kwargs)
