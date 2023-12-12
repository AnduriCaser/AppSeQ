const express = require("express");
const sqlite3 = require("sqlite3").verbose();
const port = 3000;
const app = express();


var db = new sqlite3.Database(process.env.DB_FILE);

const getProduct = async (product_name, callback) => {
    const query = `SELECT name, description, price from products where name='${product_name}'`;


    db.all(query, (err, rows) => {
        callback(rows);
    });
};



app.post('/search', async (req, res) => {
    const { productName } = req.body;
    await getProduct(productName, async (product) => {
        if (product) return res.type('json').send(JSON.stringify(product, null, 2) + '\n');
        return res.json({ status: 'Product not found' });
    });
});




app.all('*', (req, res) => {
    return res.sendStatus(404);
});


app.listen(port, () => {
    console.log(`App listening on ${port}`);
})
