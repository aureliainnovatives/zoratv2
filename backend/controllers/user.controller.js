const userService = require("../services/user.service");

// Create a User
exports.createUser = async (req, res) => {
  try {
    const { name, email, password, role } = req.body;
    const user = await userService.createUser({ name, email, password, role });
    res.status(201).json({ message: "User created successfully", data: user });
  } catch (error) {
    res.status(400).json({ message: "Error creating user", error: error.message });
  }
};

// Get All Users
exports.getAllUsers = async (req, res) => {
  try {
    const users = await userService.getAllUsers();
    res.status(200).json({ data: users });
  } catch (error) {
    res.status(500).json({ message: "Error fetching users", error: error.message });
  }
};

// Get User By ID
exports.getUserById = async (req, res) => {
  try {
    const user = await userService.getUserById(req.params.id);
    if (!user) return res.status(404).json({ message: "User not found" });
    res.status(200).json({ data: user });
  } catch (error) {
    res.status(500).json({ message: "Error fetching user", error: error.message });
  }
};

// Update User
exports.updateUser = async (req, res) => {
  try {
    const updatedUser = await userService.updateUser(req.params.id, req.body);
    if (!updatedUser) return res.status(404).json({ message: "User not found" });
    res.status(200).json({ message: "User updated successfully", data: updatedUser });
  } catch (error) {
    res.status(400).json({ message: "Error updating user", error: error.message });
  }
};

// Delete User
exports.deleteUser = async (req, res) => {
  try {
    const deletedUser = await userService.deleteUser(req.params.id);
    if (!deletedUser) return res.status(404).json({ message: "User not found" });
    res.status(200).json({ message: "User deleted successfully" });
  } catch (error) {
    res.status(500).json({ message: "Error deleting user", error: error.message });
  }
};
