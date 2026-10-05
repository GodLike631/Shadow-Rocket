/**
 * 影视 M3U8 通用清洗脚本（片头 + 片中）
 */

let body = $response.body;

if (typeof body === "string" && body.toUpperCase().indexOf("#EXTM3U") !== -1) {
    const lines = body.split("\n");
    const outputLines = [];

    // 广告特征正则：加了 i 修饰符忽略大小写，涵盖 9641kb、Zse0Tpg8 等
    const adKeywords = /(9641kb|Zse0Tpg8|cdn-99\.cc|\/ad\/|\/advert\/|adjump)/i;

    let headerDone = false;
    let pendingExtinf = null;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        if (!line) continue;

        let upperLine = line.toUpperCase();

        // 1. 保留头部元数据
        if (!headerDone) {
            if (upperLine.startsWith("#EXTINF") || upperLine.startsWith("#EXT-X-DISCONTINUITY")) {
                headerDone = true;
            } else {
                if (upperLine.startsWith("#EXT-X-KEY:METHOD=NONE")) continue;
                outputLines.push(line);
                continue;
            }
        }

        // 2. 暂存时长标签
        if (upperLine.startsWith("#EXTINF")) {
            pendingExtinf = line;
            continue;
        }

        // 3. 切片路径判定
        if (!line.startsWith("#")) {
            if (adKeywords.test(line)) {
                // 广告切片，直接抛弃
                pendingExtinf = null;
            } else {
                // 正片切片
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

            if (isAdSection) {
                continue;
            }

            if (outputLines.length > 0 && outputLines[outputLines.length - 1].toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) {
                continue;
            }

            outputLines.push(line);
            continue;
        }

        // 5. 解密 Key 标签放行
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

        // 6. 其他标签保留
        outputLines.push(line);
    }

    body = outputLines.join("\n");
}

$done({
    response: { body: body },
    body: body
});
