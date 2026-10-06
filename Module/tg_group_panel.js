/**
 * Telegram 群组状态与一键禁言/解禁 Panel
 * GitHub: 支持通用部署，通过 Surge Argument 传参
 */

// 1. 从 Surge Module 的 argument 中解析配置，格式形如：token=123:ABC&chat_id=-100123456
const parseArgs = (argStr) => {
  const args = {};
  if (!argStr) return args;
  argStr.split("&").forEach((item) => {
    const [key, val] = item.split("=");
    if (key && val) args[key.trim()] = decodeURIComponent(val.trim());
  });
  return args;
};

const args = parseArgs(typeof $argument !== "undefined" ? $argument : "");
const BOT_TOKEN = args.token || "";
const CHAT_ID = args.chat_id || "";

// 基础参数校验
if (!BOT_TOKEN || !CHAT_ID) {
  $done({
    title: "TG 群控面板",
    content: "未配置 token 或 chat_id，请检查模块参数",
    icon: "exclamationmark.circle.fill",
    "icon-color": "#FF9500"
  });
} else {
  main();
}

const API_BASE = `https://api.telegram.org/bot${BOT_TOKEN}`;

function request(endpoint, payload = null) {
  return new Promise((resolve, reject) => {
    const isPost = payload !== null;
    const options = {
      url: `${API_BASE}/${endpoint}`,
      method: isPost ? "POST" : "GET",
      headers: isPost ? { "Content-Type": "application/json" } : {},
      body: isPost ? JSON.stringify(payload) : undefined,
      timeout: 6000,
    };

    const handler = (error, response, data) => {
      if (error) {
        reject(error);
        return;
      }
      try {
        const json = JSON.parse(data);
        if (json.ok) {
          resolve(json.result);
        } else {
          reject(json.description || "API 返回错误");
        }
      } catch (e) {
        reject("响应解析失败");
      }
    };

    if (isPost) {
      $httpClient.post(options, handler);
    } else {
      $httpClient.get(options, handler);
    }
  });
}

async function main() {
  try {
    // 获取群组详情与成员总数
    const chatInfo = await request(`getChat?chat_id=${CHAT_ID}`);
    const memberCount = await request(`getChatMemberCount?chat_id=${CHAT_ID}`);

    const title = chatInfo.title || "TG 群组";
    const currentPerms = chatInfo.permissions || {};
    
    // 判断当前是否处于禁言状态 (can_send_messages 为 false 即为禁言)
    const isMuted = currentPerms.can_send_messages === false;

    // Surge Panel 点击触发 (反转全员发言权限)
    if (typeof $trigger !== "undefined" && $trigger === "button") {
      const targetState = !isMuted;

      await request("setChatPermissions", {
        chat_id: CHAT_ID,
        permissions: {
          can_send_messages: !targetState,
          can_send_audios: !targetState,
          can_send_documents: !targetState,
          can_send_photos: !targetState,
          can_send_videos: !targetState,
          can_send_video_notes: !targetState,
          can_send_voice_notes: !targetState,
          can_send_polls: !targetState,
          can_send_other_messages: !targetState,
          can_add_web_page_previews: !targetState,
          can_change_info: false,
          can_invite_users: true,
          can_pin_messages: false
        }
      });

      $notification.post("群状态变更", title, targetState ? "🔒 已开启全员禁言" : "🔓 已解除全员禁言");

      $done({
        title: `${title} (${memberCount}人)`,
        content: targetState ? "状态: 🔴 全员禁言中 [点击解禁]" : "状态: 🟢 正常发言 [点击锁群]",
        icon: targetState ? "lock.fill" : "lock.open.fill",
        "icon-color": targetState ? "#FF3B30" : "#34C759"
      });
      return;
    }

    // 默认定时轮询或打开 Surge 刷新展示
    $done({
      title: `${title} (${memberCount}人)`,
      content: isMuted ? "状态: 🔴 全员禁言中 [点击解禁]" : "状态: 🟢 正常发言 [点击锁群]",
      icon: isMuted ? "lock.fill" : "lock.open.fill",
      "icon-color": isMuted ? "#FF3B30" : "#34C759"
    });

  } catch (err) {
    $done({
      title: "TG 群控面板",
      content: `错误: ${typeof err === "string" ? err : JSON.stringify(err)}`,
      icon: "exclamationmark.triangle.fill",
      "icon-color": "#FF9500"
    });
  }
}
