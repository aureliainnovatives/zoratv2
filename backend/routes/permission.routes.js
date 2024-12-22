const express = require("express");
const router = express.Router();
const permissionController = require("../controllers/permission.controller");

router.post("/", permissionController.createPermission);
router.get("/", permissionController.getPermissions);
router.get("/:id", permissionController.getPermissionById);
router.put("/:id", permissionController.updatePermission);
router.delete("/:id", permissionController.deletePermission);

module.exports = router;
