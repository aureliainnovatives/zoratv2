const Permission = require("../models/Permission");

exports.createPermission = async (data) => {
  return await Permission.create(data);
};

exports.getAllPermissions = async () => {
  return await Permission.find();
};

exports.getPermissionById = async (id) => {
  return await Permission.findById(id);
};

exports.updatePermission = async (id, data) => {
  return await Permission.findByIdAndUpdate(id, data, { new: true });
};

exports.deletePermission = async (id) => {
  return await Permission.findByIdAndDelete(id);
};
