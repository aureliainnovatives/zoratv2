const User = require("../models/User");

exports.createUser = async (data) => {
  return await User.create(data);
};

exports.getAllUsers = async () => {
  return await User.find().populate("role");
};

exports.getUserById = async (id) => {
  return await User.findById(id).populate("role");
};

exports.updateUser = async (id, data) => {
  return await User.findByIdAndUpdate(id, data, { new: true });
};

exports.deleteUser = async (id) => {
  return await User.findByIdAndDelete(id);
};
