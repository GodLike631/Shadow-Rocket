/**
 * 花街影院图片解密脚本 (Surge 专用无依赖版)
 * 密钥: OzoTeoS7D>6Y^@z39JmD
 */
(function () {
    const key = [79, 122, 111, 84, 101, 111, 83, 55, 68, 62, 54, 89, 94, 64, 122, 51, 57, 74, 109, 68];
    const keyLen = key.length;

    let bodyBytes = $response.body;
    if (!bodyBytes || bodyBytes.length === 0) {
        $done({});
        return;
    }

    // 纯JS实现的 Base64 解码表，不依赖浏览器的 atob/TextDecoder
    const b64Chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    const b64Lookup = new Uint8Array(256);
    for (let i = 0; i < b64Chars.length; i++) {
        b64Lookup[b64Chars.charCodeAt(i)] = i;
    }

    function decodeBase64Uint8(u8Arr) {
        let validLen = 0;
        let buf = new Uint8Array(u8Arr.length);
        for (let i = 0; i < u8Arr.length; i++) {
            let c = u8Arr[i];
            // 过滤换行符、回车符和空格
            if (c > 32 && c !== 61) { // 61 是 '='
                buf[validLen++] = c;
            }
        }

        let outLen = (validLen * 3) >> 2;
        let out = new Uint8Array(outLen);
        let cur = 0;

        for (let i = 0; i < validLen; i += 4) {
            let a = b64Lookup[buf[i]];
            let b = b64Lookup[buf[i + 1]];
            let c = b64Lookup[buf[i + 2]];
            let d = b64Lookup[buf[i + 3]];

            out[cur++] = (a << 2) | (b >> 4);
            if (i + 2 < validLen && buf[i + 2] !== 61) {
                out[cur++] = ((b & 15) << 4) | (c >> 2);
            }
            if (i + 3 < validLen && buf[i + 3] !== 61) {
                out[cur++] = ((c & 3) << 6) | d;
            }
        }
        return out.subarray(0, cur);
    }

    try {
        // 1. 直接对收到的二进制 Base64 数据进行就地解码
        let binary = decodeBase64Uint8(bodyBytes);
        let len = binary.length;

        // 2. 异或解密
        for (let i = 0; i < len; i++) {
            binary[i] = binary[i] ^ key[i % keyLen];
        }

        // 3. 校验魔数以确定真实 MIME
        let mime = "image/jpeg";
        if (binary[0] === 0x89 && binary[1] === 0x50) {
            mime = "image/png";
        } else if (binary[0] === 0x52 && binary[1] === 0x49) {
            mime = "image/webp";
        }

        // 4. 重建 Headers 并剔除导致截断/错乱的字段
        let headers = Object.assign({}, $response.headers);
        headers["Content-Type"] = mime;
        headers["Content-Length"] = String(len);
        headers["Cache-Control"] = "public, max-age=604800";
        delete headers["Content-Encoding"];
        delete headers["content-encoding"];

        // 5. Surge 标准返回：body 必须是 Uint8Array
        $done({
            status: 200,
            headers: headers,
            body: binary
        });
    } catch (err) {
        $done({});
    }
})();