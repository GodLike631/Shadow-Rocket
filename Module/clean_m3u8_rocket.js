    // 非字串或空內容直接放行
    if (typeof originalBody !== "string" || !originalBody) {
        return $done({});
    }

    // 不是 HLS Playlist
    if (!originalBody.includes("#EXTM3U")) {
        return $done({});
    }

    const newline = originalBody.includes("\r\n") ? "\r\n" : "\n";
    const lines = originalBody.split(/\r?\n/);

    const discontinuityIndex = lines.findIndex(
        line => line.trim() === "#EXT-X-DISCONTINUITY"
    );

    // 沒有 discontinuity，不修改
    if (discontinuityIndex === -1) {
        return $done({});
    }

    /*
     * 找第一個媒體段 #EXTINF。
     *
     * 在第一個 EXTINF 前面的內容視為 Playlist Header，
     * 例如：
     *
     * #EXTM3U
     * #EXT-X-VERSION
     * #EXT-X-TARGETDURATION
     * #EXT-X-MEDIA-SEQUENCE
     * ...
     */
    const firstSegmentIndex = lines.findIndex(
        line => line.trim().startsWith("#EXTINF")
    );

    if (firstSegmentIndex === -1) {
        return $done({});
    }

    // discontinuity 必須位於媒體區域
    if (discontinuityIndex < firstSegmentIndex) {
        return $done({});
    }

    const header = lines.slice(0, firstSegmentIndex);

    /*
     * 從 discontinuity 下一行開始保留。
     * discontinuity 本身刪除。
     */
    const remaining = lines.slice(discontinuityIndex + 1);

    // 去除接合位置多餘空行
    while (header.length && header[header.length - 1].trim() === "") {
        header.pop();
    }

    while (remaining.length && remaining[0].trim() === "") {
        remaining.shift();
    }

    const body = [...header, ...remaining].join(newline);

    $done({ body });

} catch (error) {
    // 發生任何異常時保持原始回應，避免播放失敗
    $done({});
}
