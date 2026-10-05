/**
 * 影视 M3U8 通用全段（片头 + 片中）去广告清洗脚本
 * 支持: 片头前置贴片清洗 + 片中插入广告区间剔除 + AES-128 密钥防护
 * 兼容: Surge / Shadowrocket / Loon / Quantumult X
 */

let body = $response.body;

if (typeof body === "string" && body.indexOf("#EXTM3U") !== -1 && body.indexOf("#EXT-X-DISCONTINUITY") !== -1) {
    const lines = body.split("\n");
    const outputLines = [];

    // 广告特征正则（命中任意即视作广告切片目录）
    const adKeywords = /(9641kb|Zse0Tpg8|cdn-99\.cc|\/ad\/|\/advert\/|adjump)/i;

    let isInsideAdBlock = false;
    let headerCollected = false;
    let isFirstContent = true;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        if (!line) continue;

        // 1. 采集并无损保留文件头
        if (!headerCollected) {
            if (line.startsWith("#EXTINF")) {
                headerCollected = true;
            } else {
                // 剔除头部的明文无加密伪声明（如果存在）
                if (line.startsWith("#EXT-X-KEY:METHOD=NONE")) {
                    continue;
                }
                outputLines.push(line);
                continue;
            }
        }

        // 2. 遇到断点标签
        if (line.startsWith("#EXT-X-DISCONTINUITY")) {
            // 查看后续几行切片是否具有广告特征
            let lookAheadIsAd = false;
            for (let j = i + 1; j < Math.min(i + 8, lines.length); j++) {
                let nextLine = lines[j].trim();
                if (nextLine.startsWith("#EXT-X-DISCONTINUITY")) break;
                if (adKeywords.test(nextLine)) {
                    lookAheadIsAd = true;
                    break;
                }
            }

            if (isFirstContent || lookAheadIsAd) {
                // 属于片头贴片，或已被预读命中广告特征，标记进入广告段
                isInsideAdBlock = true;
                continue;
            } else if (isInsideAdBlock) {
                // 当前正处于广告段，遇到第二个断点，代表广告段落结束，正片恢复
                isInsideAdBlock = false;
                continue;
            } else {
                // 属于正片内部合理的断点，予以放行
                outputLines.push(line);
                continue;
            }
        }

        // 3. 广告块内部的内容（切片、时长标签、临时 KEY）全部丢弃
        if (isInsideAdBlock) {
            // 防御机制：如果在广告段内撞见了正片的强特征密钥声明，强行拉回正片状态
            if (line.startsWith("#EXT-X-KEY") && !line.includes("METHOD=NONE")) {
                isInsideAdBlock = false;
                outputLines.push(line);
            }
            continue;
        }

        // 4. 单行切片特征兜底过滤（即便断点异常，也能单切片拦截）
        if (adKeywords.test(line)) {
            // 如果上一行是对应的 #EXTINF，撤回丢弃
            if (outputLines.length > 0 && outputLines[outputLines.length - 1].startsWith("#EXTINF")) {
                outputLines.pop();
            }
            continue;
        }

        // 5. 纯净的正片行，收录
        isFirstContent = false;
        outputLines.push(line);
    }

    body = outputLines.join("\n");
}

// 统一回传
$done({
    response: { body: body },
    body: body
});
