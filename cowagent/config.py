# encoding:utf-8

import copy
import json
import logging
import os
import pickle

from cowagent.common import const
from cowagent.common.log import logger

# Unified LLM provider → bot_type mapping
LLM_PROVIDER_TO_BOT_TYPE = {
    "openai": const.CHATGPT,
    "claude": const.CLAUDEAPI,
    "gemini": const.GEMINI,
    "qwen": const.QWEN_DASHSCOPE,
    "zhipu": const.ZHIPU_AI,
    "moonshot": const.MOONSHOT,
    "doubao": const.DOUBAO,
    "deepseek": const.DEEPSEEK,
    "minimax": const.MiniMax,
    "modelscope": const.MODELSCOPE,
    "linkai": const.LINKAI,
    "baidu": const.BAIDU,
    "xunfei": const.XUNFEI,
}

# 将所有可用的配置项写在字典里, 请使用小写字母
# 此处的配置值无实际意义，程序不会读取此处的配置，仅用于提示格式，请将配置加入到config.json中
available_setting = {
    # LLM unified config
    "llm_provider": "openai",  # LLM provider: openai, claude, gemini, qwen, zhipu, moonshot, doubao, deepseek, minimax, modelscope, linkai, baidu, xunfei
    "llm_model": "gpt-5.4",  # LLM model name
    "llm_api_key": "",  # LLM API key
    "llm_api_base": "",  # LLM API base URL (leave empty for provider default)
    # proxy
    "proxy": "",  # proxy for API requests
    # Bot type override (optional, auto-derived from llm_provider if not set)
    "bot_type": "",
    # Azure config (for use_azure_chatgpt bot_type)
    "use_azure_chatgpt": False,
    "azure_deployment_id": "",
    "azure_api_version": "",
    # Azure DALL-E image gen (separate key/endpoint)
    "azure_openai_dalle_api_base": "",
    "azure_openai_dalle_api_key": "",
    "azure_openai_dalle_deployment_id": "",
    # Bot触发配置
    "single_chat_prefix": ["bot", "@bot"],  # 私聊时文本需要包含该前缀才能触发机器人回复
    "single_chat_reply_prefix": "[bot] ",  # 私聊时自动回复的前缀，用于区分真人
    "single_chat_reply_suffix": "",  # 私聊时自动回复的后缀，\n 可以换行
    "group_chat_prefix": ["@bot"],  # 群聊时包含该前缀则会触发机器人回复
    "no_need_at": False,  # 群聊回复时是否不需要艾特
    "group_chat_reply_prefix": "",  # 群聊时自动回复的前缀
    "group_chat_reply_suffix": "",  # 群聊时自动回复的后缀，\n 可以换行
    "group_chat_keyword": [],  # 群聊时包含该关键词则会触发机器人回复
    "group_at_off": False,  # 是否关闭群聊时@bot的触发
    "group_name_white_list": [
        "ChatGPT测试群",
        "ChatGPT测试群2",
    ],  # 开启自动回复的群名称列表
    "group_name_keyword_white_list": [],  # 开启自动回复的群名称关键词列表
    "group_chat_in_one_session": ["ChatGPT测试群"],  # 支持会话上下文共享的群名称
    "group_shared_session": False,  # 群聊是否共享会话上下文（所有成员共享）。False时每个用户在群内有独立会话
    "nick_name_black_list": [],  # 用户昵称黑名单
    "group_welcome_msg": "",  # 配置新人进群固定欢迎语，不配置则使用随机风格欢迎
    "trigger_by_self": False,  # 是否允许机器人触发
    "text_to_image": "dall-e-2",  # 图片生成模型，可选 dall-e-2, dall-e-3
    # Azure OpenAI dall-e-3 配置
    "dalle3_image_style": "vivid",  # 图片生成dalle3的风格，可选有 vivid, natural
    "dalle3_image_quality": "hd",  # 图片生成dalle3的质量，可选有 standard, hd
    # Azure OpenAI DALL-E API 配置, 当use_azure_chatgpt为true时,用于将文字回复的资源和Dall-E的资源分开.
    "azure_openai_dalle_api_base": "",  # [可选] azure openai 用于回复图片的资源 endpoint，默认使用 open_ai_api_base
    "azure_openai_dalle_api_key": "",  # [可选] azure openai 用于回复图片的资源 key，默认使用 open_ai_api_key
    "azure_openai_dalle_deployment_id": "",  # [可选] azure openai 用于回复图片的资源 deployment id，默认使用 text_to_image
    "image_proxy": True,  # 是否需要图片代理，国内访问LinkAI时需要
    "image_create_prefix": ["画", "看", "找"],  # 开启图片回复的前缀
    "concurrency_in_session": 1,  # 同一会话最多有多少条消息在处理中，大于1可能乱序
    "image_create_size": "256x256",  # 图片大小,可选有 256x256, 512x512, 1024x1024 (dall-e-3默认为1024x1024)
    "group_chat_exit_group": False,
    # chatgpt会话参数
    "expires_in_seconds": 3600,  # 无操作会话的过期时间
    # 人格描述
    "character_desc": "你是ChatGPT, 一个由OpenAI训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。",
    "conversation_max_tokens": 1000,  # 支持上下文记忆的最多字符数
    # chatgpt限流配置
    "rate_limit_chatgpt": 20,  # chatgpt的调用频率限制
    "rate_limit_dalle": 50,  # openai dalle的调用频率限制
    # chatgpt api参数 参考https://platform.openai.com/docs/api-reference/chat/create
    "temperature": 0.9,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "request_timeout": 180,  # chatgpt请求超时时间，openai接口默认设置为600，对于难问题一般需要较长时间
    "timeout": 120,  # chatgpt重试超时时间，在这个时间内，将会自动重试
    # 语音设置
    "speech_recognition": True,  # 是否开启语音识别
    "group_speech_recognition": False,  # 是否开启群组语音识别
    "voice_reply_voice": False,  # 是否使用语音回复语音，需要设置对应语音合成引擎的api key
    "always_reply_voice": False,  # 是否一直使用语音回复
    "voice_to_text": "openai",  # 语音识别引擎，支持openai,baidu,google,azure,xunfei,ali
    "text_to_voice": "openai",  # 语音合成引擎，支持openai,baidu,google,azure,xunfei,ali,pytts(offline),elevenlabs,edge(online)
    "text_to_voice_model": "tts-1",
    "tts_voice_id": "alloy",
    # baidu 语音api配置， 使用百度语音识别和语音合成时需要
    "baidu_app_id": "",
    "baidu_api_key": "",
    "baidu_secret_key": "",
    # 1536普通话(支持简单的英文识别) 1737英语 1637粤语 1837四川话 1936普通话远场
    "baidu_dev_pid": 1536,
    # azure 语音api配置， 使用azure语音识别和语音合成时需要
    "azure_voice_api_key": "",
    "azure_voice_region": "japaneast",
    # elevenlabs 语音api配置
    "xi_api_key": "",  # 获取ap的方法可以参考https://docs.elevenlabs.io/api-reference/quick-start/authentication
    "xi_voice_id": "",  # ElevenLabs提供了9种英式、美式等英语发音id，分别是“Adam/Antoni/Arnold/Bella/Domi/Elli/Josh/Rachel/Sam”
    # 服务时间限制
    "chat_time_module": False,  # 是否开启服务时间限制
    "chat_start_time": "00:00",  # 服务开始时间
    "chat_stop_time": "24:00",  # 服务结束时间
    # 翻译api
    "translate": "baidu",  # 翻译api，支持baidu
    # baidu翻译api的配置
    "baidu_translate_app_id": "",  # 百度翻译api的appid
    "baidu_translate_app_key": "",  # 百度翻译api的秘钥
    # wechatmp的配置
    "wechatmp_token": "",  # 微信公众平台的Token
    "wechatmp_port": 8080,  # 微信公众平台的端口,需要端口转发到80或443
    "wechatmp_app_id": "",  # 微信公众平台的appID
    "wechatmp_app_secret": "",  # 微信公众平台的appsecret
    "wechatmp_aes_key": "",  # 微信公众平台的EncodingAESKey，加密模式需要
    # wechatcom的通用配置
    "wechatcom_corp_id": "",  # 企业微信公司的corpID
    # wechatcomapp的配置
    "wechatcomapp_token": "",  # 企业微信app的token
    "wechatcomapp_port": 9898,  # 企业微信app的服务端口,不需要端口转发
    "wechatcomapp_secret": "",  # 企业微信app的secret
    "wechatcomapp_agent_id": "",  # 企业微信app的agent_id
    "wechatcomapp_aes_key": "",  # 企业微信app的aes_key
    # 飞书配置
    "feishu_port": 80,  # 飞书bot监听端口
    "feishu_app_id": "",  # 飞书机器人应用APP Id
    "feishu_app_secret": "",  # 飞书机器人APP secret
    "feishu_token": "",  # 飞书 verification token
    "feishu_bot_name": "",  # 飞书机器人的名字
    "feishu_event_mode": "websocket",  # 飞书事件接收模式: webhook(HTTP服务器) 或 websocket(长连接)
    # 钉钉配置
    "dingtalk_client_id": "",  # 钉钉机器人Client ID
    "dingtalk_client_secret": "",  # 钉钉机器人Client Secret
    "dingtalk_card_enabled": False,
    # 企微智能机器人配置(长连接模式)
    "wecom_bot_id": "",  # 企微智能机器人BotID
    "wecom_bot_secret": "",  # 企微智能机器人长连接Secret
    # 微信配置
    "weixin_token": "",  # 微信登录后获取的bot_token，留空则启动时自动扫码登录
    "weixin_base_url": "https://ilinkai.weixin.qq.com",  # Weixin ilink API base URL
    "weixin_cdn_base_url": "https://novac2c.cdn.weixin.qq.com/c2c",  # CDN base URL
    "weixin_credentials_path": "~/.cowagent/weixin_credentials.json",  # credentials file path
    # chatgpt指令自定义触发词
    "clear_memory_commands": ["#清除记忆"],  # 重置会话指令，必须以#开头
    # channel配置
    "channel_type": "",  # 通道类型，支持多渠道同时运行。单个: "feishu"，多个: "feishu, dingtalk" 或 ["feishu", "dingtalk"]。可选值: web,feishu,dingtalk,wecom_bot,weixin,wechatmp,wechatmp_service,wechatcom_app
    "web_console": True,  # 是否自动启动Web控制台（默认启动）。设为False可禁用
    "subscribe_msg": "",  # 订阅消息, 支持: wechatmp, wechatmp_service, wechatcom_app
    "debug": False,  # 是否开启debug模式，开启后会打印更多日志
    "appdata_dir": "",  # 数据目录
    # 插件配置
    "plugin_trigger_prefix": "$",  # 规范插件提供聊天相关指令的前缀，建议不要和管理员指令前缀"#"冲突
    # 是否使用全局插件配置
    "use_global_plugin_config": False,
    "max_media_send_count": 3,  # 单次最大发送媒体资源的个数
    "media_send_interval": 1,  # 发送图片的事件间隔，单位秒
    # LinkAI平台配置
    "use_linkai": False,
    "linkai_app_code": "",
    "cloud_host": "client.link-ai.tech",
    "cloud_port": None,
    "cloud_deployment_id": "",
    "Minimax_group_id": "",
    "web_port": 9899,
    "agent": True,  # 是否开启Agent模式
    "agent_workspace": "~/.cowagent",  # agent工作空间路径，用于存储skills、memory等
    "agent_max_context_tokens": 50000,  # Agent模式下最大上下文tokens
    "agent_max_context_turns": 30,  # Agent模式下最大上下文记忆轮次
    "agent_max_steps": 15,  # Agent模式下单次运行最大决策步数
}


