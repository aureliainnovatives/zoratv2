const bcrypt = require("bcrypt");
const jwtUtils = require("../utils/jwt.utils");
const User = require("../models/User");
const Role = require("../models/Role");

// Signup API
exports.signup = async (req, res) => {
  try {
    const { name, email, password } = req.body;

    // Check if user exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: "Email already exists" });
    }

    const defaultRole = await Role.findOne({ name: "User" });
    if (!defaultRole) {
      return res.status(500).json({ message: "Default role not found" });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    const newUser = await User.create({
      name,
      email,
      password: hashedPassword,
      role: defaultRole._id,
    });

    res.status(201).json({ message: "User registered successfully", data: newUser });
  } catch (error) {
    res.status(500).json({ message: "Signup failed", error: error.message });
  }
};

// Login API
exports.login = async (req, res) => {
  try {
    const { email, password } = req.body;

    const user = await User.findOne({ email }).populate("role");
    if (!user) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    // Check password
    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    // Generate token
    const token = jwtUtils.generateToken(user);

    res.status(200).json({ message: "Login successful", token });
  } catch (error) {
    res.status(500).json({ message: "Login failed", error: error.message });
  }
};
