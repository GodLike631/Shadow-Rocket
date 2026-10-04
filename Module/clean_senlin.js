let body = $response.body;

if (typeof body === "string" && body.indexOf("#EXTM3U") !== -1) {
    let discoIndex = body.indexOf("#EXT-X-DISCONTINUITY");
    if (discoIndex !== -1) {
        // 提取第 1~6 行纯净头部（截取到第一个 #EXTINF 之前）
        let firstExtinf = body.indexOf("#EXTINF");
        let header = firstExtinf !== -1 ? body.substring(0, firstExtinf) : "#EXTM3U\n";
        
        // 找到 #EXT-X-DISCONTINUITY 之后的下一个换行符
        let nextLineIndex = body.indexOf("\n", discoIndex);
        if (nextLineIndex !== -1) {
            // 拼接纯净头与正片切片（直接保留第 26 行的 AES-128 KEY 和后续正片）
            body = header.trim() + "\n" + body.substring(nextLineIndex + 1).trim();
        }
    }
}

$done({ body: body });
