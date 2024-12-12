# encoding:utf-8

import redis
from conf import config
from qfcommon3.base import redispool

redis_pool = redis.Redis(**config.REDIS_CONF)
redispool.patch()