class Config(dict):
    def __init__(self, d=None):
        super().__init__()
        if d is None:
            d = {}
        for k, v in d.items():
            self[k] = v
        # user_datas: 用户数据，key为用户名，value为用户数据，也是dict
        self.user_datas = {}

    def __getitem__(self, key):
        # 跳过以下划线开头的注释字段
        if not key.startswith("_") and key not in available_setting:
            logger.warning(
                "[Config] key '{}' not in available_setting, may not take effect".format(
                    key
                )
            )
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        # 跳过以下划线开头的注释字段
        if not key.startswith("_") and key not in available_setting:
            logger.warning(
                "[Config] key '{}' not in available_setting, may not take effect".format(
                    key
                )
            )
        return super().__setitem__(key, value)

    def get(self, key, default=None):
        # 跳过以下划线开头的注释字段
        if key.startswith("_"):
            return super().get(key, default)

        # 如果key不在available_setting中，直接返回default
        if key not in available_setting:
            return super().get(key, default)

        try:
            return self[key]
        except KeyError:
            return default
        except Exception as e:
            raise e

    # Make sure to return a dictionary to ensure atomic
    def get_user_data(self, user) -> dict:
        if self.user_datas.get(user) is None:
            self.user_datas[user] = {}
        return self.user_datas[user]

    def load_user_datas(self):
        try:
            with open(os.path.join(get_appdata_dir(), "user_datas.pkl"), "rb") as f:
                self.user_datas = pickle.load(f)
                logger.debug("[Config] User datas loaded.")
        except FileNotFoundError:
            logger.debug("[Config] User datas file not found, ignore.")
        except Exception as e:
            logger.warning("[Config] User datas error: {}".format(e))
            self.user_datas = {}

    def save_user_datas(self):
        try:
            with open(os.path.join(get_appdata_dir(), "user_datas.pkl"), "wb") as f:
                pickle.dump(self.user_datas, f)
                logger.info("[Config] User datas saved.")
        except Exception as e:
            logger.info("[Config] User datas error: {}".format(e))


