module.exports = {
    port: process.env.PORT || 3000,
    jwtSecret: process.env.JWT_SECRET || 'your-secret-key',
    mongoUri: 'mongodb://localhost:27017/zoratv2',
    redis: {
        host: process.env.REDIS_HOST,
        port: parseInt(process.env.REDIS_PORT) || 6379,
        password: process.env.REDIS_PASSWORD
    },
    cors: {
        origins: ["https://account.zorat.io"],
        credentials: true
    }
};
  