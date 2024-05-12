bind = '0.0.0.0:5000'


workers = 2


max_requests = 1000


timeout = 30

# Log level
loglevel = 'info'

# Specify the access log file
accesslog = '-'

app_module = 'runserver'
app = getattr(__import__(app_module), 'app')