# 📋 开发任务清单 — Claude Code 优化版

> 每个任务 = 一个 Claude Code 会话，包含：精确文件路径、函数签名、验收标准
> 项目根目录：`/root/projects/BlockMind/`

---

## 任务格式说明

每个任务块包含：
- **文件路径**：Claude Code 需要创建/修改的精确文件
- **输入**：前置依赖（哪些文件/模块已存在）
- **输出**：需要创建的类/函数签名（Python 代码）
- **验收**：运行什么命令验证通过

---

## P0: 项目初始化

### Task 0.1 — 搭建基础框架

```
目标：创建所有 src/ 下的 __init__.py 和核心入口文件
工作目录：/root/projects/BlockMind/
```

**需要创建的文件：**

```python
# src/__init__.py — 空文件
# src/core/__init__.py — 空文件
# src/game/__init__.py — 空文件
# src/skills/__init__.py — 空文件
# src/ai/__init__.py — 空文件
# src/safety/__init__.py — 空文件
# src/monitoring/__init__.py — 空文件
# src/webui/__init__.py — 空文件
# src/config/__init__.py — 空文件
# src/utils/__init__.py — 空文件

# src/main.py — 主入口
```

`src/main.py` 需要包含：

```python
"""Minecraft AI Companion 主入口"""
import asyncio
import signal
import sys
from src.config.loader import load_config
from src.core.engine import CompanionEngine
from src.utils.logger import setup_logger

async def main():
    config = load_config("config.yaml")
    logger = setup_logger(config.logging)
    logger.info("🎮 Minecraft AI Companion 启动中...")

    engine = CompanionEngine(config)

    # 优雅退出
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(engine.shutdown()))

    await engine.start()

if __name__ == "__main__":
    asyncio.run(main())
```

**验收命令：**
```bash
cd /root/projects/BlockMind && python -c "from src.main import main; print('✅ 框架搭建成功')"
```

---

### Task 0.2 — 配置加载器

```
目标：实现配置文件加载与校验
工作目录：/root/projects/BlockMind/
```

**需要创建的文件：**

`src/config/loader.py`:

```python
"""配置加载与校验"""
import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class GameConfig(BaseModel):
    server_ip: str
    server_port: int = 25565
    username: str
    version: str = "1.20.4"
    auth_mode: str = "offline"
    reconnect_enabled: bool = True
    reconnect_interval: int = 5
    reconnect_max_retries: int = -1

class AIConfig(BaseModel):
    provider: str = "openai"
    api_key: str
    model: str = "gpt-4o"
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = True
    thinking_enabled: bool = True
    thinking_max_tokens: int = 8192

class SkillsConfig(BaseModel):
    storage_path: str = "./skills"
    validation_syntax: bool = True
    validation_safety: bool = True
    validation_logic: bool = True
    validation_max_retries: int = 3
    auto_repair: bool = True
    versioning_enabled: bool = True
    versioning_max: int = 10

class SafetyConfig(BaseModel):
    audit_log_enabled: bool = True
    audit_log_retention_days: int = 30
    auth_enabled: bool = True
    auth_timeout: int = 30
    auth_timeout_action: str = "deny"
    emergency_takeover_enabled: bool = True
    emergency_auto_repair: bool = True
    risk_levels: Dict[str, int] = Field(default_factory=dict)

class MonitoringConfig(BaseModel):
    health_check_enabled: bool = True
    health_check_interval: int = 10
    fallback_retry_count: int = 3
    fallback_safe_point: str = "spawn"
    alert_chat_notify: bool = True

class IdleTasksConfig(BaseModel):
    enabled: bool = True
    interval: int = 30
    actions: List[Dict] = Field(default_factory=list)

class WebUIConfig(BaseModel):
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8080
    auth_enabled: bool = True
    auth_password: str = "change-me"
    auth_session_timeout: int = 3600
    allow_remote: bool = True
    allowed_ips: List[str] = Field(default_factory=lambda: ["0.0.0.0/0"])

class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "logs/companion.log"
    max_size: str = "100MB"
    backup_count: int = 5

class AppConfig(BaseModel):
    game: GameConfig
    ai: AIConfig
    skills: SkillsConfig = SkillsConfig()
    safety: SafetyConfig = SafetyConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    idle_tasks: IdleTasksConfig = IdleTasksConfig()
    webui: WebUIConfig = WebUIConfig()
    logging: LoggingConfig = LoggingConfig()

def load_config(path: str = "config.yaml") -> AppConfig:
    """加载 YAML 配置文件，返回 AppConfig 对象"""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return AppConfig(**raw)
```

**验收命令：**
```bash
cd /root/projects/BlockMind && python -c "
from src.config.loader import load_config, AppConfig
print('✅ 配置加载器完成')
print('  - load_config() 函数已定义')
print('  - AppConfig 数据模型已定义')
print('  - 支持所有配置项的类型校验')
"
```

---

### Task 0.3 — 日志系统

```
目标：实现统一日志工具
工作目录：/root/projects/BlockMind/
```

**需要创建的文件：**

