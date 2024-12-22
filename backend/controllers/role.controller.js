const roleService = require("../services/role.service");

// Create a new Role
exports.createRole = async (req, res) => {
  try {
    const { name, description } = req.body;

    // Input validation
    if (!name) {
      return res.status(400).json({ message: "Role name is required." });
    }

    const role = await roleService.createRole({ name, description });
    res.status(201).json({ message: "Role created successfully", data: role });
  } catch (error) {
    res.status(500).json({ message: "Error creating role", error: error.message });
  }
};

// Get all Roles
exports.getAllRoles = async (req, res) => {
  try {
    const roles = await roleService.getAllRoles();
    res.status(200).json({ data: roles });
  } catch (error) {
    res.status(500).json({ message: "Error fetching roles", error: error.message });
  }
};

// Get Role by ID
exports.getRoleById = async (req, res) => {
  try {
    const role = await roleService.getRoleById(req.params.id);
    if (!role) {
      return res.status(404).json({ message: "Role not found" });
    }
    res.status(200).json({ data: role });
  } catch (error) {
    res.status(500).json({ message: "Error fetching role", error: error.message });
  }
};

// Update Role by ID
exports.updateRole = async (req, res) => {
  try {
    const { name, description } = req.body;

    // Input validation
    if (!name) {
      return res.status(400).json({ message: "Role name is required." });
    }

    const updatedRole = await roleService.updateRole(req.params.id, { name, description });
    if (!updatedRole) {
      return res.status(404).json({ message: "Role not found" });
    }
    res.status(200).json({ message: "Role updated successfully", data: updatedRole });
  } catch (error) {
    res.status(500).json({ message: "Error updating role", error: error.message });
  }
};

// Delete Role by ID
exports.deleteRole = async (req, res) => {
  try {
    const deletedRole = await roleService.deleteRole(req.params.id);
    if (!deletedRole) {
      return res.status(404).json({ message: "Role not found" });
    }
    res.status(200).json({ message: "Role deleted successfully" });
  } catch (error) {
    res.status(500).json({ message: "Error deleting role", error: error.message });
  }
};
