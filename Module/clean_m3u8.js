/**
 * 影视 M3U8 通用去广告脚本（分块状态机终极稳定版）
 * 兼容: Surge / Shadowrocket / Loon / Quantumult X
 * Telegram群组：https://t.me/tvshare23
 */

let body = $response.body;

if (typeof body === "string" && body.indexOf("#EXTM3U") !== -1) {
    // 归一化换行符
    const rawLines = body.replace(/\r/g, "").split("\n");
    const outputLines = [];

    // 广告特征库（已包含全部历史特征）
    const adKeywords = /(9641kb|Zse0Tpg8|seg_iif|9c08cdc|cdn-99\.cc|C7bAbClC|erlgnf\.com|\/ad\/|\/advert\/|adjump)/i;

    let inHeader = true;
    let currentBlock = [];
    let blockHasAd = false;

    // 提交当前块数据的辅助函数
    function flushBlock() {
        if (!blockHasAd && currentBlock.length > 0) {
            for (let k = 0; k < currentBlock.length; k++) {
                outputLines.push(currentBlock[k]);
            }
        }
        currentBlock = [];
        blockHasAd = false;
    }

    for (let i = 0; i < rawLines.length; i++) {
        let line = rawLines[i].trim();
        if (!line) continue;

        let upperLine = line.toUpperCase();

        // 1. 过滤干扰混淆标签
        if (upperLine.startsWith("#DISC-NOISE")) {
            continue;
        }

        // 2. 头部元数据区（在遇到第一个切片、第一个断点或密钥前）
        if (inHeader) {
            if (upperLine.startsWith("#EXTINF") || upperLine.startsWith("#EXT-X-DISCONTINUITY") || upperLine.startsWith("#EXT-X-KEY")) {
                inHeader = false;
                // 转入块处理逻辑
            } else {
                outputLines.push(line);
                continue;
            }
        }

        // 3. 遇到断点标签：标志着上一个块结束，新块开始
        if (upperLine.startsWith("#EXT-X-DISCONTINUITY")) {
            flushBlock();
            // 先不把 DISCONTINUITY 放进新块，等确认新块是非广告块后再决定是否保留
            continue;
        }

        // 4. 块内属性探测与收集
        if (upperLine.startsWith("#EXT-X-KEY:METHOD=NONE")) {
            // 广告块通常带有 METHOD=NONE，不压入正片流
            continue;
        }

        // 检测 Key 是否含广告特征
        if (upperLine.startsWith("#EXT-X-KEY") && adKeywords.test(line)) {
            blockHasAd = true;
            continue;
        }

        // 检测切片 URL 是否含广告特征
        if (!line.startsWith("#")) {
            if (adKeywords.test(line)) {
                blockHasAd = true;
            }
        }

        currentBlock.push(line);
    }

    // 刷出最后一个块
    flushBlock();

    // 4. 结尾规范化与双重断点清理
    const finalLines = [];
    for (let j = 0; j < outputLines.length; j++) {
        let l = outputLines[j];
        // 清除开头多余的 DISCONTINUITY
        if (finalLines.length === 0 && l.toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) {
            continue;
        }
        // 清除连续重复的 DISCONTINUITY
        if (l.toUpperCase().startsWith("#EXT-X-DISCONTINUITY") && 
            finalLines.length > 0 && 
            finalLines[finalLines.length - 1].toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) {
            continue;
        }
        finalLines.push(l);
    }

    body = finalLines.join("\n");
}

// 统一标准输出，防止跨客户端兼容性问题
$done({ body: body });
