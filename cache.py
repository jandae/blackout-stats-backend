import redis
from config import Config

try:
	r = redis.StrictRedis(
			host=Config.redis_host,
			port=Config.redis_port,
			password=Config.redis_password,
			decode_responses=True
		)
except Exception as e:
	print(e)

def cacheData(key, value):
	try:
		r.hmset(key, value)
	except Exception as e:
		print(e)

def getCached(key):
	msg = r.hgetall(key)
	return msg

def getSingleCached(key):
	msg = r.get(key)
	return msg