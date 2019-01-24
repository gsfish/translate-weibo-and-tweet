# translate-weibo-and-tweet

Translate your Weibo into English and post a Tweet. Thanks for IFTTT, Google and NetEase.

## Usage

Register in Youdao Cloud and Google Cloud Platform, creat an App Engine.

Run the following command to download requirements:

```
pip install -r requirements -t lib
```

Configure your KEYs in `app.py`, deploy it to your GAE service.

Create 3 IFTTT Applets:

1. when post a weibo, send it to cloud service
2. when trigger webhook, post a tweet
3. when trigger webhook, post a tweet with image

Turn on and enjoy the automatic Weibo translation service!

