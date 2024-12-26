require("dotenv").config();

const MODE = process.env.MODE || "development";

const configMap = {
    development: require("./development"),
    production: require("./production")
};

const config = configMap[MODE];

if (!config) {
    throw new Error(`Invalid MODE: ${MODE}. Available modes: development, production`);
}

console.log(`Loaded configuration for MODE: ${MODE}`);

module.exports = config;
