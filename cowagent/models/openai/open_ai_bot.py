# encoding:utf-8

import time

from openai import OpenAI
from cowagent.models.openai.openai_compat import (
    RateLimitError,
    Timeout,
    APIConnectionError,
)

from cowagent.models.bot import Bot
from cowagent.models.openai_compatible_bot import OpenAICompatibleBot
from cowagent.models.openai.open_ai_image import OpenAIImage
from cowagent.models.openai.open_ai_session import OpenAISession
from cowagent.models.session_manager import SessionManager
from cowagent.bridge.context import ContextType
from cowagent.bridge.reply import Reply, ReplyType
from cowagent.common.log import logger
from cowagent.config import conf

user_session = dict()


# OpenAI对话模型API (可用)
class OpenAIBot(Bot, OpenAIImage, OpenAICompatibleBot):
    def __init__(self):
        super().__init__()
        self.api_key = conf().get("llm_api_key")
        self.api_base = conf().get("llm_api_base")
        self.proxy = conf().get("proxy")
        self.client = self._build_client()

        self.sessions = SessionManager(
            OpenAISession, model=conf().get("llm_model") or "text-davinci-003"
        )
        self.args = {
            "model": conf().get("llm_model") or "text-davinci-003",
            "temperature": conf().get("temperature", 0.9),
            "max_tokens": 1200,
            "top_p": 1,
            "frequency_penalty": conf().get("frequency_penalty", 0.0),
            "presence_penalty": conf().get("presence_penalty", 0.0),
        }

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
            "model": conf().get("llm_model", "text-davinci-003"),
            "default_temperature": conf().get("temperature", 0.9),
            "default_top_p": conf().get("top_p", 1.0),
            "default_frequency_penalty": conf().get("frequency_penalty", 0.0),
            "default_presence_penalty": conf().get("presence_penalty", 0.0),
        }

    def reply(self, query, context=None):
        if context and context.type:
            if context.type == ContextType.TEXT:
                logger.info("[OPEN_AI] query={}".format(query))
                session_id = context["session_id"]
                reply = None
                if query == "#清除记忆":
                    self.sessions.clear_session(session_id)
                    reply = Reply(ReplyType.INFO, "记忆已清除")
                elif query == "#清除所有":
                    self.sessions.clear_all_session()
                    reply = Reply(ReplyType.INFO, "所有人记忆已清除")
                else:
                    session = self.sessions.session_query(query, session_id)
                    result = self.reply_text(session)
                    total_tokens, completion_tokens, reply_content = (
                        result["total_tokens"],
                        result["completion_tokens"],
                        result["content"],
                    )
                    logger.debug(
                        "[OPEN_AI] new_query={}, session_id={}, reply_cont={}, completion_tokens={}".format(
                            str(session), session_id, reply_content, completion_tokens
                        )
                    )

                    if total_tokens == 0:
                        reply = Reply(ReplyType.ERROR, reply_content)
                    else:
                        self.sessions.session_reply(
                            reply_content, session_id, total_tokens
                        )
                        reply = Reply(ReplyType.TEXT, reply_content)
                return reply
            elif context.type == ContextType.IMAGE_CREATE:
                ok, retstring = self.create_img(query, 0)
                reply = None
                if ok:
                    reply = Reply(ReplyType.IMAGE_URL, retstring)
                else:
                    reply = Reply(ReplyType.ERROR, retstring)
                return reply

    def reply_text(self, session: OpenAISession, retry_count=0):
        try:
            response = self.client.completions.create(prompt=str(session), **self.args)
            response_dict = self._model_to_dict(response)
            res_content = response_dict["choices"][0]["text"].strip().replace("<think>", "").replace("</think>", "")
            total_tokens = response_dict["usage"]["total_tokens"]
            completion_tokens = response_dict["usage"]["completion_tokens"]
            logger.info("[OPEN_AI] reply={}".format(res_content))
            return {
                "total_tokens": total_tokens,
                "completion_tokens": completion_tokens,
                "content": res_content,
            }
        except Exception as e:
            need_retry = retry_count < 2
            result = {"completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            logger.error(
                f"[OPEN_AI] reply_text error | model={self.args.get('model')} | "
                f"session_id={session.session_id} | retry={retry_count} | "
                f"prompt_len={len(str(session))} | error_type={type(e).__name__} | "
                f"error={e}",
                exc_info=isinstance(e, (RateLimitError, Timeout, APIConnectionError)),
            )
            if isinstance(e, RateLimitError):
                logger.warn("[OPEN_AI] RateLimitError: {}".format(e))
                result["content"] = "提问太快啦，请休息一下再问我吧"
                if need_retry:
                    time.sleep(20)
            elif isinstance(e, Timeout):
                logger.warn("[OPEN_AI] Timeout: {}".format(e))
                result["content"] = "我没有收到你的消息"
                if need_retry:
                    time.sleep(5)
            elif isinstance(e, APIConnectionError):
                logger.warn("[OPEN_AI] APIConnectionError: {}".format(e))
                need_retry = False
                result["content"] = "我连接不到你的网络"
            else:
                logger.warn("[OPEN_AI] Exception: {}".format(e))
                need_retry = False
                self.sessions.clear_session(session.session_id)

            if need_retry:
                logger.warn("[OPEN_AI] 第{}次重试".format(retry_count + 1))
                return self.reply_text(session, retry_count + 1)
            else:
                return result

    def call_with_tools(self, messages, tools=None, stream=False, **kwargs):
        try:
            logger.info("[OPEN_AI] Using ChatCompletion API for tool support")

            request_params = {
                "model": kwargs.get("model", conf().get("llm_model") or "gpt-4.1"),
                "messages": messages,
                "temperature": kwargs.get(
                    "temperature", conf().get("temperature", 0.9)
                ),
                "top_p": kwargs.get("top_p", 1),
                "frequency_penalty": kwargs.get(
                    "frequency_penalty", conf().get("frequency_penalty", 0.0)
                ),
                "presence_penalty": kwargs.get(
                    "presence_penalty", conf().get("presence_penalty", 0.0)
                ),
                "stream": stream,
            }

            if kwargs.get("max_tokens"):
                request_params["max_tokens"] = kwargs["max_tokens"]

            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = kwargs.get("tool_choice", "auto")

            if stream:
                return self._handle_stream_response(request_params)
            else:
                return self._handle_sync_response(request_params)

        except Exception as e:
            logger.error(f"[OPEN_AI] call_with_tools error: {e}")
            error_msg = str(e)
            if stream:

                def error_generator():
                    yield {"error": True, "message": error_msg, "status_code": 500}

                return error_generator()
            else:
                return {"error": True, "message": error_msg, "status_code": 500}

    def _handle_sync_response(self, request_params):
        try:
            response = self.client.chat.completions.create(**request_params)
            response_dict = self._model_to_dict(response)
            logger.info(
                f"[OPEN_AI] call_with_tools reply, model={response_dict.get('model')}, "
                f"total_tokens={response_dict.get('usage', {}).get('total_tokens', 0)}"
            )
            return response_dict

        except Exception as e:
            logger.error(f"[OPEN_AI] sync response error: {e}")
            raise

    def _handle_stream_response(self, request_params):
        try:
            stream = self.client.chat.completions.create(**request_params)

            for chunk in stream:
                yield self._model_to_dict(chunk)

        except Exception as e:
            logger.error(f"[OPEN_AI] stream response error: {e}")
            yield {"error": True, "message": str(e), "status_code": 500}
