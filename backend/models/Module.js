const mongoose = require("mongoose");

const moduleSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, unique: true }, // e.g., Users, Roles
    description: { type: String },
  },
  { timestamps: true }
);

module.exports = mongoose.model("Module", moduleSchema);
