const express = require("express");
const { initializeDatabase, isTableEmpty, main } = require("./db");

const port = 3000;
const app = express();

let conn;

(async () => {
  try {
    conn = await initializeDatabase();
    const tableEmpty = await isTableEmpty(conn);

    if (tableEmpty) {
      await main(conn);
    }
  } catch (error) {
    console.error("Error initializing the database:", error);
    process.exit(1);
  }
})();

const getUser = async (username) => {
  const [rows, fields] = await conn.query(
    `SELECT username, email FROM users WHERE username='${username}'`
  );
  return rows;
};

app.get("/search", async (req, res) => {
  try {
    const { username } = req.query;
    const result = await getUser(username);

    if (result.length > 0) {
      return res.type("json").json(result);
    }
    return res.json({ status: "User not found" });
  } catch (error) {
    console.error("Error:", error);
    return res.status(500).json({ error: error });
  }
});

app.all("*", (req, res) => {
  return res.sendStatus(404);
});

app.listen(port, () => {
  console.log(`App listening on ${port}`);
});
