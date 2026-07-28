```markdown
# ⚡️ Shadowrocket Node Rename Script

![Stars](https://img.shields.io/github/stars/yourname/yourrepo?style=flat-square)
![Python](https://img.shields.io/badge/JavaScript-ES6%2B-yellow?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Shadowrocket-blue?style=flat-square)
![Telegram](https://img.shields.io/badge/Telegram-%E9%A2%91%E9%81%93-2CA5E0?style=flat-square)

> 👑 **欢迎使用【Shadowrocket 节点自动化重命名脚本】**！本项目基于正则解析与动态规则匹配机制，自动剔除无效广告节点，精准将节点名称转化为`国旗 Emoji + ISO 缩写`的标准格式，为您打造极致整洁、规范清晰的节点列表体验。

---

## 🤝 致敬与鸣谢 (Credits)

本脚本的研发与优化离不开开源社区的无私贡献，特此向以下大佬致以最崇高的敬意与感谢：

* 🐬 **开源社区大佬** —— 感谢提供核心匹配逻辑与算法灵感。
* 🌸 **业内所有开源贡献者** —— 感谢 Shadowrocket 生态内所有默默付出的规则及脚本开发者。

⚠️ **使用声明**：本仓库脚本仅用于个人技术交流与节点美化。版权归原作者所有，如有侵权或规则冲突，请联系删除。

---

## 📡 核心配置与参数说明

| 配置项 | 变量名称 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| **前缀修饰** | `customCharStart` | `➥` | 节点名称前缀符号，设为 `""` 即禁用 |
| **后缀修饰** | `customCharEnd` | `ᵐᵗ` | 节点名称后缀符号，设为 `""` 即禁用 |
| **语言切换** | `outputLanguage` | `EN` | 支持 `CN`（中文）与 `EN`（英文） |
| **垃圾过滤** | `filterKeywords` | 数组 | 自动识别并丢弃包含“测试/广告/失效”等关键词节点 |

---

## 💡 转换效果对比

| 原始节点名称 | 脚本处理后名称 | 处理逻辑 |
| :--- | :--- | :--- |
| ⭐️ **洛杉矶-美国** | `➥🇺🇸USᵐᵗ` | 自动匹配地区映射为国旗+缩写，追加自定义前后缀 |
| ⭐️ **香港 HY2 高速** | `➥🇭🇰HK-GPTᵐᵗ` | 识别地区并执行 `HY2` ➔ `GPT` 协议/功能别名替换 |
| ⚠️ **过期测试-广告** | *(已丢弃)* | 触发 `filterKeywords` 过滤规则，自动剔除垃圾节点 |

---

## 🚀 快速开始

```text
[订阅管理] ➔ [点击 ⓘ 图标] ➔ [节点过滤 / Filter] ➔ [粘贴脚本] ➔ [保存]
```

1. 打开 **Shadowrocket**，进入 **订阅** 页面。
2. 点击目标订阅项右侧的 **ⓘ** 详情按钮。
3. 找到 **过滤 (Filter)** 配置选项。
4. 将本脚本全部代码复制并粘贴至输入框内。
5. 点击 **保存** 即可实时完成节点洗牌与重排。
```
