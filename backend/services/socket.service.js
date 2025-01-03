const jwt = require('jsonwebtoken');
const config = require('../config/config');
const { createAdapter } = require('@socket.io/redis-adapter');
const { getRedisClient } = require('../config/redis.config');
const aiService = require('./ai.service');

class SocketService {
    constructor() {
        this.io = null;
        this.agentNamespace = null;
        this.redisClient = getRedisClient();
        this.pubClient = this.redisClient.duplicate();
        this.subClient = this.redisClient.duplicate();
        this.activeConnections = new Map();
        this.socketToUser = new Map();
    }

    async initialize(server) {
        this.io = require('socket.io')(server, {
            cors: {
                origin: config.cors.origins,
                methods: ["GET", "POST"],
                credentials: config.cors.credentials
            },
            path: '/socket.io'
        });

        // Setup Redis adapter
        this.io.adapter(createAdapter(this.pubClient, this.subClient));

        // Create agent chat namespace
        this.agentNamespace = this.io.of('/agent-chat');
        
        // Setup middleware for the namespace
        this.setupMiddleware();
        
        // Setup event handlers for the namespace
        this.setupEventHandlers();
        
        console.log('Socket.IO initialized with Redis adapter and /agent-chat namespace');
    }

    setupMiddleware() {
        this.agentNamespace.use(async (socket, next) => {
            try {
                const authHeader = socket.handshake.auth.token;
                if (!authHeader) {
                    console.log('No token provided');
                    return next(new Error('Authentication token missing'));
                }

                // Extract token from Bearer format
                const token = authHeader.startsWith('Bearer ') 
                    ? authHeader.slice(7) 
                    : authHeader;

                try {
                    const decoded = jwt.verify(token, config.jwtSecret);
                    if (!decoded || !decoded.id) {
                        console.error('Invalid token structure:', decoded);
                        return next(new Error('Invalid token structure'));
                    }

                    socket.userId = decoded.id;
                    console.log('Token verified for user:', socket.userId);

                    // Store connection in Redis using SET instead of HSET
                    const connectionData = JSON.stringify({
                        connectionTime: new Date(),
                        lastActive: new Date()
                    });

                    try {
                        // Using SET instead of HSET for Redis
                        await this.redisClient.set(
                            `socket:${socket.id}`,
                            connectionData
                        );
                        await this.redisClient.set(
                            `user:${socket.userId}:socket:${socket.id}`,
                            'connected'
                        );
                        console.log('Connection stored in Redis for user:', socket.userId);
                        next();
                    } catch (redisError) {
                        console.error('Redis error:', redisError);
                        // Continue even if Redis fails
                        next();
                    }
                } catch (jwtError) {
                    console.error('JWT verification failed:', jwtError);
                    next(new Error('Invalid token'));
                }
            } catch (error) {
                console.error('Socket authentication error:', error);
                next(new Error('Authentication error'));
            }
        });
    }

    setupEventHandlers() {
        this.agentNamespace.on('connection', (socket) => {
            console.log('New connection to /agent-chat namespace');
            this.handleConnection(socket);

            // Log all incoming events for debugging
            socket.onAny((eventName, ...args) => {
                console.log(`Received event "${eventName}":`, args);
            });

            // Handle messages
            socket.on('message', async (data) => {
                console.log('Received message from client:', data);
                try {
                    // Ensure data has the required fields
                    if (!data || !data.content) {
                        throw new Error('Invalid message format');
                    }

                    await this.handleMessage(socket, {
                        content: data.content,
                        llm_name: data.llm_name || 'GPT-3.5 Turbo',
                        useStreaming: data.useStreaming !== false, // default to true if not specified
                        agent_id: data.agent_id // Pass through agent_id if provided
                    });
                } catch (error) {
                    console.error('Error handling message:', error);
                    socket.emit('chat-error', {
                        message: error.message || 'Error processing message'
                    });
                }
            });

            socket.on('disconnect', () => this.handleDisconnect(socket));
        });
    }

    async handleConnection(socket) {
        const userId = socket.userId;
        
        if (!this.activeConnections.has(userId)) {
            this.activeConnections.set(userId, new Set());
        }
        this.activeConnections.get(userId).add(socket.id);
        this.socketToUser.set(socket.id, userId);

        // Emit connection status
        socket.emit('connection-status', {
            status: 'connected',
            userId: userId,
            socketId: socket.id,
            timestamp: new Date()
        });

        console.log(`User ${userId} connected with socket ${socket.id} in /agent-chat namespace`);
    }

