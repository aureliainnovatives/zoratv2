const express = require('express');
const router = express.Router();
const aiModelController = require('../controllers/ai-model.controller');
const auth = require('../middleware/auth');
const { checkPermission } = require('../middleware/permission');

// Create new AI Model
router.post('/',
    auth,
    checkPermission('create', 'aimodel'),
    aiModelController.createLLM
);

// Get all AI Models
router.get('/',
    auth,
    checkPermission('read', 'aimodel'),
    aiModelController.getLLMs
);

// Get AI Model by ID
router.get('/:id',
    auth,
    checkPermission('read', 'aimodel'),
    aiModelController.getLLMById
);

// Update AI Model
router.put('/:id',
    auth,
    checkPermission('update', 'aimodel'),
    aiModelController.updateLLM
);

// Delete AI Model
router.delete('/:id',
    auth,
    checkPermission('delete', 'aimodel'),
    aiModelController.deleteLLM
);

// Get AI Models by type
router.get('/type/:type',
    auth,
    checkPermission('read', 'aimodel'),
    aiModelController.getLLMsByType
);

// Get AI Models by provider
router.get('/provider/:provider',
    auth,
    checkPermission('read', 'aimodel'),
    aiModelController.getLLMsByProvider
);

// Toggle AI Model status
router.patch('/:id/toggle-status',
    auth,
    checkPermission('update', 'aimodel'),
    aiModelController.toggleLLMStatus
);

module.exports = router; 