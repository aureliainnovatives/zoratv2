const mongoose = require("mongoose");
const bcrypt = require("bcrypt");
const dotenv = require("dotenv");

// Load config
dotenv.config({ path: "../.env" });
const config = require("../config/config");

// Load models
const Role = require("../models/Role");
const Permission = require("../models/Permission");
const Module = require("../models/Module");
const User = require("../models/User");

const seedData = async () => {
  try {
    // Connect to MongoDB
    await mongoose.connect(config.mongoURI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log("Connected to MongoDB");

    // Clear existing data
    await Role.deleteMany({});
    await Permission.deleteMany({});
    await Module.deleteMany({});
    await User.deleteMany({});
    console.log("Cleared existing collections");

    // Seed Permissions
    const permissions = [
      { name: "create", description: "Permission to create resources" },
      { name: "read", description: "Permission to read resources" },
      { name: "update", description: "Permission to update resources" },
      { name: "delete", description: "Permission to delete resources" },
    ];
    const createdPermissions = await Permission.insertMany(permissions);
    console.log("Permissions seeded");

    // Seed Modules (Add "Modules" entry and additional requested entries)
    const modules = [
      { name: "Modules", description: "Module Management" }, // Added
      { name: "Users", description: "User Management Module" },
      { name: "Roles", description: "Role Management Module" },
      { name: "Permissions", description: "Permission Management Module" },
      { name: "Agent", description: "Agent Management Module" },
      { name: "Workflow", description: "Workflow Management Module" },
      { name: "Integrations", description: "Integration Management Module" },
      { name: "Settings", description: "System Settings Module" },
      { name: "Dashboard", description: "Dashboard and Metrics Module" }, // Additional
      { name: "Notifications", description: "Notifications Management Module" }, // Additional
    ];
    const createdModules = await Module.insertMany(modules);
    console.log("Modules seeded");

    // Map permissions to modules for Super Admin
    const superAdminPermissions = [];
    createdModules.forEach((module) => {
      createdPermissions.forEach((permission) => {
        superAdminPermissions.push({
          permissionId: permission._id,
          moduleId: module._id,
        });
      });
    });

    // Seed Roles with Scoped Permissions
    const roles = [
      {
        name: "Super Admin",
        description: "Has all permissions",
        permissions: superAdminPermissions, // All permissions for all modules
      },
      {
        name: "Admin",
        description: "Manages users and roles",
        permissions: [
          {
            permissionId: createdPermissions.find((p) => p.name === "read")._id,
            moduleId: createdModules.find((m) => m.name === "Users")._id,
          },
          {
            permissionId: createdPermissions.find((p) => p.name === "read")._id,
            moduleId: createdModules.find((m) => m.name === "Roles")._id,
          },
        ],
      },
      {
        name: "User",
        description: "Basic access to system",
        permissions: [
          {
            permissionId: createdPermissions.find((p) => p.name === "read")._id,
            moduleId: createdModules.find((m) => m.name === "Users")._id,
          },
        ],
      },
    ];

    const createdRoles = await Role.insertMany(roles);
    console.log("Roles with permissions seeded");

    // Seed Super Admin User
    const hashedPassword = await bcrypt.hash("123", 10);
    const superAdminRole = createdRoles.find((role) => role.name === "Super Admin");

    await User.create({
      name: "Super Admin",
      email: "mayur.patil@aurelia.tech",
      password: hashedPassword,
      role: superAdminRole._id, // Correct role reference
    });

    console.log("Super Admin user seeded");

    // Exit process
    process.exit();
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
};

seedData();