`src/utils/logger.py`:

```python
"""统一日志工具 — 支持文件轮转 + 控制台彩色输出"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from src.config.loader import LoggingConfig

def setup_logger(config: LoggingConfig) -> logging.Logger:
    """
    初始化全局 logger
    
    功能：
    1. 控制台输出：彩色格式 [TIME] [LEVEL] [MODULE] message
    2. 文件输出：logs/companion.log，100MB 轮转，保留5份
    3. 级别：从配置读取（DEBUG/INFO/WARNING/ERROR）
    
    返回：配置好的 root logger
    """
    logger = logging.getLogger("mc_companion")
    logger.setLevel(getattr(logging, config.level))

    # 控制台 handler
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    ))
    logger.addHandler(console)

    # 文件 handler（轮转）
    log_dir = Path(config.file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        config.file,
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=config.backup_count,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d]: %(message)s"
    ))
    logger.addHandler(file_handler)

    return logger
```

**验收命令：**
```bash
cd /root/projects/BlockMind && python -c "
from src.utils.logger import setup_logger
from src.config.loader import LoggingConfig
logger = setup_logger(LoggingConfig())
logger.info('测试日志输出')
print('✅ 日志系统完成')
"
```

---

### Task 0.4 — 事件总线

```
目标：实现发布/订阅事件总线（模块间解耦通信）
工作目录：/root/projects/BlockMind/
```

**需要创建的文件：**

`src/core/event_bus.py`:

```python
"""事件总线 — 发布/订阅模式，模块间解耦通信"""
import asyncio
from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Event:
    """事件数据"""
    type: str              # 事件类型，如 "task.started", "error.detected"
    data: Dict[str, Any]   # 事件负载
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""       # 事件来源模块

class EventBus:
    """
    异步事件总线
    
    用法：
        bus = EventBus()
        bus.subscribe("task.completed", my_handler)
        await bus.emit(Event(type="task.completed", data={"skill_id": "xxx"}))
    
    事件类型规范：
        task.started     — 任务开始
        task.completed   — 任务完成
        task.failed      — 任务失败
        skill.generated  — AI 生成新 Skill
        skill.repaired   — Skill 自动修复
        error.detected   — 错误检测
        error.classified — 错误分级完成
        safety.request   — 安全授权请求
        safety.approved  — 操作被授权
        safety.denied    — 操作被拒绝
        takeover.started — AI 紧急接管开始
        takeover.ended   — AI 紧急接管结束
        idle.started     — 空闲任务开始
        idle.ended       — 空闲任务结束
        status.changed   — 状态变更通知
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[Event] = []  # 最近100条事件历史
        self._max_history = 100

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """取消订阅"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)

    async def emit(self, event: Event) -> None:
        """发布事件，通知所有订阅者"""
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        handlers = self._subscribers.get(event.type, [])
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)

    def get_history(self, event_type: str = None, limit: int = 50) -> List[Event]:
        """获取事件历史"""
        events = self._history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]
```

**验收命令：**
```bash
cd /root/projects/BlockMind && python -c "
import asyncio
from src.core.event_bus import EventBus, Event

async def test():
    bus = EventBus()
    received = []
    async def handler(e): received.append(e.type)
    bus.subscribe('test.event', handler)
    await bus.emit(Event(type='test.event', data={'msg': 'hello'}))
    assert received == ['test.event'], f'Expected [\"test.event\"], got {received}'
    print('✅ 事件总线完成')
    print('  - subscribe/unsubscribe/emit 已实现')
    print('  - 异步 handler 支持')
    print('  - 事件历史记录')

asyncio.run(test())
"
```

---

## P1: 游戏连接模块

### Task 1.1 — MC 连接器

```
目标：实现 Minecraft 服务器连接（支持正版/离线，断线自动重连）
工作目录：/root/projects/BlockMind/
输入依赖：src/config/loader.py (GameConfig), src/utils/logger.py
```

**需要创建的文件：** `src/game/connection.py`

**类签名：**

