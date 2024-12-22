#!/bin/bash

# Script to create project structure for Agent Platform

echo "Creating folder structure..."

# Create directories
mkdir -p config
mkdir -p models
mkdir -p routes
mkdir -p controllers

# Create files
touch config/db.config.js
touch models/User.js
touch models/Role.js
touch models/Agent.js
touch models/Capability.js
touch models/AIModel.js

touch routes/user.routes.js
touch routes/role.routes.js
touch routes/agent.routes.js
touch routes/capability.routes.js
touch routes/aimodel.routes.js

touch controllers/user.controller.js
touch controllers/role.controller.js
touch controllers/agent.controller.js
touch controllers/capability.controller.js
touch controllers/aimodel.controller.js

touch .env
touch server.js
touch package.json

echo "Files and folders created successfully."

# Set executable permissions for the script
chmod +x create_project_structure.sh

echo "Done."
