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

        // 精准广告特征词库（包含 ryiplay18 片中两段独立插播广告切片 Hash 及所有历史全集）
        const adKeywords = /(7a52b3e0d5a61234f6f716867ec59b65|f129eaf09d0d93316a2f6f38d7214029|20c692463e73a649ab78ffc5c542905a|86fc81a0a9e6f0208f111ac7c63f65b3|a50d5ec9c3327f405f65cbf25a260f25|aaab4b0ade040aac116177afc8cea7bd|1a761b417fd6c6aa3f446bc1829d0394|9f6fc65134f1715660a417d60371cf83|1e9a8df0cd354c6e3561005b760b968d|8ca305388c7d33d288f66f4580867e85|39e8dc8cd5c8fb5e68f49998e724259e|4082412a445c8621202a93d1abf99b01|a96778aae7a971d10927d10846bef9ca|e96a8ca90f4e458c0cea7ba9320062f4|1f3dd82b245fe769e01ea816289a36e3|b6ddef913c69c36961acfe8d9182ffcc|3db83e0d0d1527fc160682ac90ec4059|41445af00cd823b10d4fcdcb0c800ae3|a678b55a5ec1960f64b1a7cfaa91f53d|c691c2a58dc874d4aa147c258cde37d4|166593c3606102a401019474fce039d9|deb4334407d17d1347cf7ed3f09f4149|1d719833da91dd2394e07b107c2571ed|86e274c34cb03dec26ac1ab83c3441b9|69308648a4705fb418f797096ba98748|60ffd2f4c2e0fbf96171176292ba2152|c41e19f3051fc03b559186c8c59275e7|38f96abdc88197de1f5ab881188d950a|ed4d44ff768aa508a7f60af6c698cca7|6756d685ca4ee76fd26db898bdd598d9|80376b1876e9e59ab4e7fbf957801e11|b324328a439f7e056262a54805420910|b979a2e62235b8f8264da66d6cb61e7c|bc3cec3f3663ef3df502132bc49b8000|4af5dcd5c9509d868be51b8e83646f2c|562c943117f10003b1e453293cdfa6c1|f4a3fae304e61995864bb36a678c02d7|e21886bb8d8de2034d608e1508500a7b|5d965933361f9a6a387b47d185ec19d1|c5f90eb6a9f33da0157a995332ace2f8|a857e6d222d2cd7c42dd3ae6bc9fc419|3321429ca1e11c655bfcbab7cb8f0308|36b1ff4e13c9cdfdedede79d14efb479|54426637dfa41b3edb43c13e36bf97a7|63805c19a0781ab931707cc66106a0da|97d341feb549d359140393e11dc0cbb4|3ab4450de204673e0e11192c96e11320|e18997a1d8ff1037997c53b8693cd4fb|75315dddea36232acb50dc0e54ad371c|9c999db913882bf6a57d705aa74ce174|7daf01a4bb3779f876adaa440746eb45|17d215de63c9b4359ed0a708efc5d884|cebf27a04c9f1d66356b96ac181cd72e|43019a357ca46f99dae3a02bc543692e|a2e91550e9009288|0a2acd07d03288af|4690328c6509c259|05bb649091fc096a|6c2930392cd9ebf8|f92bb5f778e1a655|39f3e5a2f5727612|c503e768f43dd945|5e832462b16dcf7f|899e4c25adb4829c|de1a12ef56b06437|d2eddf9bedda997d|fc76bef3267bdf23|4191e7c27087c514|32ecc33b8d1e7c15|7ec9ed3208d14032|6444e8ffb5a21d69|e6ee01f98adfd08f|CEBB1nJe|OaTAobvH|0qgR2U2V|UoK3btd2|10115kb|9gWW64MM|DoMaUgPr|2075kb|nlfRR6gH|RCP0FQBQ|7Lzh4PuW|V2C7MJhC|ymO7zGr9|Bjf6z0RU|jHKrrx6s|2078kb|a3a6eda11cbfa352|2f1563ca37e75212|2db1cf28fb771e0d|de820e92881bd4d1|6aa3d5aa8e8c1ac11479d82a|GB1mnQDZ|adjump|\/video\/adjump|1787319|178732000|84_9109598f|751808405d7|10152kb|9622kb|9641kb|10141kb|30EjJFTT|W7fqTmbJ|JKyp1S2D|5568049a638c79f9|ec5db3bbf268dd34|7e14ee319bf8017d|ac080df0b161b6fb|ea6bb8a311db9dd0|1f1d60431202f328|39803bb0fa0ec24b|787de3b9178c4058|0916de7dab851cd8|65e7a9371db1b651|Zse0Tpg8|seg_iif|9c08cdc|a6b9d4136946ad41|a0fd38|\/stream\/|\/mov\/AD\/|8jlf67z19|C7bAbClC|erlgnf\.com|^\/\d{8}\/[a-f0-9]{16}\/seg_)/i;

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
