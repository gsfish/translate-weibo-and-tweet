# translate-weibo-and-tweet

Translate your Weibo into English and post a Tweet. Thanks to IFTTT, Google and Tencent/NetEase.

## Usage

Register in Tencent/Youdao Cloud and Google Cloud Platform, creat an App Engine.

Run the following command to download requirements:

```
pip install -r requirements -t lib
```

Configure your KEYs in `main.py`, deploy it to your GAE service.

Create 3 IFTTT Applets:

1. when post a weibo, send it to cloud service (if Weibo then Webhooks)
2. when trigger webhook, post a tweet (if Webhooks then Twitter)
3. when trigger webhook, post a tweet with image (if Webhooks then Twitter)

Turn on the Applets and enjoy the free automatic Weibo translation service!