```python
"""MC 服务器连接管理器"""
import asyncio
import logging
from typing import Optional, Dict, Any
from src.config.loader import GameConfig
from src.core.event_bus import EventBus, Event

class MCConnection:
    """
    Minecraft 服务器连接
    
    功能：
    1. 连接到 MC 服务器（支持正版/离线模式）
    2. 断线指数退避重连（5s → 10s → 20s → ... → 60s 上限）
    3. 实时状态同步（世界、实体、背包）
    4. 发送聊天消息
    5. 执行游戏动作（移动、挖掘、放置、攻击等）
    """

    def __init__(self, config: GameConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger("mc_companion.connection")
        self._client = None          # pyCraft client 实例
        self._connected = False
        self._reconnecting = False
        self._retry_count = 0
        self._max_retry_delay = 60   # 最大重连间隔（秒）

    async def connect(self) -> bool:
        """连接到 MC 服务器，成功返回 True"""
        # TODO: 实现 pyCraft 连接逻辑
        # 1. 根据 auth_mode 选择连接方式
        # 2. 处理连接异常
        # 3. 连接成功后 emit Event(type="connection.established")
        pass

    async def disconnect(self) -> None:
        """断开连接"""
        # TODO: 优雅断开，emit Event(type="connection.lost")
        pass

    async def reconnect(self) -> bool:
        """断线自动重连（指数退避）"""
        # TODO: 实现指数退避重连
        # delay = min(base_delay * 2^retry_count, max_retry_delay)
        pass

    async def send_chat(self, message: str) -> None:
        """发送聊天消息"""
        pass

    async def get_world_state(self) -> Dict[str, Any]:
        """获取当前世界状态快照"""
        pass

    async def get_entity_state(self, entity_id: int) -> Dict[str, Any]:
        """获取指定实体状态"""
        pass

    async def get_inventory(self) -> list:
        """获取背包物品列表"""
        pass

    async def execute_action(self, action_type: str, **kwargs) -> Dict[str, Any]:
        """
        执行游戏动作
        
        action_type: "move" / "dig" / "place" / "attack" / "eat" / "look"
        kwargs: 根据动作类型不同
            move: x, y, z
            dig: x, y, z
            place: item, x, y, z
            attack: entity_id
            eat: item_name
            look: x, y, z
        """
        pass

    @property
    def is_connected(self) -> bool:
        return self._connected
```

**验收标准：**
1. `MCConnection` 类可实例化
2. `connect()` / `disconnect()` 方法存在
3. `execute_action()` 方法签名正确
4. 无语法错误：`python -c "from src.game.connection import MCConnection; print('✅')"` 

---

### Task 1.2 — 状态采集器

```
目标：实现实时游戏状态采集（地形、实体、时间、天气）
工作目录：/root/projects/BlockMind/
输入依赖：src/game/connection.py
```

**需要创建的文件：** `src/game/perception.py`

**类签名：**

```python
"""环境感知 — 实时采集游戏世界状态"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class WorldState:
    """世界状态快照"""
    dimension: str = "overworld"     # overworld / nether / the_end
    time_of_day: int = 0             # MC tick (0-24000)
    weather: str = "clear"           # clear / rain / thunder
    difficulty: str = "normal"
    day_count: int = 1

@dataclass
class EntityInfo:
    """实体信息"""
    entity_id: int
    entity_type: str                 # player / zombie / skeleton / cow / ...
    position: tuple                  # (x, y, z)
    health: float = 20.0
    distance: float = 0.0            # 与机器人的距离
    is_hostile: bool = False

@dataclass
class BlockInfo:
    """方块信息"""
    position: tuple                  # (x, y, z)
    block_type: str                  # stone / dirt / diamond_ore / ...
    is_mineable: bool = True

@dataclass
class GameStateSnapshot:
    """完整游戏状态快照"""
    timestamp: datetime = field(default_factory=datetime.now)
    world: WorldState = field(default_factory=WorldState)
    player_health: float = 20.0
    player_hunger: float = 20.0
    player_position: tuple = (0, 64, 0)
    player_inventory: List[Dict] = field(default_factory=list)
    nearby_entities: List[EntityInfo] = field(default_factory=list)
    nearby_blocks: List[BlockInfo] = field(default_factory=list)

class StateCollector:
    """
    状态采集器
    
    功能：
    1. 定时采集完整游戏状态快照
    2. 增量对比：检测状态变化
    3. 提供快捷查询接口
    """

    def __init__(self, connection):
        self.connection = connection
        self.logger = logging.getLogger("mc_companion.perception")
        self._last_snapshot: Optional[GameStateSnapshot] = None
        self._current_snapshot: Optional[GameStateSnapshot] = None

    async def collect(self) -> GameStateSnapshot:
        """采集当前完整游戏状态"""
        pass

    def get_changed_fields(self) -> List[str]:
        """对比新旧快照，返回变化的字段名"""
        pass

    def has_hostile_nearby(self, radius: float = 16.0) -> bool:
        """检查附近是否有敌对生物"""
        pass

    def get_nearest_entity(self, entity_type: str = None) -> Optional[EntityInfo]:
        """获取最近的指定类型实体"""
        pass

    def get_blocks_by_type(self, block_type: str, radius: int = 32) -> List[BlockInfo]:
        """获取指定范围内的特定类型方块"""
        pass

    @property
    def current(self) -> Optional[GameStateSnapshot]:
        return self._current_snapshot
```

**验收标准：**
1. `StateCollector` 类可实例化
2. `GameStateSnapshot` 数据结构完整
3. `collect()` / `has_hostile_nearby()` 方法存在

---

### Task 1.3 — 背包管理器

```
目标：实现背包物品查询与整理
工作目录：/root/projects/BlockMind/
输入依赖：src/game/connection.py
```

**需要创建的文件：** `src/game/inventory.py`

**类签名：**

