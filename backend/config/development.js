module.exports = {
    port: process.env.PORT || 3000,
    jwtSecret: process.env.JWT_SECRET || 'your-secret-key',
    mongoUri: 'mongodb://localhost:27017/zoratv2',
    redis: {
        host: 'localhost',
        port: 6379,
        password: null
    },
    cors: {
        origins: ["http://localhost:4200"],
        credentials: true
    },
    ai: {
        baseUrl: 'http://127.0.0.1:5001/api/v1',
        timeout: 60000 // 60 seconds
    }
};
  