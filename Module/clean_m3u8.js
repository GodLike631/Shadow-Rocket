/**
 * 影视 M3U8 全段通用去广告脚本（支持 TS / JPG / 混淆标签 / 片头片中）
 */

let body = $response.body;

if (typeof body === "string" && body.toUpperCase().indexOf("#EXTM3U") !== -1) {
    const lines = body.split("\n");
    const outputLines = [];

    // 广告切片特征库（新增 seg_iif、9c08cdc）
    const adKeywords = /(9641kb|Zse0Tpg8|seg_iif|9c08cdc|cdn-99\.cc|\/ad\/|\/advert\/|adjump)/i;

    let headerDone = false;
    let pendingExtinf = null;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        if (!line) continue;

        let upperLine = line.toUpperCase();

        // 过滤非标准混淆噪音标签
        if (upperLine.startsWith("#DISC-NOISE")) {
            continue;
        }

        // 1. 保留标准头部元数据
        if (!headerDone) {
            if (upperLine.startsWith("#EXTINF") || upperLine.startsWith("#EXT-X-DISCONTINUITY")) {
                headerDone = true;
            } else {
                if (upperLine.startsWith("#EXT-X-KEY:METHOD=NONE")) continue;
                outputLines.push(line);
                continue;
            }
        }

        // 2. 遇到时长声明，暂存待判
        if (upperLine.startsWith("#EXTINF")) {
            pendingExtinf = line;
            continue;
        }

        // 3. 遇到切片路径（无论是 .ts 还是伪装的 .jpg）
        if (!line.startsWith("#")) {
            if (adKeywords.test(line)) {
                // 命中广告切片，废弃当前行及对应的 EXTINF
                pendingExtinf = null;
            } else {
                // 正片切片行，写入
                if (pendingExtinf) {
                    outputLines.push(pendingExtinf);
                    pendingExtinf = null;
                }
                outputLines.push(line);
            }
            continue;
        }

        // 4. 断点标签处理
        if (upperLine.startsWith("#EXT-X-DISCONTINUITY")) {
            let isAdSection = false;
            for (let j = i + 1; j < Math.min(i + 6, lines.length); j++) {
                let testLine = lines[j].trim();
                if (testLine.toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) break;
                if (adKeywords.test(testLine)) {
                    isAdSection = true;
                    break;
                }
            }

            // 广告段落周围的断点全部剔除
            if (isAdSection) {
                continue;
            }

            // 防止连续无意义断点残留
            if (outputLines.length > 0 && outputLines[outputLines.length - 1].toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) {
                continue;
            }

            outputLines.push(line);
            continue;
        }

        // 5. 解密 Key 标签（严密保护正片 AES-128 / SAMPLE-AES 密钥）
        if (upperLine.startsWith("#EXT-X-KEY")) {
            if (upperLine.includes("METHOD=NONE")) {
                let nextAd = false;
                for (let k = i + 1; k < Math.min(i + 4, lines.length); k++) {
                    if (adKeywords.test(lines[k].trim())) {
                        nextAd = true;
                        break;
                    }
                }
                if (nextAd) continue;
            }
            outputLines.push(line);
            continue;
        }

        // 6. 其他标签原样保留
        outputLines.push(line);
    }

    body = outputLines.join("\n");
}

$done({
    response: { body: body },
    body: body
});
