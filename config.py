# encoding:utf-8

import json
import logging
import os
import pickle

from common.log import logger

# 此处的配置值无实际意义，程序不会读取此处的配置，仅用于提示格式，请将配置加入到config.json中
# 将所有可用的配置项写在字典里, 全局維度,  请使用小写字母
available_setting = {
    # openai api配置
    "open_ai_api_key": "",  # openai api key
    # openai apibase，当use_azure_chatgpt为true时，需要设置对应的api base
    "open_ai_api_base": "https://api.openai.com/v1",
    "proxy": "",  # openai使用的代理
    # chatgpt模型， 当use_azure_chatgpt为true时，其名称为Azure上model deployment名称
    "model": "gpt-3.5-turbo",
    "use_azure_chatgpt": False,  # 是否使用azure的chatgpt
    "azure_deployment_id": "",  # azure 模型部署名称
    # Bot触发配置
    "single_chat_prefix": ["bot", "@bot"],  # 私聊时文本需要包含该前缀才能触发机器人回复
    "single_chat_reply_prefix": "[bot] ",  # 私聊时自动回复的前缀，用于区分真人
    "group_chat_prefix": ["@bot"],  # 群聊时包含该前缀则会触发机器人回复
    "group_chat_reply_prefix": "",  # 群聊时自动回复的前缀
    "group_chat_keyword": [],  # 群聊时包含该关键词则会触发机器人回复
    "group_at_off": False,  # 是否关闭群聊时@bot的触发
    "group_name_white_list": ["ChatGPT测试群", "ChatGPT测试群2"],  # 开启自动回复的群名称列表
    "group_name_keyword_white_list": [],  # 开启自动回复的群名称关键词列表
    "group_chat_in_one_session": ["ChatGPT测试群"],  # 支持会话上下文共享的群名称
    "trigger_by_self": False,  # 是否允许机器人触发
    "image_create_prefix": ["画", "看", "找"],  # 开启图片回复的前缀
    "concurrency_in_session": 1,  # 同一会话最多有多少条消息在处理中，大于1可能乱序
    "image_create_size": "256x256",  # 图片大小,可选有 256x256, 512x512, 1024x1024
    # chatgpt会话参数
    "expires_in_seconds": 3600,  # 无操作会话的过期时间
    "character_desc": [
        "你是ChatGPT, 一个由OpenAI训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。"
    ],  # 人格描述
    "conversation_max_tokens": 1000,  # 支持上下文记忆的最多字符数
    # chatgpt限流配置
    "rate_limit_chatgpt": 20,  # chatgpt的调用频率限制
    "rate_limit_dalle": 50,  # openai dalle的调用频率限制
    # chatgpt api参数 参考https://platform.openai.com/docs/api-reference/chat/create
    "temperature": 0.9,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "request_timeout": 60,  # chatgpt请求超时时间，openai接口默认设置为600，对于难问题一般需要较长时间
    "timeout": 120,  # chatgpt重试超时时间，在这个时间内，将会自动重试
    # 语音设置
    "speech_recognition": False,  # 是否开启语音识别
    "group_speech_recognition": False,  # 是否开启群组语音识别
    "voice_reply_voice": False,  # 是否使用语音回复语音，需要设置对应语音合成引擎的api key
    "always_reply_voice": False,  # 是否一直使用语音回复
    "voice_to_text": "openai",  # 语音识别引擎，支持openai,baidu,google,azure
    "text_to_voice": "baidu",  # 语音合成引擎，支持baidu,google,pytts(offline),azure
    # baidu 语音api配置， 使用百度语音识别和语音合成时需要
    "baidu_app_id": "",
    "baidu_api_key": "",
    "baidu_secret_key": "",
    # 1536普通话(支持简单的英文识别) 1737英语 1637粤语 1837四川话 1936普通话远场
    "baidu_dev_pid": "1536",
    # azure 语音api配置， 使用azure语音识别和语音合成时需要
    "azure_voice_api_key": "",
    "azure_voice_region": "japaneast",
    # 服务时间限制，目前支持itchat
    "chat_time_module": False,  # 是否开启服务时间限制
    "chat_start_time": "00:00",  # 服务开始时间
    "chat_stop_time": "24:00",  # 服务结束时间
    # 翻译api
    "translate": "baidu",  # 翻译api，支持baidu
    # baidu翻译api的配置
    "baidu_translate_app_id": "",  # 百度翻译api的appid
    "baidu_translate_app_key": "",  # 百度翻译api的秘钥
    # itchat的配置
    "hot_reload": False,  # 是否开启热重载
    # wechaty的配置
    "wechaty_puppet_service_token": "",  # wechaty的token
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
    # chatgpt指令自定义触发词
    "clear_memory_commands": ["#清除记忆"],  # 重置会话指令，必须以#开头
    # channel配置
    "channel_type": "wx",  # 通道类型，支持：{wx,wxy,terminal,wechatmp,wechatmp_service,wechatcom_app}
    "subscribe_msg": "",  # 订阅消息, 支持: wechatmp, wechatmp_service, wechatcom_app
    "debug": False,  # 是否开启debug模式，开启后会打印更多日志
    "appdata_dir": "",  # 数据目录
    # 插件配置
    "plugin_trigger_prefix": "$",  # 规范插件提供聊天相关指令的前缀，建议不要和管理员指令前缀"#"冲突
    # 用户个性化配置
    "relationship": {           # 配置微信名到人物关系的映射
        "nickname1":"relation1",
        "nickname2":"relation2",
        "nickname3":"relation3",
    },
    "user_configs": ["user_setting1","user_setting2","user_setting3"]       #针对用户应用的独立配置
}

