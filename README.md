# 📚 适用于宝鸡文理学院的自动课表每日推送脚本

基于 **GitHub Actions** 和 **PushPlus/Bark** 的 Python 脚本，支持定时获取教务系统课表，生成 Markdown 日程表，搭配天气、每日情话推送到微信。

---

[![Release](https://img.shields.io/github/v/release/leisureea1/daily_push?color=%2337c6ff)](https://github.com/leisureea1/daily_push/releases)
[![Stars](https://img.shields.io/github/stars/leisureea1/daily_push?style=social)](https://github.com/leisureea1/daily_push/stargazers)
[![License](https://img.shields.io/github/license/leisureea1/daily_push)](LICENSE)
[![Hits](https://hits.sh/github.com/leisureea1/daily_push.svg?style=flat-square)](https://hits.sh/github.com/leisureea1/daily_push/)

---
## 🚀 功能特性

- ⏰ 每天早上定时运行
- 📋 自动获取当天课表并整理格式
- 🌦️ 显示天气、气温和穿衣建议
- 💌 搭配每日情话 / 鸡汤文案
- 🧭 支持 PushPlus / Bark 多平台推送

---

## 🌈 快速开始

### ✅ 1. Fork 本项目

点击右上角 `Fork` 按钮，将项目复制到自己的 GitHub 仓库。

---

### 🔐 2. 配置 Secrets

进入你的仓库：

```
Settings → Secrets → Actions → New repository secret
```

添加以下变量：

| Secret 名称       | 说明                                  |
|------------------|---------------------------------------|
| `PUSHPLUS_TOKEN` | [PushPlus](https://www.pushplus.plus/) 的 token |
| `BARK_URL`     | Bark 推送服务地址（可选）             |
| `USERNAME`| 教务系统账号（必填）               |
| `PASSWORD`     | 教务系统密码（必填）             |
| `TIANAPI_KEY`| 天行api（可选）               |

如果你只使用 PushPlus，只需设置 `PUSHPLUS_TOKEN`。

---

### ⚙️ 3. 启用 GitHub Actions

Fork 后默认不会自动执行，需要手动启用：

进入仓库主页 → 点击 `Actions` → 点击 `I understand... Enable workflows`

---

### 📆 4. 自动运行逻辑

- 脚本将于 **每天早上 7:00（北京时间）** 自动执行
- 可在 `push.yml` 中修改 `cron` 表达式自定义时间

---

## 🧑‍💻 自定义部署方式

### 🌀 方法一：GitHub Actions（推荐）

无需服务器，全自动云运行：

- 自动拉取课表数据
- 自动推送到微信或手机
- 完全免费

查看 GitHub Actions 日志调试效果。

---

### 🌿 方法二：青龙面板部署

1. 将 `push.py` 上传到青龙容器中
2. 新建 Python 定时任务：
3. 安装依赖：
4. 在青龙环境变量中配置与 GitHub Secrets 同名的变量：

- `PUSHPLUS_TOKEN`
- `BARK_URL`
- `TIANAPI_KEY`
- `USERNAME`
- `PASSWORD`
## 详细教程请移步：[@Leisure's Blog](https://blog.leisureea.com)
---

## 📁 文件结构

```text
.
├── .github/workflows/push.yml     # GitHub Actions 定时任务配置
├── push.py                        # 主脚本
├── requirements.txt               # 依赖列表
├── README.md                      # 项目说明
├── LICENSE                        # 开源协议
└── .gitignore
```

---

## 🧠 鸣谢与引用

- [PushPlus](https://pushplus.plus/)
- [Bark](https://github.com/Finb/Bark)
- 天气 API 来源于 [天行数据](https://www.tianapi.com/)
- 鸡汤 API 来自 [hitokoto.cn](https://hitokoto.cn/)

---

## 📄 License

本项目使用 [MIT License](./LICENSE) 协议开源，欢迎 Star、Fork、二次开发！

---

## ✍️ 作者 & 博客

作者：[@Leisureea](https://github.com/leisureea1)

博客地址：[@Leisure's Blog](https://blog.leisureea.com)

欢迎访问和交流！
