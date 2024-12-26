const Redis = require('ioredis');
const config = require('./config');

let redisClient = null;

const createRedisClient = () => {
    if (redisClient) {
        return redisClient;
    }

    const redisConfig = {
        host: config.redis.host,
        port: config.redis.port,
        ...(config.redis.password ? { password: config.redis.password } : {}),
        retryStrategy: (times) => {
            const delay = Math.min(times * 50, 2000);
            return delay;
        }
    };

    redisClient = new Redis(redisConfig);

    redisClient.on('connect', () => {
        console.log('Redis client connected');
    });

    redisClient.on('error', (err) => {
        console.error('Redis client error:', err);
    });

    return redisClient;
};

module.exports = {
    getRedisClient: createRedisClient
}; 