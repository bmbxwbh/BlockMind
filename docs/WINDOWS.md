# 🪟 Windows 部署指南

## 前置要求

| 软件 | 版本 | 下载地址 |
|------|------|----------|
| Python | 3.10+ | https://python.org |
| Java | 17+ | https://adoptium.net/ |
| Git | 最新 | https://git-scm.com/ |

> 安装 Python 时务必勾选 **"Add Python to PATH"**

## 快速安装

### 方式一：一键脚本（推荐）

```cmd
# 1. 克隆项目
git clone https://github.com/bmbxwbh/BlockMind.git
cd BlockMind

# 2. 运行安装脚本
install.bat

# 3. 编辑配置
notepad config.yaml

# 4. 启动
start_all.bat
```

### 方式二：手动安装

```cmd
# 1. 安装依赖
pip install -r requirements.txt

# 2. 复制配置
copy config.example.yaml config.yaml

# 3. 编辑 config.yaml，填入你的 AI 模型配置

# 4. 创建数据目录
mkdir data\skills data\logs data\memory data\backups

# 5. 启动 BlockMind
python -m src.main
```

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `install.bat` | 一键安装依赖 + 初始化配置 |
| `start.bat` | 启动 BlockMind 后端 + WebUI |
| `start_mc.bat` | 启动 Minecraft 服务端 |
| `start_all.bat` | 一键启动全部（MC + BlockMind） |

## Minecraft 服务端配置

### 下载 Fabric 服务端

1. 访问 https://fabricmc.net/use/server/
2. 选择 Minecraft 版本 **1.20.4**
3. 下载服务端 JAR 文件
4. 将 JAR 放到项目根目录的 `mc-server/` 文件夹
5. 运行 `start_mc.bat`

### 安装 BlockMind Mod

1. 从 [GitHub Releases](https://github.com/bmbxwbh/BlockMind/releases) 下载最新 Mod JAR
2. 将 JAR 放到 `mc-server/mods/` 文件夹
3. 重启 Minecraft 服务端

### 内存配置

编辑 `start_mc.bat`，修改 `MAX_RAM` 变量：

```cmd
:: 4GB 内存的机器
set MAX_RAM=1G

:: 8GB 内存的机器
set MAX_RAM=2G

:: 16GB 内存的机器
set MAX_RAM=4G
```

## WebUI 访问

启动后打开浏览器：

- 地址：http://localhost:19951
- 密码：见 `config.yaml` 中的 `webui.auth.password`

## 常见问题

### Q: `python` 命令找不到？

确保 Python 安装时勾选了 "Add Python to PATH"，或者尝试用 `py` 命令代替。

### Q: 端口 19951 被占用？

编辑 `config.yaml`，修改 `webui.port` 为其他端口。

### Q: MC 服务端启动失败？

1. 确认 Java 17+ 已安装：`java -version`
2. 确认 `eula.txt` 中 `eula=true`
3. 检查端口 25565 是否被占用

### Q: 防火墙拦截？

Windows 防火墙可能会拦截 Python 和 Java 的网络访问，首次启动时点击"允许访问"。

```cmd
:: 或手动添加防火墙规则
netsh advfirewall firewall add rule name="BlockMind WebUI" dir=in action=allow program="%~dp0python.exe" enable=yes
netsh advfirewall firewall add rule name="Minecraft Server" dir=in action=allow program="java.exe" enable=yes localport=25565 protocol=TCP
```

## 目录结构

```
BlockMind/
├── start.bat          # 启动 BlockMind
├── start_mc.bat       # 启动 MC 服务端
├── start_all.bat      # 全部启动
├── install.bat        # 安装脚本
├── config.yaml        # 配置文件
├── mc-server/         # MC 服务端（手动创建）
│   ├── fabric-server-launch.jar
│   ├── mods/          # Mod 放这里
│   └── world/         # 世界存档
├── data/              # 运行数据
│   ├── memory/        # AI 记忆
│   ├── logs/          # 日志
│   └── backups/       # 备份
└── src/               # 源码
```
