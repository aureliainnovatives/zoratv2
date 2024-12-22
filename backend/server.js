const express = require("express");
const dotenv = require("dotenv");
const connectDB = require("./config/db.config");
const config = require("./config/config");
const cors = require("cors"); // Import CORS middleware


const authRoutes = require("./routes/auth.routes");
const roleRoutes = require("./routes/role.routes");
const { verifyToken } = require("./middleware/auth.middleware");

// Import Routes
const permissionRoutes = require("./routes/permission.routes");
const moduleRoutes = require("./routes/module.routes");
const userRoutes = require("./routes/user.routes");

// Initialize app
dotenv.config();
connectDB();

const app = express();
const allowedOrigins = ["http://localhost:4200", "https://account.zorat.io"];
app.use(
  cors({
    origin: function (origin, callback) {
      // Allow requests with no origin (e.g., mobile apps, Postman)
      if (!origin) return callback(null, true);
      if (allowedOrigins.includes(origin)) {
        return callback(null, true);
      } else {
        return callback(new Error("Not allowed by CORS"));
      }
    },
    credentials: true, // Allow credentials like cookies or headers
  })
);

app.use(express.json());

// Routes Mapping

app.use("/api/auth", authRoutes);
app.use("/api/roles", verifyToken, roleRoutes); // Protected Route
app.use("/api/permissions", verifyToken, permissionRoutes);
app.use("/api/modules", verifyToken, moduleRoutes);
app.use("/api/users", verifyToken, userRoutes);


// Test Route
app.get("/", (req, res) => {
  res.send(`Agent Platform API running in ${process.env.MODE} mode.`);
});

// Start Server
app.listen(config.port, () => {
  console.log(`Server running on port ${config.port}`);
});
