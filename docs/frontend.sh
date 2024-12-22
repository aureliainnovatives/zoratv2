#!/bin/bash

# Script to create Angular project structure for RBAC front-end setup

# 1. Setup Angular Project
ng new zorat-frontend --routing --style=css
cd zorat-frontend

# 2. Install TailwindCSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init

# Add Tailwind to styles.css
echo "@tailwind base; @tailwind components; @tailwind utilities;" >> src/styles.css

# 3. Create Core Components
ng generate component auth/login
ng generate component auth/signup
ng generate component dashboard
ng generate component agents/agents-list
ng generate component agents/agents-form
ng generate component capabilities/capabilities-list
ng generate component capabilities/capabilities-form
ng generate component models/models-list
ng generate component models/models-form
ng generate component users/users-list
ng generate component users/users-form

# 4. Generate Shared Services and Modules
ng generate service services/auth
ng generate service services/agents
ng generate service services/capabilities
ng generate service services/models
ng generate service services/users
ng generate module shared

# 5. Folder Structure Cleanup
mkdir src/assets/themes
touch src/assets/themes/light.css
touch src/assets/themes/dark.css

# 6. Add Theme Switching Service
ng generate service services/theme

# 7. Summary
echo "Angular front-end setup completed with necessary components, services, and themes!"
