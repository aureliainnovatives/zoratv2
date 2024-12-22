const Role = require("../models/Role");

exports.checkPermission = (requiredPermission, moduleName) => {
  return async (req, res, next) => {
    try {
      const { role } = req.user;

      // Fetch role details with nested population for permissions and modules
      const userRole = await Role.findById(role)
        .populate({
          path: "permissions.permissionId",
          select: "name description",
        })
        .populate({
          path: "permissions.moduleId",
          select: "name description",
        });

      if (!userRole) {
        return res.status(403).json({ message: "Access Denied: Role not found" });
      }

      // Check if the user has the required permission for the specified module
      const hasPermission = userRole.permissions.some(
        (p) =>
          p.permissionId.name === requiredPermission &&
          p.moduleId.name === moduleName
      );

      if (!hasPermission) {
        return res.status(403).json({ message: "Access Denied: Insufficient permissions" });
      }

      next();
    } catch (error) {
      res.status(500).json({ message: "RBAC check failed", error: error.message });
    }
  };
};
