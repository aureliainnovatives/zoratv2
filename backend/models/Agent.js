
const mongoose = require('mongoose');

// Define the Agent Schema
const AgentSchema = new mongoose.Schema(
    {
      name: {
        type: String,
        required: true,
        trim: true
      },
      description: {
        type: String,
        required: true
      },
      capabilities: [
        {
          type: mongoose.Schema.Types.ObjectId,
          ref: 'Capability', // Reference to the Capability model
          required: true
        }
      ],
      llm: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'LLM', // Reference to the LLM model
        required: true
      },
      inputFormat: {
        type: String,
        enum: ['text', 'JSON', 'file'],
        default: 'text'
      },
      outputFormat: {
        type: String,
        enum: ['text', 'JSON', 'file'],
        default: 'JSON'
      },
      createdBy: {
        type: String,
        required: true
      },
      visibility: {
        type: String,
        enum: ['private', 'shared'],
        default: 'private'
      },
      userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User', // Reference to the User model
        required: true
      },
      createdAt: {
        type: Date,
        default: Date.now
      },
      updatedAt: {
        type: Date,
        default: Date.now
      }
    },
    {
      timestamps: true // Automatically add createdAt and updatedAt fields
    }
  );
  
// Export the Agent model
module.exports = mongoose.model('Agent', AgentSchema);