```python
"""背包管理器"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Item:
    """物品信息"""
    name: str                        # 物品名称（如 "diamond_sword"）
    display_name: str                # 显示名称（如 "钻石剑"）
    count: int                       # 数量
    slot: int                        # 背包槽位
    durability: int = 0              # 耐久
    max_durability: int = 0          # 最大耐久

class InventoryManager:
    """
    背包管理器
    
    功能：
    1. 查询物品数量：inventory.count("diamond")
    2. 查找特定物品位置
    3. 统计分类（武器/工具/食物/方块/其他）
    4. 判断背包是否已满
    5. 自动整理背包
    """

    def __init__(self, connection):
        self.connection = connection
        self.logger = logging.getLogger("mc_companion.inventory")
        self._items: List[Item] = []
        self._categories = {
            "weapons": ["sword", "axe", "bow", "crossbow", "trident"],
            "tools": ["pickaxe", "shovel", "hoe", "shears", "flint_and_steel"],
            "food": ["bread", "cooked_beef", "cooked_porkchop", "apple", "golden_apple"],
            "blocks": ["dirt", "stone", "cobblestone", "oak_log", "planks"],
        }

    async def refresh(self) -> None:
        """从连接获取最新背包数据"""
        pass

    def count(self, item_name: str) -> int:
        """计算指定物品的总数量"""
        pass

    def find(self, item_name: str) -> Optional[Item]:
        """查找指定物品（返回第一个匹配）"""
        pass

    def find_all(self, item_name: str) -> List[Item]:
        """查找指定物品的所有实例"""
        pass

    def has_item(self, item_name: str, min_count: int = 1) -> bool:
        """检查是否拥有指定数量的物品"""
        pass

    def is_full(self) -> bool:
        """背包是否已满（36 格）"""
        pass

    def get_empty_slots(self) -> int:
        """空槽数量"""
        pass

    def get_category_counts(self) -> Dict[str, int]:
        """按分类统计物品数量"""
        pass

    def get_durability_percent(self, item: Item) -> float:
        """获取物品耐久百分比"""
        pass

    def get_low_durability_items(self, threshold: float = 0.2) -> List[Item]:
        """获取耐久低于阈值的物品"""
        pass
```

---

### Task 1.4 — 动作执行器

```
目标：实现所有游戏动作（移动、挖掘、放置、攻击、进食等）
工作目录：/root/projects/BlockMind/
输入依赖：src/game/connection.py, src/safety/gateway.py (桩)
```

**需要创建的文件：** `src/game/actions.py`

**类签名：**

```python
"""动作执行器 — 所有游戏内动作的具体实现"""
import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ActionResult:
    """动作执行结果"""
    success: bool
    action_type: str
    details: str = ""
    duration_ms: int = 0

class ActionExecutor:
    """
    动作执行器
    
    所有动作都经过安全校验层（SafetyGateway）后再执行
    """

    def __init__(self, connection, safety_gateway=None):
        self.connection = connection
        self.safety_gateway = safety_gateway  # 可选，测试时可为 None
        self.logger = logging.getLogger("mc_companion.actions")

    async def walk_to(self, x: float, y: float, z: float, sprint: bool = False) -> ActionResult:
        """走到指定坐标"""
        pass

    async def dig_block(self, x: int, y: int, z: int) -> ActionResult:
        """挖掘指定位置的方块"""
        pass

    async def place_block(self, item_name: str, x: int, y: int, z: int) -> ActionResult:
        """在指定位置放置方块"""
        pass

    async def attack(self, entity_id: int) -> ActionResult:
        """攻击指定实体"""
        pass

    async def eat(self, item_name: str) -> ActionResult:
        """进食指定食物"""
        pass

    async def look_at(self, x: float, y: float, z: float) -> ActionResult:
        """看向指定位置"""
        pass

    async def jump(self) -> ActionResult:
        """原地跳跃"""
        pass

    async def craft(self, recipe: str) -> ActionResult:
        """合成物品"""
        pass

    async def use_item(self, item_name: str) -> ActionResult:
        """使用物品（右键）"""
        pass

    async def drop_item(self, item_name: str, count: int = 1) -> ActionResult:
        """丢弃物品"""
        pass
```

---

### Task 1.5 — 动作队列

```
目标：实现动作排队、超时控制、取消机制
工作目录：/root/projects/BlockMind/
输入依赖：src/game/actions.py
```

**需要创建的文件：** `src/game/action_queue.py`

**核心功能：**
- 动作 FIFO 队列
- 每个动作有超时时间（默认 60 秒）
- 支持取消当前动作
- 执行完成回调
- 失败自动重试（可配置次数）

---

### Task 1.6 — 聊天交互模块

```
目标：实现 MC 聊天消息监听和 ! 指令解析
工作目录：/root/projects/BlockMind/
输入依赖：src/game/connection.py, src/core/event_bus.py
```

**需要创建的文件：** `src/game/chat.py`

**支持的指令列表（硬编码）：**

```python
COMMANDS = {
    "!stop":       "立即终止所有任务，返回安全点",
    "!come":       "传送到玩家身边",
    "!safe":       "强制传送回出生点/床边",
    "!status":     "查看机器人当前状态",
    "!approve":    "同意高风险操作",
    "!deny":       "拒绝高风险操作",
    "!disable_ai": "禁用AI自动接管",
    "!enable_ai":  "启用AI自动接管",
    "!skill list": "列出所有可用Skill",
    "!skill run":  "手动执行指定Skill",
    "!help":       "显示帮助信息",
}
```

