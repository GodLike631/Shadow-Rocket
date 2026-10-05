/**
 * 影视 M3U8 片头+片中通用清洗脚本
 * 兼容平台: Surge / Shadowrocket / Loon / Quantumult X
 */

let body = $response.body;

if (typeof body === "string" && body.indexOf("#EXTM3U") !== -1) {
    const lines = body.split("\n");
    const outputLines = [];

    // 广告切片目录特征库（命中即视作垃圾切片）
    const adKeywords = /(9641kb|Zse0Tpg8|cdn-99\.cc|\/ad\/|\/advert\/|adjump)/i;

    let headerDone = false;
    let pendingExtinf = null;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        if (!line) continue;

        // 1. 保留顶部头部信息（直到遇到第一个分界标签或切片）
        if (!headerDone) {
            if (line.startsWith("#EXTINF") || line.startsWith("#EXT-X-DISCONTINUITY")) {
                headerDone = true;
            } else {
                // 去除头部可能附带的明文广告空 KEY
                if (line.startsWith("#EXT-X-KEY:METHOD=NONE")) continue;
                outputLines.push(line);
                continue;
            }
        }

        // 2. 遇到时长标签，先暂存（判断下一行切片地址是不是广告）
        if (line.startsWith("#EXTINF")) {
            pendingExtinf = line;
            continue;
        }

        // 3. 遇到切片路径行
        if (!line.startsWith("#")) {
            if (adKeywords.test(line)) {
                // 命中广告切片，丢弃当前切片和前置暂存的 #EXTINF
                pendingExtinf = null;
            } else {
                // 是正片切片：把暂存的 #EXTINF 和切片行推入输出
                if (pendingExtinf) {
                    outputLines.push(pendingExtinf);
                    pendingExtinf = null;
                }
                outputLines.push(line);
            }
            continue;
        }

        // 4. 遇到 #EXT-X-DISCONTINUITY 断点标签
        if (line.startsWith("#EXT-X-DISCONTINUITY")) {
            // 向后预判 4 行，看紧随其后的是不是广告切片
            let isAdSection = false;
            for (let j = i + 1; j < Math.min(i + 6, lines.length); j++) {
                let testLine = lines[j].trim();
                if (testLine.startsWith("#EXT-X-DISCONTINUITY")) break;
                if (adKeywords.test(testLine)) {
                    isAdSection = true;
                    break;
                }
            }

            // 如果断点紧跟着广告，或者是广告结束回归正片的过渡断点，直接剔除该断点
            if (isAdSection) {
                continue;
            }
            
            // 如果上一个输出的也是断点，避免连续残留断点
            if (outputLines.length > 0 && outputLines[outputLines.length - 1].startsWith("#EXT-X-DISCONTINUITY")) {
                continue;
            }

            outputLines.push(line);
            continue;
        }

        // 5. 遇到加密 KEY 声明（METHOD=AES-128 等正片解密指令必须保留）
        if (line.startsWith("#EXT-X-KEY")) {
            if (line.includes("METHOD=NONE")) {
                // 如果紧跟着的是广告切片，丢弃该空 Key
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

        // 6. 其他标准控制标签直接保留
        outputLines.push(line);
    }

    body = outputLines.join("\n");
}

$done({
    response: { body: body },
    body: body
});
