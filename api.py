from flask import (
    Flask,
    request,
    session,
    g,
    redirect,
    url_for,
    abort,
    render_template,
    flash,
)
import json
from flask_cors import (
    CORS,
    cross_origin
)
import time
import os
from redis import StrictRedis

app = Flask(__name__)
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='4th',
))
redis = StrictRedis(db=7)


@app.route("/", methods=['GET', 'POST'])
@cross_origin('*')
def home():
    results = []
    gt = redis.get('geetest:latest_gt')
    for data, score in redis.zrange(
        'geetest_response:{}'.format(gt),
        0,
        100000,
        desc=True,
        withscores=True,
    ):
        # import ipdb;ipdb.set_trace()
        # results.append(json.loads(str(data)))
        # line = str(data).strip()
        # print(line)
        try:
            results.append(json.dumps(json.loads(data)))
        except Exception as e:
            print(e.message)
            import ipdb;ipdb.set_trace()
    return "\n".join(results)
    # return json.dumps(results)
    # import ipdb;ipdb.set_trace()
    # return json.dumps(results)


@app.route("/proxy/toggle", methods=['GET', 'POST'])
@cross_origin('*')
def toggle_proxy():
    rk = 'proxy:on'
    old = redis.get(rk)
    # import ipdb;ipdb.set_trace()
    flag = b'on' if old == b'off' else b'off'
    redis.set(rk, flag)
    return flag


@app.route("/summary", methods=['GET', 'POST'])
@cross_origin('*')
def summary():
    rows = []
    challenges = sorted(redis.smembers('gt_challenges'))
    for challenge in challenges:
        data = redis.hgetall('gt_challenge:{}'.format(challenge.decode('utf-8')))
        # import ipdb;ipdb.set_trace()
        for field in (b'data', b'trace', b'response', ):
            data[field] = json.loads(data[field])
        data[b'offset'] = int(data[b'offset'])

        rows.append(json.dumps({k.decode('utf-8'): v for k, v in data.items()}))
    return "\n".join(rows)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    # app.run()
