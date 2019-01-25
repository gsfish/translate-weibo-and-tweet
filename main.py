#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import hmac
import hashlib
import base64
import random
from urllib.parse import urlparse

import requests
from flask import *


# in post body when webhook send requests, and ifttt filter after webhook triggered
AUTH_KEY = ''
# for tencent translator api
TENCENT_SECRET_ID = ''
TENCENT_SECRET_KEY = ''
TENCENT_API = 'https://tmt.tencentcloudapi.com/'
# for ifttt webhooks service
WEBHOOK_KEY = ''
WEBHOOK_EVENT_TEXT = 'text_weibo_posted'
WEBHOOK_EVENT_IMAGE = 'image_weibo_posted'
WEBHOOK_URL_TEXT = 'https://maker.ifttt.com/trigger/{0}/with/key/{1}'.format(WEBHOOK_EVENT_TEXT, WEBHOOK_KEY)
WEBHOOK_URL_IMAGE = 'https://maker.ifttt.com/trigger/{0}/with/key/{1}'.format(WEBHOOK_EVENT_IMAGE, WEBHOOK_KEY)

app = Flask(__name__)


def get_sign(params):
    method = 'GET'
    endpoint = urlparse(TENCENT_API).netloc
    query_str = '&'.join('{0}={1}'.format(k, params[k]) for k in sorted(params))
    str_to_sign = '{0}{1}/?{2}'.format(method, endpoint, query_str)
    hmac_str = hmac.new(TENCENT_SECRET_KEY.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha1).digest()
    signature = base64.b64encode(hmac_str)
    return signature


@app.route('/', methods=['POST'])
def translate_and_tweet():
    # validate auth_key
    data = request.get_json()
    if data['auth_key'] != AUTH_KEY:
        msg = 'Authorization Error: Invalid auth_key {0!r}'.format(data['auth_key'])
        app.logger.warning(msg)
        return jsonify({'detail': msg}), 401

    # translate weibo text into english
    tran_payload = {
        'Action': 'TextTranslate',
        'Version': '2018-03-21',
        'SecretId': TENCENT_SECRET_ID,
        'Timestamp': int(time.time()),
        'Nonce': random.randint(1, 65536),
        'Region': 'na-siliconvalley',
        'SourceText': data['text'],
        'Source': 'auto',
        'Target': 'en',
        'ProjectId': 0
    }
    tran_payload['Signature'] = get_sign(tran_payload)
    tran_resp = requests.get(TENCENT_API, params=tran_payload)
    tran_res = tran_resp.json()

    if 'Error' in tran_res['Response']:
        msg = 'Translation Error: {0}'.format(tran_res['Response']['Error']['Message'])
        app.logger.error(msg)
        return jsonify({'detail': msg}), 500

    # post a tweet
    tweet_text = tran_res['Response']['TargetText']
    tweet_image_url = data.get('image_url', None)
    if tweet_image_url:
        tweet_url = WEBHOOK_URL_IMAGE
    else:
        tweet_url = WEBHOOK_URL_TEXT
    tweet_payload = {
        'value1': AUTH_KEY,
        'value2': tweet_text,
        'value3': tweet_image_url
    }

    try:
        requests.post(tweet_url, json=tweet_payload)
    except Exception:
        msg = 'POST Error: Failed to trigger webhook service'
        app.logger.error(msg)
        return jsonify({'detail': msg}), 500
    else:
        return jsonify({'detail': 'Success'}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
