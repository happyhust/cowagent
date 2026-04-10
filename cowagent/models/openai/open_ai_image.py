import time

from openai import OpenAI
from cowagent.models.openai.openai_compat import RateLimitError

from cowagent.common.log import logger
from cowagent.common.token_bucket import TokenBucket
from cowagent.config import conf


# OPENAI提供的画图接口
class OpenAIImage(object):
    def __init__(self):
        if conf().get("rate_limit_dalle"):
            self.tb4dalle = TokenBucket(conf().get("rate_limit_dalle", 50))

    def _get_client(self, api_key=None, api_base=None):
        """Create an OpenAI client with the given configuration."""
        kwargs = {}
        if api_key:
            kwargs["api_key"] = api_key
        else:
            kwargs["api_key"] = conf().get("llm_api_key")
        if api_base:
            kwargs["base_url"] = api_base
        elif conf().get("llm_api_base"):
            kwargs["base_url"] = conf().get("llm_api_base")
        proxy = conf().get("proxy")
        if proxy:
            import httpx
            kwargs["http_client"] = httpx.Client(proxy=proxy)
        return OpenAI(**kwargs)

    def create_img(self, query, retry_count=0, api_key=None, api_base=None):
        try:
            if conf().get("rate_limit_dalle") and not self.tb4dalle.get_token():
                return False, "请求太快了，请休息一下再问我吧"
            logger.info("[OPEN_AI] image_query={}".format(query))
            client = self._get_client(api_key, api_base)
            response = client.images.generate(
                prompt=query,  # 图片描述
                n=1,  # 每次生成图片的数量
                model=conf().get("text_to_image") or "dall-e-2",
                # size=conf().get("image_create_size", "256x256"),  # 图片大小,可选有 256x256, 512x512, 1024x1024
            )
            image_url = response.data[0].url
            logger.info("[OPEN_AI] image_url={}".format(image_url))
            return True, image_url
        except RateLimitError as e:
            logger.warn(e)
            if retry_count < 1:
                time.sleep(5)
                logger.warn(
                    "[OPEN_AI] ImgCreate RateLimit exceed, 第{}次重试".format(
                        retry_count + 1
                    )
                )
                return self.create_img(query, retry_count + 1)
            else:
                return False, "画图出现问题，请休息一下再问我吧"
        except Exception as e:
            logger.exception(e)
            return False, "画图出现问题，请休息一下再问我吧"
