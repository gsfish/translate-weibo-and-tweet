#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import hashlib

import requests
from flask import *


# in post body when webhook send requests, and ifttt filter after webhook triggered
AUTH_KEY = ''
# for youdao cloud api
YOUDAO_APP_KEY = ''
YOUDAO_SECRET_KEY = ''
YOUDAO_API = 'https://openapi.youdao.com/api'
# for ifttt webhooks service
WEBHOOK_KEY = ''
WEBHOOK_EVENT_TEXT = 'text_weibo_posted'
WEBHOOK_EVENT_IMAGE = 'image_weibo_posted'
WEBHOOK_URL_TEXT = 'https://maker.ifttt.com/trigger/{0}/with/key/{1}'.format(WEBHOOK_EVENT_TEXT, WEBHOOK_KEY)
WEBHOOK_URL_IMAGE = 'https://maker.ifttt.com/trigger/{0}/with/key/{1}'.format(WEBHOOK_EVENT_IMAGE, WEBHOOK_KEY)

app = Flask(__name__)


@app.route('/', methods=['POST'])
def translate_and_tweet():
    # validate auth_key
    data = request.get_json()
    if data['auth_key'] != AUTH_KEY:
        msg = 'Invalid auth_key {0!r}'.format(data['auth_key'])
        app.logger.warning(msg)
        return jsonify({'detail': msg}), 401

    # translate weibo text into english
    text_raw = data['text']
    tran_salt = str(random.randint(1, 65536))
    tran_hash_str = (YOUDAO_APP_KEY+text_raw+tran_salt+YOUDAO_SECRET_KEY).encode('utf-8')
    tran_sign = hashlib.md5(tran_hash_str).hexdigest()
    tran_payload = {
        'q': text_raw,
        'from': 'auto',
        'to': 'EN',
        'appKey': YOUDAO_APP_KEY,
        'salt': tran_salt,
        'sign': tran_sign,
    }
    tran_resp = requests.post(YOUDAO_API, data=tran_payload)
    tran_res = tran_resp.json()

    if tran_res['errorCode'] != '0':
        msg = 'Translation Error: Failed to translate {0!r}'.format(text_raw)
        app.logger.error(msg)
        return jsonify({'detail': msg}), 500

    # post a tweet
    post_text = tran_res['translation'][0]
    post_image_url = data.get('image_url', None)
    if post_image_url:
        post_url = WEBHOOK_URL_IMAGE
    else:
        post_url = WEBHOOK_URL_TEXT
    post_payload = {
        'value1': AUTH_KEY,
        'value2': post_text,
        'value3': post_image_url
    }

    try:
        requests.post(post_url, json=post_payload)
    except Exception:
        msg = 'POST Error: Failed to trigger webhook service'
        app.logger.error(msg)
        return jsonify({'detail': msg}), 500
    else:
        return jsonify({'detail': 'Success'}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
