const express = require("express");
const router = express.Router();
const userController = require("../controllers/user.controller"); // Check this path

const { verifyToken } = require("../middleware/auth.middleware");
const { checkPermission } = require("../middleware/rbac.middleware");

// Verify that all controller functions exist
console.log(userController);

// User Routes
router.post(
  "/",
  verifyToken,
  checkPermission("create", "Users"),
  userController.createUser
);

router.get(
  "/",
  verifyToken,
  checkPermission("read", "Users"),
  userController.getAllUsers
);

router.get(
  "/:id",
  verifyToken,
  checkPermission("read", "Users"),
  userController.getUserById
);

router.put(
  "/:id",
  verifyToken,
  checkPermission("update", "Users"),
  userController.updateUser
);

router.delete(
  "/:id",
  verifyToken,
  checkPermission("delete", "Users"),
  userController.deleteUser
);

module.exports = router;
