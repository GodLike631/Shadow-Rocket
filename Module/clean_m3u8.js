/**
 * 影视 M3U8 通用去广告脚本（切片颗粒度级清洗版）
 * 兼容: Surge / Loon / Quantumult X
 * Telegram群组：https://t.me/tvshare23
 */

let body = $response.body;

if (typeof body === "string" && body.indexOf("#EXTM3U") !== -1) {
    const rawLines = body.replace(/\r/g, "").split("\n");
    const outputLines = [];

    // 广告特征关键词库（已追加 5568049a638c79f9、ec5db3bbf268dd34 等特征）
    const adKeywords = /(9641kb|10141kb|1000kb|30EjJFTT|W7fqTmbJ|5568049a638c79f9|ec5db3bbf268dd34|Zse0Tpg8|seg_iif|seg_|9c08cdc|a6b9d4136946ad41|a0fd38|\/stream\/|cdn-99\.cc|C7bAbClC|erlgnf\.com|\/ad\/|\/advert\/|adjump)/i;

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

        // 5. 暂存切片时长标签
        if (upperLine.startsWith("#EXTINF")) {
            pendingExtinf = line;
            continue;
        }

        // 6. 处理切片 URL
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

        // 7. 正片 AES-128 Key 及其它元数据原样保留
        outputLines.push(line);
    }

    body = outputLines.join("\n");
}

$done({ body: body });
