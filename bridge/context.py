# encoding:utf-8

from enum import Enum


class ContextType(Enum):
    TEXT = 1  # 文本消息
    VOICE = 2  # 音频消息
    IMAGE = 3  # 图片消息
    IMAGE_CREATE = 10  # 创建图片命令
    JOIN_GROUP = 20  # 加入群聊
    PATPAT = 21  # 拍了拍

    def __str__(self):
        return self.name


class Context:
    def __init__(self, type: ContextType = None, content=None, kwargs=dict()):
        self.type = type
        self.content = content
        self.kwargs = kwargs

    def __contains__(self, key):
        if key == "type":
            return self.type is not None
        elif key == "content":
            return self.content is not None
        elif key == "from_user_nickname":
            return self.from_user_nickname is not None
        else:
            return key in self.kwargs

    def __getitem__(self, key):
        if key == "type":
            return self.type
        elif key == "content":
            return self.content
        elif key == "from_user_nickname":
            return self.from_user_nickname
        else:
            return self.kwargs[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        if key == "type":
            self.type = value
        elif key == "content":
            self.content = value
        elif key == "from_user_nickname":
            self.from_user_nickname = value
        else:
            self.kwargs[key] = value

    def __delitem__(self, key):
        if key == "type":
            self.type = None
        elif key == "content":
            self.content = None
        elif key == "from_user_nickname":
            self.from_user_nickname = None
        else:
            del self.kwargs[key]

    def __str__(self):
        return "Context(type={}, content={}, kwargs={})".format(self.type, self.content, self.kwargs)
