const express = require('express');
const router = express.Router();
const socketController = require('../controllers/socket.controller');
const { verifyToken } = require('../middleware/auth.middleware');

// Get active connections for the authenticated user
router.get('/connections', verifyToken, async (req, res) => {
    try {
        const connections = await socketController.getActiveConnections(req.user.userId);
        res.json({ success: true, connections });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get all active connections (admin only)
router.get('/connections/all', verifyToken, async (req, res) => {
    try {
        // TODO: Add admin check middleware
        const connections = await socketController.getAllActiveConnections();
        res.json({ success: true, connections });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

module.exports = router; 