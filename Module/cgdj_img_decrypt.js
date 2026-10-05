/**
 * 橙果短剧封面图 AES 实时透明解密脚本 (Surge 完美对齐浏览器抓包版)
 */
(async () => {
  const rawBody = $response.body;
  if (!rawBody || rawBody.byteLength === 0) {
    $done({});
    return;
  }

  try {
    const ciphertext = new Uint8Array(rawBody);

    // 密文必须为 16 字节整数倍
    if (ciphertext.length % 16 !== 0) {
      $done({});
      return;
    }

    // 密钥与偏移量
    const keyBytes = new Uint8Array([102, 53, 100, 57, 54, 53, 100, 102, 55, 53, 51, 51, 54, 50, 55, 48]);
    const ivBytes  = new Uint8Array([57, 55, 98, 54, 48, 51, 57, 52, 97, 98, 99, 50, 102, 98, 101, 49]);

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

    // 计算解密后的实际字节大小（严格对齐抓包中的 Content-Length 与 image/jpeg）
    const decSize = decryptedBuffer.byteLength.toString();

    $done({
      response: {
        status: 200,
        headers: {
          "Content-Type": "image/jpeg",
          "Content-Length": decSize,
          "Accept-Ranges": "bytes",
          "Access-Control-Allow-Origin": "*",
          "Cache-Control": "public, max-age=31536000"
        },
        body: decryptedBuffer
      }
    });
  } catch (err) {
    console.log("[CGDJ_AES_DECRYPT_FAIL] " + err);
    $done({});
  }
})();
