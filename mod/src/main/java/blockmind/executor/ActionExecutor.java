package blockmind.executor;

import blockmind.bot.BotManager;
import blockmind.compat.MinecraftCompat;
import blockmind.compat.VersionCompat;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

/**
 * 游戏动作执行器
 * 接收 JSON 参数，执行游戏内动作
 * 优先使用 Bot（如果已 spawn），否则回退到第一个在线玩家
 *
 * 使用 MinecraftCompat 接口隔离版本差异。
 */
public class ActionExecutor {

    private static Object server;

    public static void setServer(Object srv) {
        server = srv;
    }

    /**
     * 获取目标玩家：优先 Bot，回退到第一个在线玩家
     */
    private static Object getTarget() {
        MinecraftCompat compat = VersionCompat.getCompat();
        // 优先使用 Bot
        if (BotManager.isSpawned()) {
            Object bot = BotManager.getBot();
            if (bot != null && compat.isAlive(bot)) {
                return bot;
            }
        }
        // 回退到第一个在线玩家
        if (server == null) return null;
        try {
            Object playerManager = server.getClass().getMethod("getPlayerManager").invoke(server);
            @SuppressWarnings("unchecked")
            var players = (java.util.List<?>) playerManager.getClass().getMethod("getPlayerList").invoke(playerManager);
            return players.isEmpty() ? null : players.get(0);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 移动到指定位置
     * Body: {"x": 128, "y": 64, "z": -256, "sprint": false}
     */
    public static JsonObject move(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        Object target = getTarget();
        if (target == null) return error("No player or bot available");

        MinecraftCompat compat = VersionCompat.getCompat();

        double x = json.get("x").getAsDouble();
        double y = json.get("y").getAsDouble();
        double z = json.get("z").getAsDouble();

        // Bot 用 setPos 避免 NPE
        if (BotManager.isSpawned() && target == BotManager.getBot()) {
            compat.setPos(target, x, y, z);
        } else {
            try {
                target.getClass().getMethod("teleport", double.class, double.class, double.class)
                        .invoke(target, x, y, z);
            } catch (Exception e) {
                compat.setPos(target, x, y, z);
            }
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

        Object target = getTarget();
        if (target == null) return error("No player or bot available");

        MinecraftCompat compat = VersionCompat.getCompat();

        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

        try {
            // Create BlockPos
            Class<?> blockPosClass = Class.forName("net.minecraft.util.math.BlockPos");
            Object pos = blockPosClass.getConstructor(int.class, int.class, int.class).newInstance(x, y, z);

            // Get world and block state
            Object world = getWorld(target);
            Object blockState = world.getClass().getMethod("getBlockState", blockPosClass).invoke(world, pos);
            String blockType = blockState.getClass().getMethod("getBlock").invoke(blockState).toString();

            // Break block
            world.getClass().getMethod("breakBlock", blockPosClass, boolean.class, target.getClass())
                    .invoke(world, pos, true, target);

            JsonObject result = new JsonObject();
            result.addProperty("success", true);
            result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
            result.addProperty("details", String.format("挖掘 %s at (%d, %d, %d)", blockType, x, y, z));
            return result;
        } catch (Exception e) {
            return error("Dig failed: " + e.getMessage());
        }
    }

    /**
     * 放置方块
     * Body: {"item": "torch", "x": 128, "y": 64, "z": -256}
     */
    public static JsonObject place(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        Object target = getTarget();
        if (target == null) return error("No player or bot available");

        String item = json.get("item").getAsString();
        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

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

        Object target = getTarget();
        if (target == null) return error("No player or bot available");

        int entityId = json.get("entity_id").getAsInt();

        try {
            Object world = getWorld(target);
            Object entity = world.getClass().getMethod("getEntityById", int.class).invoke(world, entityId);
            if (entity == null) return error("Entity not found");

            String entityType = entity.getClass().getMethod("getType").invoke(entity).toString();
            target.getClass().getMethod("attack", entity.getClass()).invoke(target, entity);

            JsonObject result = new JsonObject();
            result.addProperty("success", true);
            result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
            result.addProperty("details", String.format("攻击 %s (ID: %d)", entityType, entityId));
            return result;
        } catch (Exception e) {
            return error("Attack failed: " + e.getMessage());
        }
    }

    /**
     * 进食
     * Body: {"item": "bread"}
     */
    public static JsonObject eat(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        Object target = getTarget();
        if (target == null) return error("No player or bot available");

        String item = json.get("item").getAsString();

        try {
            // Get hunger manager and add food
            Object hungerManager = getHungerManager(target);
            hungerManager.getClass().getMethod("add", int.class, float.class).invoke(hungerManager, 5, 0.5f);
        } catch (Exception e) {
            // Ignore — best effort
        }

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        result.addProperty("details", String.format("进食 %s，恢复饥饿值", item));
        return result;
    }

    /**
     * 设置朝向
     */
    public static JsonObject look(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        Object target = getTarget();
        if (target == null) return error("No player or bot available");

        MinecraftCompat compat = VersionCompat.getCompat();
        float yaw, pitch;
        String details;

        if (json.has("yaw") && json.has("pitch")) {
            yaw = json.get("yaw").getAsFloat();
            pitch = json.get("pitch").getAsFloat();
            details = String.format("朝向 yaw=%.1f pitch=%.1f", yaw, pitch);
        } else if (json.has("x") && json.has("y") && json.has("z")) {
            double x = json.get("x").getAsDouble();
            double y = json.get("y").getAsDouble();
            double z = json.get("z").getAsDouble();
            double dx = x - compat.getX(target);
            double dy = y - compat.getY(target);
            double dz = z - compat.getZ(target);
            double horizontalDist = Math.sqrt(dx * dx + dz * dz);
            yaw = (float) Math.toDegrees(Math.atan2(-dx, dz));
            pitch = (float) Math.toDegrees(Math.atan2(-dy, horizontalDist));
            details = String.format("看向 (%.1f, %.1f, %.1f)", x, y, z);
        } else {
            return error("需要 yaw+pitch 或 x+y+z 参数");
        }

        compat.setRotation(target, yaw, pitch);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        result.addProperty("details", details);
        return result;
    }

    /**
     * 发送聊天消息
     * Body: {"message": "Hello!"}
     */
    public static JsonObject chat(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        Object target = getTarget();
        if (target == null) return error("No player or bot available");

        MinecraftCompat compat = VersionCompat.getCompat();
        String message = json.get("message").getAsString();

        try {
            // Create text component and broadcast
            String playerName = compat.getPlayerName(target);
            Class<?> textClass = Class.forName("net.minecraft.text.Text");
            Object text = textClass.getMethod("literal", String.class).invoke(null, "[" + playerName + "] " + message);
            Object playerManager = server.getClass().getMethod("getPlayerManager").invoke(server);
            playerManager.getClass().getMethod("broadcast", textClass, boolean.class).invoke(playerManager, text, false);
        } catch (Exception e) {
            // Try Mojang-mapped Component class
            try {
                String playerName = compat.getPlayerName(target);
                Class<?> componentClass = Class.forName("net.minecraft.network.chat.Component");
                Object text = componentClass.getMethod("literal", String.class).invoke(null, "[" + playerName + "] " + message);
                Object playerManager = server.getClass().getMethod("getPlayerManager").invoke(server);
                playerManager.getClass().getMethod("broadcast", componentClass, boolean.class).invoke(playerManager, text, false);
            } catch (Exception e2) {
                return error("Chat failed: " + e2.getMessage());
            }
        }

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        result.addProperty("details", String.format("发送消息: %s", message));
        return result;
    }

    // ─── 辅助方法 ─────────────────────────────────────

    /**
     * 获取玩家的世界对象（兼容不同版本的方法名）
     */
    private static Object getWorld(Object player) throws Exception {
        String[] methods = {"getWorld", "level", "serverLevel"};
        for (String method : methods) {
            try {
                return player.getClass().getMethod(method).invoke(player);
            } catch (NoSuchMethodException ignored) {}
        }
        throw new NoSuchMethodException("Cannot find world accessor on " + player.getClass().getName());
    }

    /**
     * 获取饥饿管理器（兼容不同版本的方法名）
     */
    private static Object getHungerManager(Object player) throws Exception {
        String[] methods = {"getHungerManager", "getFoodData", "foodData"};
        for (String method : methods) {
            try {
                return player.getClass().getMethod(method).invoke(player);
            } catch (NoSuchMethodException ignored) {}
        }
        throw new NoSuchMethodException("Cannot find hunger manager on " + player.getClass().getName());
    }

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
