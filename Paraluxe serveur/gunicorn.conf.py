bind = '127.0.0.1:8502'
workers = 1
loglevel = 'debug'
accesslog = '/var/log/gunicorn/access_log_paraluxe.log'
acceslogformat ="%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
errorlog =  '/var/log/gunicorn/error_log_paraluxe.log'
capture_output = True
