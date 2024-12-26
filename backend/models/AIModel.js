const mongoose = require('mongoose');

const llmSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        unique: true,
        trim: true
    },
    description: {
        type: String,
        required: true
    },
    type: {
        type: String,
        required: true,
        enum: ['API_BASED', 'LOCAL_URL'],
        default: 'API_BASED'
    },
    provider: {
        type: String,
        required: true,
        enum: ['OPENAI', 'ANTHROPIC', 'GOOGLE', 'LOCAL'],
        default: 'OPENAI'
    },
    apiKey: {
        type: String,
        required: function() {
            return this.type === 'API_BASED';
        }
    },
    baseUrl: {
        type: String,
        required: function() {
            return this.type === 'LOCAL_URL';
        }
    },
    modelName: {
        type: String,
        required: true
    },
    isActive: {
        type: Boolean,
        default: true
    },
    maxTokens: {
        type: Number,
        required: true
    },
    temperature: {
        type: Number,
        default: 0.7,
        min: 0,
        max: 2
    }
}, {
    timestamps: true
});



module.exports = mongoose.model('LLM', llmSchema); 