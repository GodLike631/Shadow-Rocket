/**
 * 影视 M3U8 通用贴片去广告清洗脚本
 * 兼容平台: Surge / Shadowrocket / Loon / Quantumult X
 * 特征支持: 自动保留原生头部、自动跳过不连续广告块、保留正片 AES-128 密钥
 */

let body = $response.body;

if (typeof body === "string" && body.indexOf("#EXTM3U") !== -1) {
    const discoTag = "#EXT-X-DISCONTINUITY";
    let discoIndex = body.indexOf(discoTag);

    // 命中广告分界标签才执行清洗，避免破坏正常无广告的 M3U8
    if (discoIndex !== -1) {
        // 1. 提取第 1 段内容之前的头部信息（到第一个 #EXTINF 前）
        let firstExtinf = body.indexOf("#EXTINF");
        let header = firstExtinf !== -1 ? body.substring(0, firstExtinf) : "#EXTM3U\n";

        // 2. 找到最后一个或第一个 #EXT-X-DISCONTINUITY 之后的起始换行符
        // （绝大多数采集站只有前置广告，取第一个断点之后的正片即可）
        let nextLineIndex = body.indexOf("\n", discoIndex);

        if (nextLineIndex !== -1) {
            let mainContent = body.substring(nextLineIndex + 1).trim();
            // 重新拼接标准头与干净的正片内容（保留正片的 KEY 和所有切片）
            body = header.trim() + "\n" + mainContent;
        }
    }
}

// 统一兼容 Surge 的 { body } 与小火箭的 { response: { body } } 返回结构
$done({
    response: { body: body },
    body: body
});
