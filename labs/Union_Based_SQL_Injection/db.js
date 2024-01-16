const mysql = require("mysql2/promise");

async function main(connection) {
  try {
    console.log("MySQL bağlantısı başarıyla kuruldu.");

    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        flag VARCHAR(255)
      )
    `;

    await connection.execute(createTableQuery);

    console.log("Kullanıcı tablosu oluşturuldu.");

    const insertUsersQuery = `
      INSERT INTO users (username, email, flag) VALUES
      ('Admin', 'admin@appseq.com', 'cb8508e0-4ed9-4800-a77f-e9c30c26dad7'),
      ('User', 'user@appseq.com', NULL)
    `;

    await connection.execute(insertUsersQuery);

    console.log("Kullanıcılar başarıyla eklendi.");
  } catch (err) {
    console.error("MySQL bağlantısı veya sorgu hatası: " + err);
  } finally {
    if (connection) await connection.end();
  }
}

async function initializeDatabase() {
  const conn = await mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "Tr1234567",
    database: "unisql",
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
  });

  return conn;
}

async function isTableEmpty(connection) {
  const [rows] = await connection.query("SHOW TABLES LIKE 'users'");
  return rows.length === 0;
}


module.exports = { main, isTableEmpty, initializeDatabase };
