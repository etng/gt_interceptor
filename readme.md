# gt_interceptor

## intro

just intercept data used for capthca to analyze


## usage


```
pip3 install -f requirements.txt
redis-cli -n 7 flushdb
mitmdump -s js_collect_proxy.py -p 8890
python api.py
```

1. set your proxy to `<server_ip>:8890` and visit `www.geetest.com/exp_normal`
2. do drag-refresh loop
3. check `http://<server_ip>:5000/summary` for result data with jsonlines

## status

in development do not use it in production
