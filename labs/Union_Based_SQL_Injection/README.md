# Code Review Challenge

```js

const getProduct = async (product_name, callback) => {
    const query = `SELECT name, description, price from products where name='${product_name}'`;


    db.all(query, (err, rows) => {
        callback(rows);
    });
};

```
### Açıklama
- 1) Query kısmında union based sql injection zafiyeti mevcut





```js

app.post('/search', async (req, res) => {
    const { productName } = req.body;
    await getProduct(productName, async (product) => {
        if (product) return res.type('json').send(JSON.stringify(product, null, 2) + '\n');
        return res.json({ status: 'Product not found' });
    });
});
```

### Search

- 1) Kullanıcı /search e post request attığı zaman productName parametresi zafiyetli sql injection queryisine gidiyor ve kullanıcı istediği
datayı extract edebiliyor.

Burada index.js dosyası verilip kaçıncı satırda  zafiyet olduğu sorulabilir

Cevap line 10 sql injection