config = Config()


def drag_sensitive(config):
    try:
        if isinstance(config, str):
            conf_dict: dict = json.loads(config)
            conf_dict_copy = copy.deepcopy(conf_dict)
            for key in conf_dict_copy:
                if "key" in key or "secret" in key:
                    if isinstance(conf_dict_copy[key], str):
                        conf_dict_copy[key] = "***"
            return json.dumps(conf_dict_copy, indent=4)

        elif isinstance(config, dict):
            config_copy = copy.deepcopy(config)
            for key in config:
                if "key" in key or "secret" in key:
                    if isinstance(config_copy[key], str):
                        config_copy[key] = "***"
            return config_copy
    except Exception as e:
        logger.exception(e)
        return config
    return config


def load_config():
    global config

    # 打印 ASCII Logo
    logger.info("  ____                _                    _   ")
    logger.info(" / ___|_____      __ / \\   __ _  ___ _ __ | |_ ")
    logger.info("| |   / _ \\ \\ /\\ / // _ \\ / _` |/ _ \\ '_ \\| __|")
    logger.info("| |__| (_) \\ V  V // ___ \\ (_| |  __/ | | | |_ ")
    logger.info(" \\____\\___/ \\_/\\_//_/   \\_\\__, |\\___|_| |_|\\__|")
    logger.info("                          |___/                 ")
    logger.info("")
    config_path = "./config.json"
    if not os.path.exists(config_path):
        logger.info("配置文件不存在，将使用config-template.json模板")
        config_path = "./config-template.json"

    config_str = read_file(config_path)
    logger.debug("[INIT] config str: {}".format(drag_sensitive(config_str)))

    # 将json字符串反序列化为dict类型
    config = Config(json.loads(config_str))

    # override config with environment variables.
    # Some online deployment platforms (e.g. Railway) deploy project from github directly. So you shouldn't put your secrets like api key in a config file, instead use environment variables to override the default config.
    for name, value in os.environ.items():
        name = name.lower()
        # 跳过以下划线开头的注释字段
        if name.startswith("_"):
            continue
        if name in available_setting:
            logger.info(
                "[INIT] override config by environ args: {}={}".format(name, value)
            )
            try:
                config[name] = eval(value)
            except Exception:
                if value == "false":
                    config[name] = False
                elif value == "true":
                    config[name] = True
                else:
                    config[name] = value

    if config.get("debug", False):
        logger.setLevel(logging.DEBUG)
        logger.debug("[INIT] set log level to DEBUG")

    logger.info("[INIT] load config: {}".format(drag_sensitive(config)))

    # 打印系统初始化信息
    logger.info("[INIT] ========================================")
    logger.info("[INIT] System Initialization")
    logger.info("[INIT] ========================================")
    logger.info("[INIT] Channel: {}".format(config.get("channel_type", "unknown")))
    llm_api_base = config.get("llm_api_base", "")
    llm_api_base_str = " (base: {})".format(llm_api_base) if llm_api_base else ""
    logger.info("[INIT] Model: {} ({}){}".format(
        config.get("llm_model", "unknown"),
        config.get("llm_provider", "unknown"),
        llm_api_base_str
    ))

    # Agent模式信息
    if config.get("agent", False):
        workspace = config.get("agent_workspace", "~/.cowagent")
        logger.info("[INIT] Mode: Agent (workspace: {})".format(workspace))
    else:
        logger.info(
            '[INIT] Mode: Chat (在config.json中设置 "agent":true 可启用Agent模式)'
        )

    logger.info("[INIT] Debug: {}".format(config.get("debug", False)))
    logger.info("[INIT] ========================================")

    # Sync selected config values to environment variables so that
    # subprocesses (e.g. shell skill scripts) can access them directly.
    # Existing env vars are NOT overwritten (env takes precedence).
    # Sync unified LLM config to environment variables so that
    # subprocesses (e.g. shell skill scripts) can access them directly.
    # Existing env vars are NOT overwritten (env takes precedence).
    _CONFIG_TO_ENV = {
        "llm_api_key": "OPENAI_API_KEY",
        "llm_api_base": "OPENAI_API_BASE",
    }
    injected = 0
    for conf_key, env_key in _CONFIG_TO_ENV.items():
        if env_key not in os.environ:
            val = config.get(conf_key, "")
            if val:
                os.environ[env_key] = str(val)
                injected += 1
    if injected:
        logger.info(
            "[INIT] Synced {} config values to environment variables".format(injected)
        )

    config.load_user_datas()


