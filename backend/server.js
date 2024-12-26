const express = require("express");
const dotenv = require("dotenv");
const connectDB = require("./config/db.config");
const config = require("./config/config");
const cors = require("cors");
const http = require('http');

const authRoutes = require("./routes/auth.routes");
const roleRoutes = require("./routes/role.routes");
const { verifyToken } = require("./middleware/auth.middleware");

// Import Routes
const permissionRoutes = require("./routes/permission.routes");
const moduleRoutes = require("./routes/module.routes");
const userRoutes = require("./routes/user.routes");
const socketRoutes = require("./routes/socket.routes");

// Import Socket Service
const socketService = require("./services/socket.service");

// Initialize app
dotenv.config();
connectDB();

const app = express();
const server = http.createServer(app);

app.use(
    cors({
        origin: function (origin, callback) {
            if (!origin) return callback(null, true);
            if (config.cors.origins.includes(origin)) {
                return callback(null, true);
            } else {
                return callback(new Error("Not allowed by CORS"));
            }
        },
        credentials: config.cors.credentials,
    })
);

app.use(express.json());

// Routes Mapping
app.use("/api/auth", authRoutes);
app.use("/api/roles", verifyToken, roleRoutes);
app.use("/api/permissions", verifyToken, permissionRoutes);
app.use("/api/modules", verifyToken, moduleRoutes);
app.use("/api/users", verifyToken, userRoutes);
app.use("/api/socket", verifyToken, socketRoutes);

// Test Route
app.get("/", (req, res) => {
    res.send(`Agent Platform API running in ${process.env.MODE} mode.`);
});

// Initialize Socket.IO
socketService.initialize(server);

// Start Server
server.listen(config.port, () => {
    console.log(`Server running on port ${config.port}`);
    console.log('Socket.IO server initialized');
});