user_setting = {
    "nickname" : "Sam", # 用户名
    "is_root" : False, # 拥有'root'权限的微信用户可以使用 godcmd
    "use_relationship": True,   # 让gpt bot知道用户和当前登录微信的关系
    # openai api配置
    "open_ai_api_key": "",  # openai api key
    # openai apibase，当use_azure_chatgpt为true时，需要设置对应的api base
    "open_ai_api_base": "https://api.openai.com/v1",
    "proxy": "",  # openai使用的代理
    # chatgpt模型， 当use_azure_chatgpt为true时，其名称为Azure上model deployment名称
    "model": "gpt-3.5-turbo",
    "use_azure_chatgpt": False,  # 是否使用azure的chatgpt
    "azure_deployment_id": "",  # azure 模型部署名称
    # Bot触发配置
    "single_chat_prefix": ["bot", "@bot"],  # 私聊时文本需要包含该前缀才能触发机器人回复
    "single_chat_reply_prefix": "[bot] ",  # 私聊时自动回复的前缀，用于区分真人
    "image_create_prefix": ["画", "看", "找"],  # 开启图片回复的前缀
    "concurrency_in_session": 1,  # 同一会话最多有多少条消息在处理中，大于1可能乱序
    "image_create_size": "256x256",  # 图片大小,可选有 256x256, 512x512, 1024x1024
    # chatgpt会话参数
    "expires_in_seconds": 3600,  # 无操作会话的过期时间
    "character_desc": [
        "你是ChatGPT, 一个由OpenAI训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。"
    ],  # 人格描述
    "conversation_max_tokens": 1000,  # 支持上下文记忆的最多字符数
}