def get_root():
    return os.path.dirname(os.path.abspath(__file__))


def read_file(path):
    with open(path, mode="r", encoding="utf-8-sig") as f:
        content = f.read()
    # Strip #-style comments (optionally preceded by spaces) from each line
    lines = content.split("\n")
    stripped = []
    for line in lines:
        # Match optional leading spaces + # + rest, or # inside a string value
        # We only strip # that is NOT inside a JSON string value
        idx = _comment_start_index(line)
        if idx is not None:
            stripped.append(line[:idx])
        else:
            stripped.append(line)
    return "\n".join(stripped)


def _comment_start_index(line):
    """Return the index of # that starts a comment, or None if no comment."""
    in_string = False
    escape_next = False
    for i, ch in enumerate(line):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\":
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if not in_string and ch == "#":
            return i
    return None


def conf():
    return config


def get_appdata_dir():
    data_path = os.path.join(get_root(), conf().get("appdata_dir", ""))
    if not os.path.exists(data_path):
        logger.info("[INIT] data path not exists, create it: {}".format(data_path))
        os.makedirs(data_path)
    return data_path


def subscribe_msg():
    trigger_prefix = conf().get("single_chat_prefix", [""])[0]
    msg = conf().get("subscribe_msg", "")
    return msg.format(trigger_prefix=trigger_prefix)


# global plugin config
plugin_config = {}


def write_plugin_config(pconf: dict):
    """
    写入插件全局配置
    :param pconf: 全量插件配置
    """
    global plugin_config
    for k in pconf:
        plugin_config[k.lower()] = pconf[k]


def remove_plugin_config(name: str):
    """
    移除待重新加载的插件全局配置
    :param name: 待重载的插件名
    """
    global plugin_config
    plugin_config.pop(name.lower(), None)


def pconf(plugin_name: str) -> dict:
    """
    根据插件名称获取配置
    :param plugin_name: 插件名称
    :return: 该插件的配置项
    """
    return plugin_config.get(plugin_name.lower())


# 全局配置，用于存放全局生效的状态
global_config = {"admin_users": []}
