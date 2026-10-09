/**
 * 影视 M3U8 通用去广告脚本（切片颗粒度级清洗版）
 * 兼容: Surge / Loon / Quantumult X
 * Telegram群组：https://t.me/tvshare23
 */

let body = $response.body;

if (typeof body === "string" && body.indexOf("#EXTM3U") !== -1) {
    const rawLines = body.replace(/\r/g, "").split("\n");
    const outputLines = [];

    // 精准广告特征词库（全量保留既有特征，安全追加本次哈希及相对路径动态广告通配）
    const adKeywords = /(9641kb|10141kb|1000kb|30EjJFTT|W7fqTmbJ|JKyp1S2D|5568049a638c79f9|ec5db3bbf268dd34|7e14ee319bf8017d|ac080df0b161b6fb|ea6bb8a311db9dd0|1f1d60431202f328|39803bb0fa0ec24b|787de3b9178c4058|0916de7dab851cd8|65e7a9371db1b651|Zse0Tpg8|seg_iif|9c08cdc|a6b9d4136946ad41|a0fd38|\/stream\/|\/mov\/AD\/|8jlf67z19|C7bAbClC|erlgnf\.com|adjump|^\/\d{8}\/[a-f0-9]{16}\/seg_)/i;

    let pendingExtinf = null;
    let pendingDiscontinuity = false;

    for (let i = 0; i < rawLines.length; i++) {
        let line = rawLines[i].trim();
        if (!line) continue;

        let upperLine = line.toUpperCase();

        // 1. 过滤混淆干扰标签
        if (upperLine.startsWith("#DISC-NOISE")) {
            continue;
        }

        // 2. 彻底剔除 METHOD=NONE
        if (upperLine.startsWith("#EXT-X-KEY") && upperLine.includes("METHOD=NONE")) {
            continue;
        }

        // 3. 广告专属 Key 剔除
        if (upperLine.startsWith("#EXT-X-KEY") && adKeywords.test(line)) {
            continue;
        }

        // 4. 暂存断点标签
        if (upperLine.startsWith("#EXT-X-DISCONTINUITY")) {
            pendingDiscontinuity = true;
            continue;
        }

        // 5. 正片真实解密 Key：保证断点在 Key 之前输出
        if (upperLine.startsWith("#EXT-X-KEY")) {
            if (pendingDiscontinuity) {
                if (outputLines.length > 0 && !outputLines[outputLines.length - 1].toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) {
                    outputLines.push("#EXT-X-DISCONTINUITY");
                }
                pendingDiscontinuity = false;
            }
            outputLines.push(line);
            continue;
        }

        // 6. 暂存切片时长标签
        if (upperLine.startsWith("#EXTINF")) {
            pendingExtinf = line;
            continue;
        }

        // 7. 处理切片 URL
        if (!line.startsWith("#")) {
            if (adKeywords.test(line)) {
                // 命中广告切片：清除时长标签与紧邻断点
                pendingExtinf = null;
                pendingDiscontinuity = false;
            } else {
                // 正片切片：按需输出断点、EXTINF 和切片路径
                if (pendingDiscontinuity) {
                    if (outputLines.length > 0 && !outputLines[outputLines.length - 1].toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) {
                        outputLines.push("#EXT-X-DISCONTINUITY");
                    }
                    pendingDiscontinuity = false;
                }
                if (pendingExtinf) {
                    outputLines.push(pendingExtinf);
                    pendingExtinf = null;
                }
                outputLines.push(line);
            }
            continue;
        }

        // 8. 其它头部及尾部元数据原样保留
        outputLines.push(line);
    }

    body = outputLines.join("\n");
}

$done({ body: body });
