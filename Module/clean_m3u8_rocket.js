/**
 * Surge 与 Shadowrocket 双兼容完整版
 */
let body = $response.body;

if (typeof body === "string" && body.indexOf("#EXTM3U") !== -1) {
    let discoIndex = body.indexOf("#EXT-X-DISCONTINUITY");
    if (discoIndex !== -1) {
        let firstExtinf = body.indexOf("#EXTINF");
        let header = firstExtinf !== -1 ? body.substring(0, firstExtinf) : "#EXTM3U\n";
        let nextLineIndex = body.indexOf("\n", discoIndex);
        if (nextLineIndex !== -1) {
            body = header.trim() + "\n" + body.substring(nextLineIndex + 1).trim();
        }
    }
}

$done({ response: { body: body }, body: body });
