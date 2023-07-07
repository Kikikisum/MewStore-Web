import datetime
import json

from flask import request
from flask_socketio import join_room, emit, Namespace

from mysql import db, Messages
from utils.snowflake import id_generate
from utils.time import time_transform
from utils.Token import get_id, get_expiration


class Message(Namespace):  # 聊天功能
    def on_connect(self):
        token = request.headers.get('Authorization')
        if get_expiration(token):
            uid = get_id(token)
            join_room(uid)  # 将用户添加到以其id为唯一标识符的房间
            emit('response', {'code': 200, 'message': '连接成功'})
            self.send_offline_messages(uid)
        else:
            emit('response', {'code': 401, 'message': '连接失败'})

    def on_message(self, receive_id, messages):
        token = request.headers.get('Authorization')
        if get_expiration(token):
            messages_dict = json.loads(messages)
            message = messages_dict.get('message')  # 获取消息内容
            messages = Messages(id=id_generate('message'), isSystem=1, send_id=6, receive_id=receive_id,
                                message=message, send_time=datetime.datetime.utcnow(), type=0, is_read=0)
            db.session.add(messages)
            db.session.flush()
            db.session.commit()
            emit('response', {'code': 200, 'message': message, 'message_id': str(messages.id)},
                 room=receive_id)  # 发送系统消息给接收者
        else:
            emit('response', {'code': 400, 'message': '发送失败'})

    def send_offline_messages(self, receive_id):
        # 查询数据库中针对接收者的未读消息
        offline_messages = Messages.query.filter_by(receive_id=receive_id, send_id=6, is_read=0).all()

        # 将未读消息发送给接收者
        for message in offline_messages:
            emit('response',
                 {'code': 200, 'message': message.message, 'send_id': str(message.send_id), 'type': message.type,
                  'message_id': str(message.id), 'send_time': time_transform(message.send_time)},
                 room=receive_id)
