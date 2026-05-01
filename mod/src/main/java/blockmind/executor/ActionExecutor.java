package blockmind.executor;

import blockmind.bot.BotManager;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.MinecraftServer;
import net.minecraft.text.Text;
import net.minecraft.util.math.BlockPos;

/**
 * 游戏动作执行器
 * 接收 JSON 参数，执行游戏内动作
 * 优先使用 Bot（如果已 spawn），否则回退到第一个在线玩家
 */
public class ActionExecutor {

    private static MinecraftServer server;

    public static void setServer(MinecraftServer srv) {
        server = srv;
    }

    /**
     * 获取目标玩家：优先 Bot，回退到第一个在线玩家
     */
    private static ServerPlayerEntity getTarget() {
        // 优先使用 Bot
        if (BotManager.isSpawned()) {
            ServerPlayerEntity bot = BotManager.getBot();
            if (bot != null && bot.isAlive()) {
                return bot;
            }
        }
        // 回退到第一个在线玩家
        if (server == null) return null;
        var players = server.getPlayerManager().getPlayerList();
        return players.isEmpty() ? null : players.get(0);
    }

    /**
     * 移动到指定位置
     * Body: {"x": 128, "y": 64, "z": -256, "sprint": false}
     */
    public static JsonObject move(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity target = getTarget();
        if (target == null) return error("No player or bot available");

        double x = json.get("x").getAsDouble();
        double y = json.get("y").getAsDouble();
        double z = json.get("z").getAsDouble();

        // 传送到目标位置（BotPlayer 用 setPos 避免 NPE）
        if (target instanceof blockmind.bot.BotPlayer) {
            target.setPos(x, y, z);
        } else {
            target.teleport(x, y, z);
        }

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        result.addProperty("details", String.format("移动到 (%.1f, %.1f, %.1f)", x, y, z));
        return result;
    }

    /**
     * 挖掘方块
     * Body: {"x": 128, "y": 63, "z": -256}
     */
    public static JsonObject dig(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity target = getTarget();
        if (target == null) return error("No player or bot available");

        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

        BlockPos pos = new BlockPos(x, y, z);
        String blockType = target.getWorld().getBlockState(pos).getBlock().toString();

        // 破坏方块
        target.getWorld().breakBlock(pos, true, target);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        result.addProperty("details", String.format("挖掘 %s at (%d, %d, %d)", blockType, x, y, z));
        return result;
    }

    /**
     * 放置方块
     * Body: {"item": "torch", "x": 128, "y": 64, "z": -256}
     */
    public static JsonObject place(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity target = getTarget();
        if (target == null) return error("No player or bot available");

        String item = json.get("item").getAsString();
        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

        BlockPos pos = new BlockPos(x, y, z);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        result.addProperty("details", String.format("放置 %s at (%d, %d, %d)", item, x, y, z));
        return result;
    }

    /**
     * 攻击实体
     * Body: {"entity_id": 123}
     */
    public static JsonObject attack(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity target = getTarget();
        if (target == null) return error("No player or bot available");

        int entityId = json.get("entity_id").getAsInt();

        var entity = target.getWorld().getEntityById(entityId);
        if (entity == null) return error("Entity not found");

        String entityType = entity.getType().toString();
        target.attack(entity);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        result.addProperty("details", String.format("攻击 %s (ID: %d)", entityType, entityId));
        return result;
    }

    /**
     * 进食
     * Body: {"item": "bread"}
     */
    public static JsonObject eat(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity target = getTarget();
        if (target == null) return error("No player or bot available");

        String item = json.get("item").getAsString();

        // 恢复饥饿值
        target.getHungerManager().add(5, 0.5f);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        result.addProperty("details", String.format("进食 %s，恢复饥饿值", item));
        return result;
    }

    /**
     * 看向位置
     * Body: {"x": 130, "y": 65, "z": -258}
     */
    public static JsonObject look(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity target = getTarget();
        if (target == null) return error("No player or bot available");

        double x = json.get("x").getAsDouble();
        double y = json.get("y").getAsDouble();
        double z = json.get("z").getAsDouble();

        // 计算朝向
        double dx = x - target.getX();
        double dy = y - target.getY();
        double dz = z - target.getZ();
        double horizontalDist = Math.sqrt(dx * dx + dz * dz);
        float yaw = (float) Math.toDegrees(Math.atan2(-dx, dz));
        float pitch = (float) Math.toDegrees(Math.atan2(-dy, horizontalDist));

        target.setYaw(yaw);
        target.setPitch(pitch);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        result.addProperty("details", String.format("看向 (%.1f, %.1f, %.1f)", x, y, z));
        return result;
    }

    /**
     * 发送聊天消息
     * Body: {"message": "Hello!"}
     */
    public static JsonObject chat(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity target = getTarget();
        if (target == null) return error("No player or bot available");

        String message = json.get("message").getAsString();

        // 发送聊天消息到服务器广播
        Text text = Text.literal("[" + target.getName().getString() + "] " + message);
        server.getPlayerManager().broadcast(text, false);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        result.addProperty("details", String.format("发送消息: %s", message));
        return result;
    }

    // ─── 辅助方法 ─────────────────────────────────────

    private static JsonObject parseBody(String body) {
        try {
            return JsonParser.parseString(body).getAsJsonObject();
        } catch (Exception e) {
            return null;
        }
    }

    private static JsonObject error(String message) {
        JsonObject json = new JsonObject();
        json.addProperty("success", false);
        json.addProperty("error", message);
        return json;
    }
}
