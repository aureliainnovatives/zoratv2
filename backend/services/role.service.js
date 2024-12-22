const Role = require("../models/Role");

// Create a new role
exports.createRole = async (data) => {
  return await Role.create(data);
};

// Get all roles
exports.getAllRoles = async () => {
  return await Role.find().populate("permissions.permissionId").populate("permissions.moduleId");
};

// Get role by ID
exports.getRoleById = async (id) => {
  return await Role.findById(id).populate("permissions.permissionId").populate("permissions.moduleId");
};

// Update role by ID
exports.updateRole = async (id, data) => {
  return await Role.findByIdAndUpdate(id, data, { new: true });
};

// Delete role by ID
exports.deleteRole = async (id) => {
  return await Role.findByIdAndDelete(id);
};
