const express = require("express");
const router = express.Router();
const roleController = require("../controllers/role.controller");
const { verifyToken } = require("../middleware/auth.middleware");
const { checkPermission } = require("../middleware/rbac.middleware");

// Routes for Role CRUD
router.post(
  "/",
  verifyToken,
  checkPermission("create", "Roles"),
  roleController.createRole
);

router.get(
  "/",
  verifyToken,
  checkPermission("read", "Roles"),
  roleController.getAllRoles
);

router.get(
  "/:id",
  verifyToken,
  checkPermission("read", "Roles"),
  roleController.getRoleById
);

router.put(
  "/:id",
  verifyToken,
  checkPermission("update", "Roles"),
  roleController.updateRole
);

router.delete(
  "/:id",
  verifyToken,
  checkPermission("delete", "Roles"),
  roleController.deleteRole
);

module.exports = router;
