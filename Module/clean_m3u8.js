/**
 * 影视 M3U8 通用去广告脚本（切片颗粒度清洗标准版）
 * 兼容: Surge / Loon / Quantumult X
 * Telegram群组：hxxps://t[.]me/tvshare23
 */

let body = $response.body;

if (typeof body === "string" && body.indexOf("#EXTM3U") !== -1) {
    // 1. 如果是 Master 主索引列表（包含多码率重定向标签），直接原样放行，严禁修改
    if (body.indexOf("#EXT-X-STREAM-INF") !== -1) {
        $done({ body: body });
    } else {
        // 2. 统一将 \r\n 规整为 \n 并按行拆分
        const rawLines = body.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
        const outputLines = [];

        // 精准广告特征词库（新增 power*play 18组广告切片Hash，并保留全量基准）
        const adKeywords = /(a2e91550e9009288|0a2acd07d03288af|4690328c6509c259|05bb649091fc096a|6c2930392cd9ebf8|f92bb5f778e1a655|39f3e5a2f5727612|c503e768f43dd945|5e832462b16dcf7f|899e4c25adb4829c|de1a12ef56b06437|d2eddf9bedda997d|fc76bef3267bdf23|4191e7c27087c514|32ecc33b8d1e7c15|7ec9ed3208d14032|6444e8ffb5a21d69|e6ee01f98adfd08f|CEBB1nJe|OaTAobvH|0qgR2U2V|UoK3btd2|10115kb|9gWW64MM|DoMaUgPr|2075kb|nlfRR6gH|RCP0FQBQ|7Lzh4PuW|V2C7MJhC|ymO7zGr9|Bjf6z0RU|jHKrrx6s|2078kb|a3a6eda11cbfa352|2f1563ca37e75212|2db1cf28fb771e0d|de820e92881bd4d1|6aa3d5aa8e8c1ac11479d82a|GB1mnQDZ|adjump|\/video\/adjump|1787319|178732000|84_9109598f|751808405d7|10152kb|9622kb|9641kb|10141kb|30EjJFTT|W7fqTmbJ|JKyp1S2D|5568049a638c79f9|ec5db3bbf268dd34|7e14ee319bf8017d|ac080df0b161b6fb|ea6bb8a311db9dd0|1f1d60431202f328|39803bb0fa0ec24b|787de3b9178c4058|0916de7dab851cd8|65e7a9371db1b651|Zse0Tpg8|seg_iif|9c08cdc|a6b9d4136946ad41|a0fd38|\/stream\/|\/mov\/AD\/|8jlf67z19|C7bAbClC|erlgnf\.com|^\/\d{8}\/[a-f0-9]{16}\/seg_)/i;

        let pendingExtinf = null;
        let pendingDiscontinuity = false;
        let hasAdRemoved = false;

        for (let i = 0; i < rawLines.length; i++) {
            let line = rawLines[i].trim();
            if (!line) continue;

            let upperLine = line.toUpperCase();

            // 过滤混淆与注入标签
            if (upperLine.startsWith("#DISC-NOISE") || upperLine.includes("PPVOD-AD-INJECTED")) {
                continue;
            }

            // 剔除明文加密切换标签
            if (upperLine.startsWith("#EXT-X-KEY") && upperLine.includes("METHOD=NONE")) {
                continue;
            }

            // 广告专属 Key 剔除（命中词库直接丢弃）
            if (upperLine.startsWith("#EXT-X-KEY") && adKeywords.test(line)) {
                continue;
            }

            // 捕获断点标签
            if (upperLine.startsWith("#EXT-X-DISCONTINUITY")) {
                pendingDiscontinuity = true;
                continue;
            }

            // 正片真实解密 Key：保证断点在 Key 之前输出
            if (upperLine.startsWith("#EXT-X-KEY")) {
                if (pendingDiscontinuity || hasAdRemoved) {
                    if (outputLines.length > 0 && !outputLines[outputLines.length - 1].toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) {
                        outputLines.push("#EXT-X-DISCONTINUITY");
                    }
                    pendingDiscontinuity = false;
                    hasAdRemoved = false;
                }
                outputLines.push(line);
                continue;
            }

            // 暂存切片时长标签
            if (upperLine.startsWith("#EXTINF")) {
                pendingExtinf = line;
                continue;
            }

            // 处理切片实体行
            if (!line.startsWith("#")) {
                if (adKeywords.test(line)) {
                    // 命中广告切片：直接清除该切片与时长
                    pendingExtinf = null;
                    hasAdRemoved = true;
                } else {
                    // 正片切片
                    if (pendingDiscontinuity || hasAdRemoved) {
                        if (outputLines.length > 0 && !outputLines[outputLines.length - 1].toUpperCase().startsWith("#EXT-X-DISCONTINUITY")) {
                            outputLines.push("#EXT-X-DISCONTINUITY");
                        }
                        pendingDiscontinuity = false;
                        hasAdRemoved = false;
                    }
                    if (pendingExtinf) {
                        outputLines.push(pendingExtinf);
                        pendingExtinf = null;
                    }
                    outputLines.push(line);
                }
                continue;
            }

            // 其它标准元数据原样保留
            outputLines.push(line);
        }

        body = outputLines.join("\n");
        $done({ body: body });
    }
} else {
    $done({ body: body });
}
