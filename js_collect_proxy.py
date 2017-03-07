from mitmproxy import ctx
import json
import re
import os
import time
from redis import StrictRedis
from urllib.parse import urlparse, parse_qsl, urlencode
from mitmproxy import http
redis = StrictRedis(db=7)


def start():
    ctx.log.info("geetest js proxy started")
    # ctx.log.error("This is an error.")


def request(flow):
    # print("handle request: %s%s" % (flow.request.host, flow.request.path))
    url = flow.request.pretty_url
    ctx.log.info("url is: {}".format(url))
    parts = urlparse(url)
    base_url, qsa = (
        '{}://{}{}'.format(parts.scheme, parts.netloc, parts.path),
        dict(parse_qsl(parts.query)) if parts.query else dict(),
    )
    # http://static.geetest.com/static/js/geetest.5.10.0.js
    if re.match('.*/js/geetest\.[\d\.]+\.js$', base_url):
        local_file = 'geetest.5.10.0.js'
        content = open(local_file).read()
        if 'callback' in qsa:
            content = '{}({})'.format(qsa['callback'], content)
        flow.response = http.HTTPResponse.make(200, content)
        flow.response.headers["MITMProxy"] = "tampered"
        return

    if base_url == 'http://api.geetest.com/ajax.php':
        ctx.log.info("is gt ajax response: {}".format(url))
        challenge = qsa['challenge']
        redis.sadd('gt_challenges', challenge)
        rk = 'gt_challenge:{}'.format(challenge)
        redis.hset(rk, 'offset', qsa.pop('offset', ''))
        redis.hset(rk, 'trace', qsa.pop('trace', ''))
        flow.request.url = '{}?{}'.format(base_url, urlencode(qsa))
        ctx.log.info("url changed: {}".format(flow.request.url))
        # import ipdb;ipdb.set_trace()


def parse_jsonp(content):
    return json.loads(re.match('^[^\(]+\((.*)\)$', content.decode('utf-8')).group(1))


def response(flow):
    url = flow.request.pretty_url
    parts = urlparse(url)
    base_url, qsa = (
        '{}://{}{}'.format(parts.scheme, parts.netloc, parts.path),
        dict(parse_qsl(parts.query)) if parts.query else dict(),
    )
    if base_url in (
        'http://api.geetest.com/get.php',
        'http://api.geetest.com/refresh.php',
    ):
        print(flow.request.pretty_url)
        print(flow.response.content)
        # import ipdb;ipdb.set_trace()
        response = parse_jsonp(flow.response.content)
        challenge = response['challenge']
        redis.sadd('gt_challenges', challenge)
        redis.hset('gt_challenge:{}'.format(challenge), 'data', json.dumps(response))
    elif base_url == 'http://api.geetest.com/ajax.php':
        challenge = qsa['challenge']
        redis.sadd('gt_challenges', challenge)
        response = parse_jsonp(flow.response.content)
        redis.hset('gt_challenge:{}'.format(challenge), 'response', json.dumps(response))
