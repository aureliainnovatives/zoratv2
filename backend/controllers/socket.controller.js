const socketService = require('../services/socket.service');

class SocketController {
    constructor() {
        this.socketService = socketService;
    }

    // Get active connections for a user
    async getActiveConnections(userId) {
        return await this.socketService.getUserSockets(userId);
    }

    // Broadcast message to specific user
    async broadcastToUser(userId, event, data) {
        await this.socketService.broadcastToUser(userId, event, data);
    }

    // Get all active connections from Redis
    async getAllActiveConnections() {
        const pattern = 'user:*:sockets';
        const keys = await this.socketService.pubClient.keys(pattern);
        const connections = {};

        for (const key of keys) {
            const userId = key.split(':')[1];
            const sockets = await this.socketService.pubClient.hGetAll(key);
            connections[userId] = Object.entries(sockets).map(([socketId, data]) => ({
                socketId,
                ...JSON.parse(data)
            }));
        }

        return connections;
    }
}

module.exports = new SocketController(); 