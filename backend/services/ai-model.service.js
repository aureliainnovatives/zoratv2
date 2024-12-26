const AIModel = require('../models/AIModel');

class AIModelService {
    // Create new AI Model
    async createLLM(llmData) {
        try {
            const aiModel = new AIModel(llmData);
            return await aiModel.save();
        } catch (error) {
            throw error;
        }
    }

    // Get all AI Models with optional filtering
    async getLLMs(filter = {}) {
        try {
            return await AIModel.find(filter).sort({ createdAt: -1 });
        } catch (error) {
            throw error;
        }
    }

    // Get AI Model by ID
    async getLLMById(id) {
        try {
            return await AIModel.findById(id);
        } catch (error) {
            throw error;
        }
    }

    // Update AI Model
    async updateLLM(id, updateData) {
        try {
            return await AIModel.findByIdAndUpdate(
                id,
                updateData,
                { new: true, runValidators: true }
            );
        } catch (error) {
            throw error;
        }
    }

    // Delete AI Model
    async deleteLLM(id) {
        try {
            return await AIModel.findByIdAndDelete(id);
        } catch (error) {
            throw error;
        }
    }

    // Get AI Models by type
    async getLLMsByType(type) {
        try {
            return await AIModel.find({ type, isActive: true });
        } catch (error) {
            throw error;
        }
    }

    // Get AI Models by provider
    async getLLMsByProvider(provider) {
        try {
            return await AIModel.find({ provider, isActive: true });
        } catch (error) {
            throw error;
        }
    }

    // Toggle AI Model active status
    async toggleLLMStatus(id) {
        try {
            const aiModel = await AIModel.findById(id);
            if (!aiModel) throw new Error('AI Model not found');
            
            aiModel.isActive = !aiModel.isActive;
            return await aiModel.save();
        } catch (error) {
            throw error;
        }
    }
}

module.exports = new AIModelService(); 