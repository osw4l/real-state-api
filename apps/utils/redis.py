import redis
import json


class RedisClient:
    client: redis.Redis

    def __init__(self, host: str, port: int):
        self.client = redis.Redis(
            host=host,
            port=port
        )

    def get(self, key: str):
        return self.client.get(key)

    def get_json(self, key: str):
        data = self.client.get(key)
        try:
            data = json.loads(data)
        except Exception as e:
            data = {}
        return data

    def set(self, key: str, value: str):
        self.client.set(key, value)

    def get_setup(self):
        return self.get_json('setup')

    def delete(self, key: str):
        self.client.delete(key)


client = RedisClient(host='redis', port=6379)
