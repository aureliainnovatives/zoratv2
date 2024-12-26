const aiModelService = require('../services/ai-model.service');

class AIModelController {
    // Create new AI Model
    async createLLM(req, res) {
        try {
            const aiModel = await aiModelService.createLLM(req.body);
            res.status(201).json({
                success: true,
                data: aiModel,
                message: 'AI Model created successfully'
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                message: error.message
            });
        }
    }

    // Get all AI Models
    async getLLMs(req, res) {
        try {
            const filter = {};
            if (req.query.type) filter.type = req.query.type;
            if (req.query.provider) filter.provider = req.query.provider;
            if (req.query.isActive) filter.isActive = req.query.isActive === 'true';

            const aiModels = await aiModelService.getLLMs(filter);
            res.status(200).json({
                success: true,
                data: aiModels,
                message: 'AI Models retrieved successfully'
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                message: error.message
            });
        }
    }

    // Get AI Model by ID
    async getLLMById(req, res) {
        try {
            const aiModel = await aiModelService.getLLMById(req.params.id);
            if (!aiModel) {
                return res.status(404).json({
                    success: false,
                    message: 'AI Model not found'
                });
            }
            res.status(200).json({
                success: true,
                data: aiModel,
                message: 'AI Model retrieved successfully'
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                message: error.message
            });
        }
    }

    // Update AI Model
    async updateLLM(req, res) {
        try {
            const aiModel = await aiModelService.updateLLM(req.params.id, req.body);
            if (!aiModel) {
                return res.status(404).json({
                    success: false,
                    message: 'AI Model not found'
                });
            }
            res.status(200).json({
                success: true,
                data: aiModel,
                message: 'AI Model updated successfully'
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                message: error.message
            });
        }
    }

    // Delete AI Model
    async deleteLLM(req, res) {
        try {
            const aiModel = await aiModelService.deleteLLM(req.params.id);
            if (!aiModel) {
                return res.status(404).json({
                    success: false,
                    message: 'AI Model not found'
                });
            }
            res.status(200).json({
                success: true,
                data: aiModel,
                message: 'AI Model deleted successfully'
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                message: error.message
            });
        }
    }

    // Get AI Models by type
    async getLLMsByType(req, res) {
        try {
            const aiModels = await aiModelService.getLLMsByType(req.params.type);
            res.status(200).json({
                success: true,
                data: aiModels,
                message: 'AI Models retrieved successfully'
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                message: error.message
            });
        }
    }

    // Get AI Models by provider
    async getLLMsByProvider(req, res) {
        try {
            const aiModels = await aiModelService.getLLMsByProvider(req.params.provider);
            res.status(200).json({
                success: true,
                data: aiModels,
                message: 'AI Models retrieved successfully'
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                message: error.message
            });
        }
    }

    // Toggle AI Model status
    async toggleLLMStatus(req, res) {
        try {
            const aiModel = await aiModelService.toggleLLMStatus(req.params.id);
            res.status(200).json({
                success: true,
                data: aiModel,
                message: 'AI Model status toggled successfully'
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                message: error.message
            });
        }
    }
}

module.exports = new AIModelController(); 