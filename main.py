#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import hashlib

import requests
from flask import *


AUTH_KEY = ''

YOUDAO_APP_KEY = ''
YOUDAO_SECRET_KEY = ''
YOUDAO_API = 'https://openapi.youdao.com/api'

WEBHOOK_KEY = ''
WEBHOOK_EVENT_TEXT = 'text_weibo_posted'
WEBHOOK_EVENT_IMAGE = 'image_weibo_posted'
WEBHOOK_URL_TEXT = 'https://maker.ifttt.com/trigger/{0}/with/key/{1}'.format(WEBHOOK_EVENT_TEXT, WEBHOOK_KEY)
WEBHOOK_URL_IMAGE = 'https://maker.ifttt.com/trigger/{0}/with/key/{1}'.format(WEBHOOK_EVENT_IMAGE, WEBHOOK_KEY)

app = Flask(__name__)


@app.route('/', methods=['POST'])
def translate_and_tweet():
    data = request.get_json()
    if data['auth_key'] != AUTH_KEY:
        return jsonify({
            'detail': 'Invalid auth_key {0!r}'.format(data['auth_key'])
        }), 401

    text_raw = data['text']
    tran_salt = str(random.randint(1, 65536))
    tran_hash_str = (YOUDAO_APP_KEY+text_raw+tran_salt+YOUDAO_SECRET_KEY).encode('utf-8')
    tran_sign = hashlib.md5(tran_hash_str).hexdigest()
    tran_data = {
        'q': text_raw,
        'from': 'auto',
        'to': 'EN',
        'appKey': YOUDAO_APP_KEY,
        'salt': tran_salt,
        'sign': tran_sign,
    }
    try:
        tran_resp = requests.post(YOUDAO_API, data=tran_data)
    except Exception as e:
        return jsonify({
            'detail': str(e)
        }), 500

    tran_res = tran_resp.json()
    if tran_res['errorCode'] != '0':
        return jsonify({
            'detail': 'Translation Error: Failed to translate {0!r}'.format(text_raw)
        }), 500

    text_tran = tran_res['translation'][0]
    image_url = data.get('image_url', None)
    if image_url:
        url = WEBHOOK_URL_IMAGE
    else:
        url = WEBHOOK_URL_TEXT
    payload = {
        'value1': AUTH_KEY,
        'value2': text_tran,
        'value3': image_url
    }

    try:
        requests.post(url, json=payload)
    except Exception:
        return jsonify({
            'detail': 'POST Error: Failed to trigger webhook service'
        }), 500

    return jsonify({
        'detail': 'Success.'
    }), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
