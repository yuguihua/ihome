
import redis


class Redis:
    cache_prefix = 'ihome_robot_'

    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self.r = redis.Redis(connection_pool=pool,decode_responses=True)

    def getInstance(self):
        return self.r

    def loadData(self, key,format='string'):
        key = self.prefixKey(key)
        data=self.r.get(key)
        if data!=None:
            data=data.decode(encoding="utf-8")
            if format=='json':
                from ast import literal_eval
                data = literal_eval(data)
        return data

    def saveData(self, key, value, lifetime=None):
        key = self.prefixKey(key)
        self.r.set(key, value, lifetime)

    def remove(self,key):
        return self.r.delete(key)

    def prefixKey(self, key):
        return self.cache_prefix + key

rds = Redis()
