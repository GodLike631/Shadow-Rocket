# ⚡ Shadow-Rocket Node Renamer

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Shadowrocket-blue?style=for-the-badge&logo=shadowrocket" alt="Platform">
  <img src="https://img.shields.io/badge/Language-JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="Language">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>精细化·自动化·极简美学的节点名称正则重构脚本</b>
  <br>
  <sub>赋予你的代理订阅更加直观、美观且干净的展示体验</sub>
</p>

---

## 💡 为什么需要它？

`Shadow-Rocket Node Renamer` 专为追求订阅界面极致整洁的用户打造。脚本通过内置的**多国地理数据库**与**正则提取算法**，自动清洗广告节点、对齐国旗标识，并注入自定义高亮前后缀，实现节点的标准化重命名。

> <b>✨ 转换示例：</b>
> 
> `洛杉矶-HK-01-专线[测试]` ➔ **`➥🇭🇰HKᵐᵗ`**
> 
> `美国-01-HY2-高速` ➔ **`➥🇺🇸US-GPTᵐᵗ`**

---

## 🛠️ 核心黑科技特性

```text
┌─────────────────────────────────────────────────────────┐
│                    Processing Pipeline                  │
│                                                         │
│  [原始节点] ──> [垃圾过滤] ──> [精准识别] ──> [修饰注入] ──> [美化完成]  │

/* ==================== 🛠️ 用户配置区域 ==================== */

// 1. 全局前后缀修饰符
const customCharStart = "➥";  // 节点前缀 (置空 "" 即关闭)
const customCharEnd   = "ᵐᵗ"; // 节点后缀 (置空 "" 即关闭)

// 2. 语言模式 ('CN' | 'EN')
const outputLanguage  = "EN"; // EN: 🇺🇸US | CN: 🇺🇸美国

// 3. 广告/垃圾节点过滤词黑名单
const filterKeywords  = ["广告", "无效", "测试", "官网", "过期", "续费"];

// 4. 节点特殊标签映射 (保留并替换功能关键词)
const keywordsMap     = {
    "HY2": "GPT",
    "IEPL": "专线"
};

/* ======================================================= */
└─────────────────────────────────────────────────────────┘
