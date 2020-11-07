import redis

redis_host = "localhost"
redis_port = 6379
redis_password = ""

try:
	r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
except Exception as e:
	print(e)

def cacheData(key, value):
	try:
		r.set(key, value)
	except Exception as e:
		print(e)

def getCached(key):
	msg = r.get(key)
	return msg