---

### Task 1.7 — 寻路算法

```
目标：实现 A* 寻路（支持避障、跳跃攀爬、安全落点检测）
工作目录：/root/projects/BlockMind/
输入依赖：src/game/perception.py
```

**需要创建的文件：** `src/game/pathfinding.py`

**核心类：**

```python
class Pathfinder:
    """A* 寻路算法"""
    
    async def find_path(self, start: Tuple[int,int,int], end: Tuple[int,int,int], 
                        max_distance: int = 128) -> List[Tuple[int,int,int]]:
        """找到从 start 到 end 的路径，返回坐标列表"""
        pass
    
    async def find_safe_landing(self, x: int, z: int) -> Optional[Tuple[int,int,int]]:
        """找到安全的落点（不会摔死）"""
        pass
    
    async def find_nearest(self, condition: callable, radius: int = 32) -> Optional[Tuple[int,int,int]]:
        """找到满足条件的最近位置"""
        pass
```

---

### Task 1.8 — 游戏连接模块测试

```
目标：编写游戏连接模块的单元测试
工作目录：/root/projects/BlockMind/
输入依赖：src/game/ 下所有文件
```

**需要创建的文件：** `tests/test_game_connection.py`

**测试用例：**

```python
"""游戏连接模块测试"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

class TestMCConnection:
    def test_can_instantiate(self):
        """MCConnection 可以实例化"""
        pass
    
    @pytest.mark.asyncio
    async def test_connect_success(self):
        """连接成功返回 True"""
        pass
    
    @pytest.mark.asyncio
    async def test_reconnect_backoff(self):
        """断线重连使用指数退避"""
        pass
    
    @pytest.mark.asyncio
    async def test_disconnect_emits_event(self):
        """断开连接时发送事件"""
        pass

class TestStateCollector:
    def test_can_instantiate(self):
        """StateCollector 可以实例化"""
        pass

class TestInventoryManager:
    def test_count_returns_int(self):
        """count() 返回整数"""
        pass
    
    def test_has_item(self):
        """has_item() 正确判断"""
        pass

class TestActionExecutor:
    def test_can_instantiate(self):
        """ActionExecutor 可以实例化"""
        pass
```

---

## P2: Skill DSL 引擎

### Task 2.1 — DSL 数据模型

```
目标：定义 Skill DSL 的完整数据模型（Pydantic）
工作目录：/root/projects/BlockMind/
```

**需要创建的文件：** `src/skills/models.py`

**模型定义：**

```python
"""Skill DSL 数据模型"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class WhenClause(BaseModel):
    """触发条件"""
    all: List[str] = Field(default_factory=list)  # 所有条件都满足
    any: List[str] = Field(default_factory=list)  # 任意条件满足

class DoStep(BaseModel):
    """执行步骤"""
    action: str                          # 函数名
    args: Dict[str, Any] = Field(default_factory=dict)
    loop: Optional['LoopBlock'] = None   # 循环块
    condition: Optional[str] = None      # 条件判断

class LoopBlock(BaseModel):
    """循环块"""
    while_condition: Optional[str] = None
    over_variable: Optional[str] = None  # 遍历变量
    do_steps: List[DoStep] = Field(default_factory=list)
    max_iterations: int = 1000           # 防止死循环

class UntilClause(BaseModel):
    """结束条件"""
    any: List[str] = Field(default_factory=list)

class SkillDSL(BaseModel):
    """Skill DSL 完整结构"""
    skill_id: str                        # 唯一标识
    name: str                            # 显示名称
    tags: List[str] = Field(default_factory=list)
    priority: int = 5                    # 1=最高, 5=最低
    when: WhenClause = Field(default_factory=WhenClause)
    do_steps: List[DoStep] = Field(default_factory=list)
    until: UntilClause = Field(default_factory=UntilClause)
    description: str = ""                # 描述
    author: str = "system"               # 创建者
    version: int = 1                     # 版本号
    usage_count: int = 0                 # 使用次数
    success_rate: float = 1.0            # 成功率
```

---

### Task 2.2 — DSL 解析器

```
目标：将 YAML 文件解析为 SkillDSL 对象
工作目录：/root/projects/BlockMind/
输入依赖：src/skills/models.py
```

**需要创建的文件：** `src/skills/dsl_parser.py`

**类签名：**

