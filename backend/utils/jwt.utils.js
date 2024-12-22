const jwt = require("jsonwebtoken");
const config = require("../config/config");

exports.generateToken = (user) => {
  return jwt.sign(
    {
      id: user._id,
      role: user.role,
    },
    config.jwtSecret,
    { expiresIn: "1h" }
  );
};

exports.verifyToken = (token) => {
  try {
    return jwt.verify(token, config.jwtSecret);
  } catch (error) {
    throw new Error("Invalid or expired token");
  }
};
