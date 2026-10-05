/**
 * 影视 M3U8 通用去广告脚本（彻底清洗版）
 * 兼容: Surge / Shadowrocket / Loon / Quantumult X
 * 支持: 片头 + 片中插播全量清洗、\r\n 换行符消除、METHOD=NONE 强制擦除
 */

let body = $response.body;

if (typeof body === "string" && body.toUpperCase().indexOf("#EXTM3U") !== -1) {
    // 1. 统一归一化换行符，剔除 \r 干扰
    const lines = body.replace(/\r/g, "").split("\n");
    const outputLines = [];

    // 广告切片目录及特征关键词库
    const adKeywords = /(9641kb|Zse0Tpg8|seg_iif|9c08cdc|cdn-99\.cc|C7bAbClC|erlgnf\.com|\/ad\/|\/advert\/|adjump)/i;

    let headerDone = false;
    let pendingExtinf = null;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        if (!line) continue;

        let upperLine = line.toUpperCase();

        // 0. 过滤非标准混淆噪音标签
        if (upperLine.startsWith("#DISC-NOISE")) {
            continue;
        }

        // 1. 全局彻底清除 METHOD=NONE 标签（正片绝不需要该标签，广告多用来重置解密状态）
        if (upperLine.startsWith("#EXT-X-KEY") && upperLine.includes("METHOD=NONE")) {
            continue;
        }

        // 2. 广告特征 Key 直接剔除
        if (upperLine.startsWith("#EXT-X-KEY") && adKeywords.test(line)) {
            continue;
        }

        // 3. 保留播放列表头部元数据
        if (!headerDone) {
            if (upperLine.startsWith("#EXTINF") || upperLine.startsWith("#EXT-X-DISCONTINUITY")) {
                headerDone = true;
            } else {
                outputLines.push(line);
                continue;
            }
        }

        // 4. 时长标签暂存待判
        if (upperLine.startsWith("#EXTINF")) {
            pendingExtinf = line;
            continue;
        }

        // 5. 切片路径判定与清洗
        if (!line.startsWith("#")) {
            if (adKeywords.test(line)) {
                // 命中广告切片，废弃对应的 EXTINF
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

        // 6. 断点标签 (#EXT-X-DISCONTINUITY) 深度前瞻探测
        if (upperLine.startsWith("#EXT-X-DISCONTINUITY")) {
            let isAdSection = false;
            // 扩大前瞻范围至 15 行，确保能越过 EXTINF 探测到切片 URL
            for (let j = i + 1; j < Math.min(i + 16, lines.length); j++) {
                let testLine = lines[j].trim();
                let upperTest = testLine.toUpperCase();
                if (upperTest.startsWith("#EXT-X-DISCONTINUITY")) break;
                if (adKeywords.test(testLine)) {
                    isAdSection = true;
                    break;
                }
            }

            if (isAdSection) {
                continue;
            }

            // 防止正片开头或相邻位置留下冗余连续的 DISCONTINUITY
            if (outputLines.length > 0 && outputLines[outputLines.length - 1].toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) {
                continue;
            }

            outputLines.push(line);
            continue;
        }

        // 7. 正片正常 Key 及其它元数据原样保留
        outputLines.push(line);
    }

    body = outputLines.join("\n");
}

$done({
    response: { body: body },
    body: body
});