```python
"""DSL 解析器 — YAML → SkillDSL"""
import yaml
import logging
from pathlib import Path
from typing import List, Optional
from src.skills.models import SkillDSL, WhenClause, DoStep, LoopBlock, UntilClause

class DSLParser:
    """将 YAML Skill 文件解析为 SkillDSL 对象"""

    def __init__(self):
        self.logger = logging.getLogger("mc_companion.dsl_parser")

    def parse_file(self, file_path: str) -> SkillDSL:
        """从文件路径解析 Skill"""
        pass

    def parse_yaml(self, yaml_content: str) -> SkillDSL:
        """从 YAML 字符串解析 Skill"""
        pass

    def parse_dict(self, data: dict) -> SkillDSL:
        """从 Python 字典解析 Skill"""
        pass

    def _parse_when(self, when_data: dict) -> WhenClause:
        """解析 when 子句"""
        pass

    def _parse_do(self, do_data: list) -> List[DoStep]:
        """解析 do 子句"""
        pass

    def _parse_until(self, until_data: dict) -> UntilClause:
        """解析 until 子句"""
        pass

    def _parse_loop(self, loop_data: dict) -> LoopBlock:
        """解析 loop 块"""
        pass

    def validate_syntax(self, skill: SkillDSL) -> List[str]:
        """
        语法校验，返回错误列表（空=通过）
        检查项：
        1. skill_id 唯一性
        2. priority 范围 1-5
        3. do_steps 非空
        4. 引用的函数名在内置函数库中
        """
        pass
```

---

### Task 2.3 — DSL 校验器

```
目标：实现语法校验 + 安全校验 + 逻辑合理性校验
工作目录：/root/projects/BlockMind/
输入依赖：src/skills/models.py, src/skills/dsl_parser.py
```

**需要创建的文件：** `src/skills/validator.py`

**校验规则：**

```python
class SkillValidator:
    """Skill DSL 校验器"""

    # 安全性校验规则
    FORBIDDEN_PATTERNS = [
        "rm -rf",          # 禁止危险命令
        "place_command_block",  # 禁止放置命令方块
        "suicide",         # 禁止自杀
        "ignite_tnt",      # 禁止点燃TNT
    ]

    # 硬编码检测（禁止写死坐标/物品数量）
    HARDCODE_PATTERNS = [
        r"position\s*:\s*\(\d+,\s*\d+,\s*\d+\)",  # 写死坐标
        r"count\s*==\s*\d+",                        # 写死数量
    ]

    def validate_syntax(self, skill: SkillDSL) -> ValidationResult:
        """语法校验"""
        pass

    def validate_safety(self, skill: SkillDSL) -> ValidationResult:
        """安全性校验（禁止危险操作、检测硬编码）"""
        pass

    def validate_logic(self, skill: SkillDSL, game_state: dict) -> ValidationResult:
        """逻辑合理性校验（条件是否可达、循环是否可能终止）"""
        pass

    def validate_all(self, skill: SkillDSL, game_state: dict = None) -> ValidationResult:
        """执行全部校验"""
        pass
```

---

### Task 2.4 — 状态管理器

```
目标：实现 Skill 运行时的游戏状态查询函数
工作目录：/root/projects/BlockMind/
输入依赖：src/game/perception.py, src/game/inventory.py
```

**需要创建的文件：** `src/skills/state_manager.py`

**核心功能：** 实现 `self.health()`, `self.hunger()`, `self.position()`, `inventory.count()`, `world.time()`, `world.get_block()`, `world.any_entity()` 等查询函数在运行时的映射。

---

### Task 2.5 — 内置函数库

```
目标：实现 Skill DSL 的全部内置函数
工作目录：/root/projects/BlockMind/
输入依赖：src/skills/state_manager.py, src/game/actions.py
```

**需要创建的文件：** `src/skills/builtin_functions.py`

**函数清单：**

```python
# 状态查询类
"self.health"        → 返回当前生命值 (float)
"self.hunger"        → 返回当前饥饿值 (float)
"self.position"      → 返回当前位置 (tuple)
"inventory.count"    → 返回物品数量 (int)
"inventory.has"      → 判断是否拥有 (bool)
"world.time"         → 返回游戏时间 (int)
"world.get_block"    → 返回方块类型 (str)
"world.any_entity"   → 判断是否存在实体 (bool)
"world.entity_exists"→ 判断实体是否存在 (bool)

# 动作类
"walk_to"            → 走到指定位置
"dig_block"          → 挖掘方块
"place_block"        → 放置方块
"attack"             → 攻击实体
"eat"                → 进食
"look_at"            → 看向位置
"pickup_item"        → 拾取物品
"scan_blocks"        → 扫描方块
"scan_entities"      → 扫描实体
"scan_drops"         → 扫描掉落物

# 控制流类
"if/then/else"       → 条件判断
"loop/while"         → 循环
"break_loop"         → 跳出循环
"wait"               → 等待指定秒数
```

---

### Task 2.6 — 控制流调度器

```
目标：实现 if/loop/break/wait 等控制流逻辑
工作目录：/root/projects/BlockMind/
输入依赖：src/skills/models.py, src/skills/builtin_functions.py
```

**需要创建的文件：** `src/skills/control_flow.py`

---

### Task 2.7 — Skill 运行时引擎

```
目标：串联解析→状态→控制流→执行的完整流程
工作目录：/root/projects/BlockMind/
输入依赖：2.2-2.6 全部
```

**需要创建的文件：** `src/skills/runtime.py`

