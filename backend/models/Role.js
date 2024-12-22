const mongoose = require("mongoose");

const roleSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, unique: true }, // e.g., Admin, User
    description: { type: String },
    permissions: [
      {
        permissionId: { type: mongoose.Schema.Types.ObjectId, ref: "Permission" },
        moduleId: { type: mongoose.Schema.Types.ObjectId, ref: "Module" },
      },
    ],
  },
  { timestamps: true }
);

module.exports = mongoose.model("Role", roleSchema);
