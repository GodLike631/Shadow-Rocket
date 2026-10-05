/**
 * 影视 M3U8 通用去广告脚本（片头 + 片中全覆盖）
 * 兼容: Surge / Shadowrocket / Loon / Quantumult X
 */

let body = $response.body;

if (typeof body === "string" && body.toUpperCase().indexOf("#EXTM3U") !== -1) {
    const lines = body.split("\n");
    const outputLines = [];

    // 广告切片目录及特征关键词库（新增 C7bAbClC 与 erlgnf.com）
    const adKeywords = /(9641kb|Zse0Tpg8|seg_iif|9c08cdc|cdn-99\.cc|C7bAbClC|erlgnf\.com|\/ad\/|\/advert\/|adjump)/i;

    let headerDone = false;
    let pendingExtinf = null;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        if (!line) continue;

        let upperLine = line.toUpperCase();

        // 0. 过滤非标准混淆干扰标签
        if (upperLine.startsWith("#DISC-NOISE")) {
            continue;
        }

        // 1. 保留头部元数据（到第一个切片或密钥前）
        if (!headerDone) {
            if (upperLine.startsWith("#EXTINF") || upperLine.startsWith("#EXT-X-DISCONTINUITY")) {
                headerDone = true;
            } else {
                if (upperLine.startsWith("#EXT-X-KEY:METHOD=NONE")) continue;
                // 如果头部直接带的是广告的 EXT-X-KEY，则跳过
                if (upperLine.startsWith("#EXT-X-KEY") && adKeywords.test(line)) continue;
                outputLines.push(line);
                continue;
            }
        }

        // 2. 时长标签暂存
        if (upperLine.startsWith("#EXTINF")) {
            pendingExtinf = line;
            continue;
        }

        // 3. 切片路径过滤
        if (!line.startsWith("#")) {
            if (adKeywords.test(line)) {
                pendingExtinf = null;
            } else {
                if (pendingExtinf) {
                    outputLines.push(pendingExtinf);
                    pendingExtinf = null;
                }
                outputLines.push(line);
            }
            continue;
        }

        // 4. 断点标签过滤
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

            if (isAdSection) {
                continue;
            }

            if (outputLines.length > 0 && outputLines[outputLines.length - 1].toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) {
                continue;
            }

            outputLines.push(line);
            continue;
        }

        // 5. 解密 Key 过滤与保护
        if (upperLine.startsWith("#EXT-X-KEY")) {
            // 过滤广告专属 Key（如含特征字符或 METHOD=NONE）
            if (adKeywords.test(line) || upperLine.includes("METHOD=NONE")) {
                continue;
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