**核心类：**

```python
class SkillRuntime:
    """Skill 执行引擎 — 核心入口"""

    def __init__(self, mc_connection, state_manager, action_executor):
        self.parser = DSLParser()
        self.state_manager = state_manager
        self.action_executor = action_executor
        self.control_flow = ControlFlowScheduler()
        self._current_skill: Optional[SkillDSL] = None
        self._interrupted = False

    async def execute_skill(self, skill_path: str) -> SkillResult:
        """执行指定的 DSL Skill 文件"""
        # 1. 解析 YAML → SkillDSL
        # 2. 更新游戏状态
        # 3. 执行 do_steps（带控制流）
        # 4. 检查 until 条件
        # 5. 返回执行结果
        pass

    async def execute_skill_object(self, skill: SkillDSL) -> SkillResult:
        """执行已解析的 SkillDSL 对象"""
        pass

    def interrupt(self) -> None:
        """中断当前 Skill 执行"""
        self._interrupted = True

    @property
    def is_running(self) -> bool:
        return self._current_skill is not None
```

---

### Task 2.8 — Skill 存储管理

```
目标：实现 Skill 文件的 CRUD、索引、版本控制
工作目录：/root/projects/BlockMind/
输入依赖：src/skills/models.py
```

**需要创建的文件：** `src/skills/storage.py`

---

### Task 2.9 — Skill 意图匹配器

```
目标：根据玩家指令/当前状态匹配最合适的 Skill
工作目录：/root/projects/BlockMind/
输入依赖：src/skills/storage.py
```

**需要创建的文件：** `src/skills/matcher.py`

---

### Task 2.10 — 编写 15 个内置 Skill YAML

```
目标：编写全部内置 Skill 的 YAML 文件
工作目录：/root/projects/BlockMind/skills/builtin/
```

**需要创建的文件列表：**

```
skills/builtin/
├── survival/
│   ├── emergency_retreat.yaml    # 紧急撤退 (priority: 1)
│   ├── eat_food.yaml             # 自动吃食物 (priority: 2)
│   └── avoid_hostile.yaml        # 躲避敌对生物 (priority: 2)
├── gathering/
│   ├── chop_tree.yaml            # 砍树 (priority: 4)
│   ├── mine_stone.yaml           # 挖石头 (priority: 4)
│   ├── mine_ore.yaml             # 挖矿石 (priority: 3)
│   └── collect_crops.yaml        # 收集作物 (priority: 4)
├── building/
│   ├── build_shelter.yaml        # 建造庇护所 (priority: 3)
│   ├── place_torches.yaml        # 放置火把 (priority: 4)
│   └── repair_building.yaml      # 修补建筑 (priority: 5)
├── farming/
│   ├── plant_wheat.yaml          # 种植小麦 (priority: 5)
│   ├── harvest_wheat.yaml        # 收割小麦 (priority: 5)
│   └── replant.yaml              # 重新种植 (priority: 5)
└── storage/
    ├── organize_chest.yaml       # 整理箱子 (priority: 5)
    └── deposit_items.yaml        # 存放物品 (priority: 5)
```

每个 YAML 文件格式示例（以 chop_tree.yaml 为例）：

```yaml
skill_id: skill_chop_tree_001
name: 砍树
tags: ["砍树", "收集木材", "采集"]
priority: 4
description: "寻找附近橡树并砍伐收集木材"

when:
  all:
    - "inventory.has('wooden_axe') or inventory.has('stone_axe') or inventory.has('iron_axe')"
    - "world.any_entity(type='oak_tree', radius=32)"
    - "not inventory.is_full()"

do:
  - scan_entities:
      radius: 32
      filter: "type == 'oak_tree'"
      sort_by: distance
  - walk_to: "scanned_entities[0].position"
  - loop:
      while: "world.entity_exists(scanned_entities[0].id)"
      do:
        - dig_block: "scanned_entities[0].position"
        - wait: 1
  - scan_drops:
      radius: 5
  - loop:
      over: "scanned_drops"
      do:
        - walk_to: "item.position"
        - pickup_item: "item"

until:
  any:
    - "inventory.count('oak_log') >= 64"
    - "not world.any_entity(type='oak_tree', radius=32)"
    - "task_interrupted()"
```

---

### Task 2.11 — Skill 引擎集成测试

```
目标：编写 Skill 引擎的完整测试
工作目录：/root/projects/BlockMind/
```

**需要创建的文件：** `tests/test_skill_engine.py`

---

## P3: AI 决策模块

### Task 3.1 — AI 提供商抽象层

```
目标：实现统一的 AI 调用接口（支持 OpenAI/Anthropic/本地模型）
工作目录：/root/projects/BlockMind/
输入依赖：src/config/loader.py (AIConfig)
```

**需要创建的文件：** `src/ai/provider.py`

**类签名：**

