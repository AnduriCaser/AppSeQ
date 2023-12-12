const express = require("express");
const app = express();
const bodyParser = require("body-parser");
const NodeCache = require("node-cache");

app.use(express.urlencoded({ extended: true }));
app.use(bodyParser.json());

const cache = new NodeCache({ stdTTL: 180, checkperiod: 120 });

app.get("/", (req, res) => {
  const xForwardedHost = req.get("x-forwarded-host");

  if (xForwardedHost) {
    cache.set("content", xForwardedHost);
  }

  if (cache.get("content")) {
    const html = `<meta property="og:image" content="https://${cache.get(
      "content"
    )}"/>`;

    res.setHeader("Cache-Control", "public");

    return res.send(html);
  }

  return res.status(400).send({
    error: true,
    message: "Image URL not found!",
  });
});

app.listen(80);
