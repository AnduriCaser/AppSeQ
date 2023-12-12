const { v4: uuidv4 } = require("uuid");

const generate_flag = () => {
  const uuid = uuidv4();
  return uuid;
};

module.exports = {
  generate_flag,
};
