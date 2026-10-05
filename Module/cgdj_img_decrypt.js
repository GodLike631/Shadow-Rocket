/**
 * 橙果短剧封面图 AES 实时透明解密脚本 (Surge WebCrypto 原生高速版)
 */
(async () => {
  const rawBody = $response.body;
  if (!rawBody || rawBody.byteLength === 0) {
    $done({});
    return;
  }

  try {
    const ciphertext = new Uint8Array(rawBody);

    // 密文非 16 字节整数倍时跳过
    if (ciphertext.length % 16 !== 0) {
      $done({});
      return;
    }

    // Key: "f5d965df75336270"
    const keyBytes = new Uint8Array([102, 53, 100, 57, 54, 53, 100, 102, 55, 53, 51, 51, 54, 50, 55, 48]);
    // IV: "97b60394abc2fbe1"
    const ivBytes = new Uint8Array([57, 55, 98, 54, 48, 51, 57, 52, 97, 98, 99, 50, 102, 98, 101, 49]);

    // 导入密钥并执行原生 AES-CBC 解密
    const cryptoKey = await crypto.subtle.importKey(
      "raw",
      keyBytes,
      { name: "AES-CBC" },
      false,
      ["decrypt"]
    );

    const decryptedBuffer = await crypto.subtle.decrypt(
      { name: "AES-CBC", iv: ivBytes },
      cryptoKey,
      ciphertext
    );

    const decHead = new Uint8Array(decryptedBuffer, 0, 2);
    let mimeType = "image/jpeg";
    if (decHead[0] === 0x89 && decHead[1] === 0x50) {
      mimeType = "image/png";
    }

    $done({
      response: {
        status: 200,
        headers: {
          "Content-Type": mimeType,
          "Access-Control-Allow-Origin": "*"
        },
        body: decryptedBuffer
      }
    });
  } catch (err) {
    console.log("[CGDJ_DECRYPT_FAIL] " + err);
    $done({});
  }
})();
