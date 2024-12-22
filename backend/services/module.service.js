const Module = require("../models/Module");

exports.createModule = async (data) => {
  return await Module.create(data);
};

exports.getAllModules = async () => {
  return await Module.find();
};

exports.getModuleById = async (id) => {
  return await Module.findById(id);
};

exports.updateModule = async (id, data) => {
  return await Module.findByIdAndUpdate(id, data, { new: true });
};

exports.deleteModule = async (id) => {
  return await Module.findByIdAndDelete(id);
};