    async handleDisconnect(socket) {
        const userId = this.socketToUser.get(socket.id);
        if (userId) {
            try {
                // Remove from Redis
                await this.redisClient.del(`socket:${socket.id}`);
                await this.redisClient.del(`user:${userId}:socket:${socket.id}`);

                // Remove from local maps
                const userSockets = this.activeConnections.get(userId);
                if (userSockets) {
                    userSockets.delete(socket.id);
                    if (userSockets.size === 0) {
                        this.activeConnections.delete(userId);
                    }
                }
                this.socketToUser.delete(socket.id);
                console.log(`Socket ${socket.id} disconnected and cleaned up for user ${userId}`);
            } catch (error) {
                console.error('Error during disconnect cleanup:', error);
            }
        }
    }

    async handleMessage(socket, message) {
        try {
            console.log('Processing message for user:', socket.userId);
            console.log('Socket details:', {
                id: socket.id,
                namespace: socket.nsp.name,
                rooms: Array.from(socket.rooms)
            });
            console.log('Message data:', message);
            
            // Explicitly check if streaming is enabled and get endpoint
            const useStreaming = message.useStreaming === true;
            const endpoint = message.endpoint || (useStreaming ? '/agent/chat/stream' : '/agent/chat');
            
            console.log('Message configuration:', {
                mode: useStreaming ? 'streaming' : 'non-streaming',
                endpoint: endpoint,
                llm: message.llm_name
            });
            
            if (useStreaming) {
                console.log('Using streaming mode with endpoint:', endpoint);
                // Handle streaming mode
                const stream = await aiService.chatStream(message.content, message.llm_name, endpoint);
                console.log('Received stream from AI service');

                // Handle Node.js stream
                stream.on('data', chunk => {
                    try {
                        const text = chunk.toString();
                        console.log('Received chunk:', text);
                        
                        const lines = text.split('\n');
                        for (const line of lines) {
                            if (line.trim() && line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.slice(6));
                                    console.log('Emitting chunk to socket:', {
                                        socketId: socket.id,
                                        data: data
                                    });
                                    
                                    socket.emit('chat-response', {
                                        type: 'chunk',
                                        data: data
                                    });
                                } catch (e) {
                                    console.error('Error parsing SSE data:', e);
                                }
                            }
                        }
                    } catch (error) {
                        console.error('Error processing chunk:', error);
                    }
                });

                stream.on('end', () => {
                    console.log('Stream ended, emitting complete to socket:', socket.id);
                    socket.emit('chat-response', {
                        type: 'complete'
                    });
                });

                stream.on('error', (error) => {
                    console.error('Stream error:', error);
                    socket.emit('chat-error', {
                        message: 'Error processing chat stream'
                    });
                });
            } else {
                console.log('Using non-streaming mode with endpoint:', endpoint);
                // Handle non-streaming mode
                const response = await aiService.chat(
                    message.content, 
                    message.llm_name, 
                    endpoint,
                    message.agent_id // Pass agent_id to AI service
                );
                console.log('Received non-streaming response:', response);
                socket.emit('chat-response', {
                    type: 'message',
                    data: response
                });
            }
        } catch (error) {
            console.error('AI service error:', error);
            socket.emit('chat-error', {
                message: error.message || 'Error processing chat request'
            });
        }
    }

    // Utility methods
    async getUserSockets(userId) {
        try {
            const pattern = `user:${userId}:socket:*`;
            const keys = await this.redisClient.keys(pattern);
            return keys.map(key => key.split(':').pop());
        } catch (error) {
            console.error('Error getting user sockets:', error);
            return [];
        }
    }

    async broadcastToUser(userId, event, data) {
        try {
            const sockets = await this.getUserSockets(userId);
            sockets.forEach(socketId => {
                this.agentNamespace.to(socketId).emit(event, data);
            });
        } catch (error) {
            console.error('Error broadcasting to user:', error);
        }
    }

    // Cleanup method (call this when shutting down the server)
    async cleanup() {
        try {
            if (this.pubClient) await this.pubClient.disconnect();
            if (this.subClient) await this.subClient.disconnect();
            if (this.redisClient) await this.redisClient.disconnect();
        } catch (error) {
            console.error('Error during cleanup:', error);
        }
    }
}

module.exports = new SocketService(); 