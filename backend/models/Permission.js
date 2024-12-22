const mongoose = require("mongoose");

const permissionSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, unique: true }, // e.g., read, write
    description: { type: String },
  },
  { timestamps: true }
);

module.exports = mongoose.model("Permission", permissionSchema);
