/**
 * 橙果短剧封面图 AES 实时透明解密脚本 (iOS Surge 终极加固版)
 */

const S_BOX = new Uint8Array([
  0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
  0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
  0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
  0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
  0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
  0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
  0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
  0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
  0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
  0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
  0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
  0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
  0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
  0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
  0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
  0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
]);

const INV_S_BOX = new Uint8Array(256);
for (let i = 0; i < 256; i++) {
  INV_S_BOX[S_BOX[i]] = i;
}

const RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36];

function mul(a, b) {
  let res = 0;
  while (b) {
    if (b & 1) res ^= a;
    a = (a & 0x80) ? ((a << 1) ^ 0x1b) & 0xff : (a << 1);
    b >>= 1;
  }
  return res;
}

function keyExpansion(keyBytes) {
  const w = [];
  for (let i = 0; i < 4; i++) {
    w.push([keyBytes[4 * i], keyBytes[4 * i + 1], keyBytes[4 * i + 2], keyBytes[4 * i + 3]]);
  }
  for (let i = 4; i < 44; i++) {
    let temp = [w[i - 1][0], w[i - 1][1], w[i - 1][2], w[i - 1][3]];
    if (i % 4 === 0) {
      temp = [temp[1], temp[2], temp[3], temp[0]];
      temp = [S_BOX[temp[0]] ^ RCON[i / 4], S_BOX[temp[1]], S_BOX[temp[2]], S_BOX[temp[3]]];
    }
    w.push([
      w[i - 4][0] ^ temp[0],
      w[i - 4][1] ^ temp[1],
      w[i - 4][2] ^ temp[2],
      w[i - 4][3] ^ temp[3]
    ]);
  }
  return w;
}

// 预先分配单块缓冲区，彻底避免内存频繁回收引发闪退
const s_matrix = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]];
const block_out = new Uint8Array(16);

function decryptBlock(inBytes, offset, w) {
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      s_matrix[r][c] = inBytes[offset + r + 4 * c] ^ w[40 + c][r];
    }
  }

  for (let round = 9; round > 0; round--) {
    let s1_0 = s_matrix[1][0], s1_1 = s_matrix[1][1], s1_2 = s_matrix[1][2], s1_3 = s_matrix[1][3];
    s_matrix[1][0] = s1_3; s_matrix[1][1] = s1_0; s_matrix[1][2] = s1_1; s_matrix[1][3] = s1_2;

    let s2_0 = s_matrix[2][0], s2_1 = s_matrix[2][1], s2_2 = s_matrix[2][2], s2_3 = s_matrix[2][3];
    s_matrix[2][0] = s2_2; s_matrix[2][1] = s2_3; s_matrix[2][2] = s2_0; s_matrix[2][3] = s2_1;

    let s3_0 = s_matrix[3][0], s3_1 = s_matrix[3][1], s3_2 = s_matrix[3][2], s3_3 = s_matrix[3][3];
    s_matrix[3][0] = s3_1; s_matrix[3][1] = s3_2; s_matrix[3][2] = s3_3; s_matrix[3][3] = s3_0;

    for (let r = 0; r < 4; r++) {
      for (let c = 0; c < 4; c++) {
        s_matrix[r][c] = INV_S_BOX[s_matrix[r][c]] ^ w[round * 4 + c][r];
      }
    }

    for (let c = 0; c < 4; c++) {
      let u0 = s_matrix[0][c], u1 = s_matrix[1][c], u2 = s_matrix[2][c], u3 = s_matrix[3][c];
      s_matrix[0][c] = mul(u0, 0x0e) ^ mul(u1, 0x0b) ^ mul(u2, 0x0d) ^ mul(u3, 0x09);
      s_matrix[1][c] = mul(u0, 0x09) ^ mul(u1, 0x0e) ^ mul(u2, 0x0b) ^ mul(u3, 0x0d);
      s_matrix[2][c] = mul(u0, 0x0d) ^ mul(u1, 0x09) ^ mul(u2, 0x0e) ^ mul(u3, 0x0b);
      s_matrix[3][c] = mul(u0, 0x0b) ^ mul(u1, 0x0d) ^ mul(u2, 0x09) ^ mul(u3, 0x0e);
    }
  }

  let s1_0 = s_matrix[1][0], s1_1 = s_matrix[1][1], s1_2 = s_matrix[1][2], s1_3 = s_matrix[1][3];
  s_matrix[1][0] = s1_3; s_matrix[1][1] = s1_0; s_matrix[1][2] = s1_1; s_matrix[1][3] = s1_2;

  let s2_0 = s_matrix[2][0], s2_1 = s_matrix[2][1], s2_2 = s_matrix[2][2], s2_3 = s_matrix[2][3];
  s_matrix[2][0] = s2_2; s_matrix[2][1] = s2_3; s_matrix[2][2] = s2_0; s_matrix[2][3] = s2_1;

  let s3_0 = s_matrix[3][0], s3_1 = s_matrix[3][1], s3_2 = s_matrix[3][2], s3_3 = s_matrix[3][3];
  s_matrix[3][0] = s3_1; s_matrix[3][1] = s3_2; s_matrix[3][2] = s3_3; s_matrix[3][3] = s3_0;

  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      block_out[r + 4 * c] = INV_S_BOX[s_matrix[r][c]] ^ w[c][r];
    }
  }
  return block_out;
}

(function main() {
  const rawBody = $response.body;
  if (!rawBody || rawBody.byteLength === 0) {
    $done({});
    return;
  }

  try {
    const ciphertext = new Uint8Array(rawBody);
    const len = ciphertext.length;

    if (len % 16 !== 0) {
      $done({});
      return;
    }

    const keyBytes = [102, 53, 100, 57, 54, 53, 100, 102, 55, 53, 51, 51, 54, 50, 55, 48];
    const ivBytes  = [57, 55, 98, 54, 48, 51, 57, 52, 97, 98, 99, 50, 102, 98, 101, 49];

    const w = keyExpansion(keyBytes);
    const out = new Uint8Array(len);
    let prev = ivBytes;

    for (let i = 0; i < len; i += 16) {
      const dec = decryptBlock(ciphertext, i, w);
      for (let j = 0; j < 16; j++) {
        out[i + j] = dec[j] ^ prev[j];
      }
      prev = ciphertext.subarray(i, i + 16);
    }

    const pad = out[len - 1];
    const validLen = (pad >= 1 && pad <= 16) ? (len - pad) : len;
    const finalBuffer = out.buffer.slice(0, validLen);

    $done({
      response: {
        status: 200,
        headers: {
          "Content-Type": "image/jpeg",
          "Access-Control-Allow-Origin": "*"
        },
        body: finalBuffer
      }
    });
  } catch (err) {
    console.log("[CGDJ_AES_ERR] " + err);
    $done({});
  }
})();