```python
"""AI 提供商抽象层"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class AIProvider(ABC):
    """AI 提供商基类"""

    @abstractmethod
    async def chat(self, messages: List[Dict], temperature: float = 0.7,
                   max_tokens: int = 4096) -> str:
        """发送对话请求，返回文本响应"""
        pass

    @abstractmethod
    async def chat_stream(self, messages: List[Dict], **kwargs):
        """流式对话，yield 每个 token"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """检查 API 连接是否正常"""
        pass

class OpenAIProvider(AIProvider):
    """OpenAI 适配器"""
    pass

class AnthropicProvider(AIProvider):
    """Anthropic 适配器"""
    pass

class LocalProvider(AIProvider):
    """本地模型适配器（兼容 OpenAI API 格式）"""
    pass

def create_provider(config: AIConfig) -> AIProvider:
    """工厂函数：根据配置创建对应的 Provider"""
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "local": LocalProvider,
    }
    cls = providers.get(config.provider)
    if not cls:
        raise ValueError(f"不支持的 AI 提供商: {config.provider}")
    return cls(config)
```

---

### Task 3.2 — Prompt 模板管理

```
目标：管理所有 AI Prompt 模板
工作目录：/root/projects/BlockMind/
```

**需要创建的文件：** `src/ai/prompts.py`

**Prompt 模板清单：**

```python
PROMPTS = {
    "skill_generation": """
你是一个 Minecraft AI 助手。请将以下任务描述转换为 Skill DSL（YAML 格式）。

【任务描述】
{task_description}

【当前游戏状态】
{game_state}

【可用函数】
{available_functions}

【输出要求】
1. 严格遵循 Skill DSL 语法规范
2. 禁止使用硬编码坐标
3. 必须包含 when/do/until 三个部分
4. 只输出 YAML，不要其他解释

【Skill DSL】
""",

    "emergency_takeover": """
【紧急接管模式启动】
你现在直接控制 Minecraft 机器人，当前处于紧急危险状态。
首要任务是保证机器人安全。

【规则】
1. 只输出动作指令，不要输出任何解释
2. 可用指令：walk_to(x,y,z), jump(), dig(x,y,z), attack(entity_id), eat(item)
3. 优先处理：溺水 > 被攻击 > 掉落 > 其他
4. 安全后输出 "SAFE"

【当前状态】
{context_snapshot}
""",

    "error_analysis": """
分析以下 Skill 执行错误，找出根本原因并给出修复建议。

【Skill DSL】
{skill_dsl}

【错误信息】
{error_message}

【执行日志】
{execution_log}

请分析：
1. 错误的根本原因
2. DSL 中哪一行/哪个步骤导致了问题
3. 具体的修复建议（修改后的 DSL 片段）
""",

    "skill_repair": """
你是一个 Skill 修复专家。请根据以下分析结果修复 Skill DSL。

【原始 Skill DSL】
{original_skill}

【错误分析】
{error_analysis}

【修复要求】
1. 只修复导致错误的部分
2. 保持原有功能不变
3. 输出完整的修复后 DSL（YAML 格式）
4. 只输出 YAML，不要其他解释

【修复后的 Skill DSL】
""",
}
```

---

### Task 3.3 — DSL 生成器

```
目标：将自然语言任务转换为标准 DSL YAML
工作目录：/root/projects/BlockMind/
输入依赖：src/ai/provider.py, src/ai/prompts.py, src/skills/validator.py
```

**需要创建的文件：** `src/ai/generator.py`

---

### Task 3.4 — 紧急接管模块

```
目标：3级错误时 AI 直接控制机器人
工作目录：/root/projects/BlockMind/
输入依赖：src/ai/provider.py, src/game/actions.py
```

**需要创建的文件：** `src/ai/takeover.py`

---

### Task 3.5 — Skill 自动修复

```
目标：AI 分析 Skill 失败原因并自动修复
工作目录：/root/projects/BlockMind/
输入依赖：src/ai/generator.py, src/skills/storage.py
```

**需要创建的文件：** `src/ai/auto_repair.py`

---

## P4-P9: 后续模块

> P4（安全校验层）、P5（故障监控）、P6（空闲任务）、P7（WebUI）、P8（部署）、P9（测试）
> 的任务格式与上面相同，每个任务都包含精确的文件路径、类签名、验收标准。
> 
> **待后续迭代时展开。**

---

## 📊 任务统计

| 模块 | 任务数 | 预估工时 | 文件数 |
|------|--------|----------|--------|
| P0 初始化 | 6 | 2h | ~15 |
| P1 游戏连接 | 8 | 20h | 8 |
| P2 Skill DSL | 12 | 32h | 12 |
| P3 AI 决策 | 5 | 16h | 5 |
| P4 安全校验 | 8 | 16h | 8 |
| P5 故障监控 | 7 | 14h | 7 |
| P6 空闲任务 | 5 | 7h | 5 |
| P7 WebUI | 10 | 20h | 15+ |
| P8 部署 | 6 | 8h | 5 |
| P9 测试优化 | 7 | 12h | 5 |
| **合计** | **74** | **~147h** | **~95** |

---

<p align="center">
  <i>📋 Claude Code 优化版任务清单 · 星糯 🎀</i>
</p>