# 系统配置（包含默认用户配置）
class Config(dict):
    def __init__(self, d=None):
        super().__init__()
        if d is None:
            d = {}

        # personal_settings: 以微信用户名区分的私人配置
        self.personal_settings = {}
        for k, v in d.items():
            if k != "user_configs":
                self[k] = v
                continue
            if v is None:
                continue
            for user_config in v:
                if user_config is None:
                    continue
                user_nickname = user_config["nickname"]
                self.personal_settings[user_nickname] = UserConfig(user_config)


        # user_datas: 用户数据，key为用户名，value为用户数据，也是dict
        self.user_datas = {}

    def __getitem__(self, key):
        if key not in available_setting:
            logger.warn("key {} not in available_setting".format(key))
            return None
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if key not in available_setting:
            logger.warn("key {} not in available_setting".format(key))
            return
        return super().__setitem__(key, value)


    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError as e:
            return default
        except Exception as e:
            raise e
        
        

    def __get_user_config__(self, nickname, default=None):
        return self.personal_settings.get(nickname, default)
    

    def __set_user_config__(self, nickname, key, value):
        if nickname not in self.personal_settings:
            self.personal_settings[nickname] = {}
        d = self.personal_settings.get(nickname)
        d[key] = value


    # nickname is None 时设置 全局配置
    def set_config(self, key, value, nickname=None):
        if nickname is None:
            if key in available_setting:
                super().__setitem__(key, value)
            else:
                logger.warn("nickname is none and key {} not in available_setting".format(key))
            return
        if key in user_setting:
            self.__set_user_config__(nickname, key, value)
        else:
            logger.warn("nickname {} set user config key {} not in user_setting".format(nickname, key))

    # nickname is None 时获取 全局配置
    def get_config(self, key, default=None, nickname=None):
        if nickname is None:
            if key in available_setting:
                return self.get(key, default)
            else:
                logger.warn("nickname is none and key {} not in available_setting".format(key))
            return default
        user_config = self.__get_user_config__(nickname)
        if user_config is None:
            if key in available_setting:
                return self.get(key, default)
            else:
                return default
        return user_config.get(key, default)

    # Make sure to return a dictionary to ensure atomic
    def get_user_data(self, user) -> dict:
        if self.user_datas.get(user) is None:
            self.user_datas[user] = {}
        return self.user_datas[user]

    def load_user_datas(self):
        try:
            with open(os.path.join(get_appdata_dir(), "user_datas.pkl"), "rb") as f:
                self.user_datas = pickle.load(f)
                logger.info("[Config] User datas loaded.")
        except FileNotFoundError as e:
            logger.info("[Config] User datas file not found, ignore.")
        except Exception as e:
            logger.info("[Config] User datas error: {}".format(e))
            self.user_datas = {}

    def save_user_datas(self):
        try:
            with open(os.path.join(get_appdata_dir(), "user_datas.pkl"), "wb") as f:
                pickle.dump(self.user_datas, f)
                logger.info("[Config] User datas saved.")
        except Exception as e:
            logger.info("[Config] User datas error: {}".format(e))



# 独立用户配置 （按照微信用户名配置）
class UserConfig(dict):
    def __init__(self, sys_config : Config, d=None):
        super().__init__()
        if d is None:
            d = {}
        
        self.sys_config = sys_config
        for k, v in d.items():
            self[k] = v
 
    def __getitem__(self, __key):
        if __key not in user_setting:
            if __key in available_setting:
                return self.sys_config.get(__key)
            else:
                return None
        v = super().get(__key)
        if v is None and __key in available_setting:
            v = self.sys_config[__key]
        return v
    
    def __setitem__(self, __key, __value):
        if __key not in user_setting:
            logger.warn("key {} not in user_setting".format(__key))
            return
        return super().__setitem__(__key, __value)
    
    def get(self, key, default=None):
        try:
            v = self[key]
            if v is None:
                return default
            return v
        except KeyError as e:
            return default
        except Exception as e:
            logger.warn("get key {} exception {}".format(key, e))
            return default
        


config = Config()

empty_user_config = UserConfig()


def load_config():
    global config
    config_path = "./config.json"
    if not os.path.exists(config_path):
        logger.info("配置文件不存在，将使用config-template.json模板")
        config_path = "./config-template.json"

    config_str = read_file(config_path)
    logger.debug("[INIT] config str: {}".format(config_str))

    # 将json字符串反序列化为dict类型
    config = Config(json.loads(config_str))

    # override config with environment variables.
    # Some online deployment platforms (e.g. Railway) deploy project from github directly. So you shouldn't put your secrets like api key in a config file, instead use environment variables to override the default config.
    for name, value in os.environ.items():
        name = name.lower()
        if name in available_setting:
            logger.info("[INIT] override config by environ args: {}={}".format(name, value))
            try:
                config[name] = eval(value)
            except:
                if value == "false":
                    config[name] = False
                elif value == "true":
                    config[name] = True
                else:
                    config[name] = value

    if config.get("debug", False):
        logger.setLevel(logging.DEBUG)
        logger.debug("[INIT] set log level to DEBUG")

    logger.info("[INIT] load config: {}".format(config))

    config.load_user_datas()


def get_root():
    return os.path.dirname(os.path.abspath(__file__))


def read_file(path):
    with open(path, mode="r", encoding="utf-8") as f:
        return f.read()


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
