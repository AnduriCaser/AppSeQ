const express = require("express");
const https = require("https");
const fs = require("fs");
const JWT = require("jsonwebtoken");
const jwkToPem = require("jwk-to-pem");
const request = require("request");
const { exec } = require("child_process");

const app = express();
app.use(express.json());

const { generate_flag } = require("./flag");

process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

const payload = { account: "Bob", role: "User" };

app.get("/", (req, res, next) => {
  JWT.sign(
    payload,
    "885ae2060fbedcfb491c5e8aafc92cab5a8057b3d4c39655acce9d4f09280a20",
    { algorithm: "HS256", audience: "http://127.0.0.1/jwt/none" },
    (err, token) => {
      const res_body = {
        jwt: token,
        endpoint: "/jwt/none",
      };
      res.status(200).json(res_body);
    }
  );
});

app.post("/jwt/none", (req, res) => {
  req.headers["content-type"] = "application/json";
  const { jwt_token } = req.body;
  let secret_key = "";
  if (jwt_token == null) {
    res
      .status(400)
      .send(
        'Send a HTTP request with a body with the format: {jwt: "< Place the JWT to test here >"}'
      );
  } else {
    const jwt_b64_dec = JWT.decode(jwt_token, { complete: true });
    if (jwt_b64_dec.header.alg == "HS256") {
      secret_key =
        "885ae2060fbedcfb491c5e8aafc92cab5a8057b3d4c39655acce9d4f09280a20";

      res.status(200).json({
        message: "This is the same JWT as before !",
      });
    } else if (jwt_b64_dec.header.alg == "none") {
      secret_key = "";
      JWT.verify(
        jwt_token,
        secret_key,
        {
          algorithms: ["none", "HS256"],
          complete: true,
          audience: "http://127.0.0.1/jwt/none",
        },
        (err, decoded_token) => {
          if (err) {
            res.status(400).json(err);
          } else {
            const success = {
              message: "Congrats!! You've solved the JWT challenge!!",
              jwt_token: decoded_token,
              flag: generate_flag(),
            };
            res.status(200).json(success);
          }
        }
      );
    }
  }
});

app.listen(80);
