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
const LLM = require("../models/AIModel"); // Include the LLM model

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


      // Seed LLM Models
      const llmModels = [
        {
          name: "GPT-3.5 Turbo",
          description: "OpenAI's GPT-3.5 Turbo model",
          type: "API_BASED",
          provider: "OPENAI",
          apiKey: "your-openai-api-key",
          baseUrl: "https://api.openai.com/v1",
          modelName: "gpt-3.5-turbo",
          isActive: true,
          maxTokens: 4096,
          temperature: 0.7,
        },
        {
          name: "GPT-4",
          description: "OpenAI's GPT-4 model",
          type: "API_BASED",
          provider: "OPENAI",
          apiKey: "your-openai-api-key",
          baseUrl: "https://api.openai.com/v1",
          modelName: "gpt-4",
          isActive: true,
          maxTokens: 8192,
          temperature: 0.7,
        },
        {
          name: "GPT-40",
          description: "OpenAI's hypothetical GPT-40 model",
          type: "API_BASED",
          provider: "OPENAI",
          apiKey: "your-openai-api-key",
          baseUrl: "https://api.openai.com/v1",
          modelName: "gpt-40",
          isActive: true,
          maxTokens: 16000,
          temperature: 0.9,
        },
        {
          name: "Google Gemini",
          description: "Google's Gemini model for advanced tasks",
          type: "API_BASED",
          provider: "GOOGLE",
          apiKey: "your-google-api-key",
          baseUrl: "https://api.google.com/gemini",
          modelName: "gemini-v1",
          isActive: true,
          maxTokens: 4096,
          temperature: 0.8,
        },
        {
          name: "Claude Sonnet",
          description: "Anthropic Claude Sonnet model (Local)",
          type: "LOCAL_URL",
          provider: "LOCAL",
          baseUrl: "http://localhost:5001",
          modelName: "claude-sonnet",
          isActive: true,
          maxTokens: 2048,
          temperature: 0.6,
        },
        {
          name: "Claude Opus",
          description: "Anthropic Claude Opus model (Local)",
          type: "LOCAL_URL",
          provider: "LOCAL",
          baseUrl: "http://localhost:5002",
          modelName: "claude-opus",
          isActive: true,
          maxTokens: 2048,
          temperature: 0.6,
        },
        {
          name: "Claude Haiku",
          description: "Anthropic Claude Haiku model (Local)",
          type: "LOCAL_URL",
          provider: "LOCAL",
          baseUrl: "http://localhost:5003",
          modelName: "claude-haiku",
          isActive: true,
          maxTokens: 2048,
          temperature: 0.6,
        },
        {
          name: "Llama 3.3",
          description: "Meta's Llama 3.3 model (Local)",
          type: "LOCAL_URL",
          provider: "LOCAL",
          baseUrl: "http://localhost:5004",
          modelName: "llama-3.3",
          isActive: true,
          maxTokens: 4096,
          temperature: 0.7,
        },
        {
          name: "Qwen",
          description: "Alibaba's Qwen model (Local)",
          type: "LOCAL_URL",
          provider: "LOCAL",
          baseUrl: "http://localhost:5005",
          modelName: "qwen-v1",
          isActive: true,
          maxTokens: 4096,
          temperature: 0.7,
        },
      ];
      await LLM.insertMany(llmModels);
      console.log("LLM models seeded");

    // Exit process
    process.exit();
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
};

seedData();
