const mongoose = require('mongoose');

// Define the Capability Schema
const CapabilitySchema = new mongoose.Schema(
    {
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
      file: {
        type: String,
        required: true,
        trim: true
      },
      functionName: {
        type: String,
        required: true,
        trim: true
      },
      category: {
        type: String,
        required: true,
        trim: true
      },
      parameters: {
        type: Map,
        of: mongoose.Schema.Types.Mixed, // Allows dynamic parameters (key-value pairs)
        default: {}
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


module.exports = mongoose.model('Capability', CapabilitySchema);
