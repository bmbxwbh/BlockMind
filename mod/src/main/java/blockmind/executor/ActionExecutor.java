package blockmind.executor;

import blockmind.bot.BotManager;
import blockmind.compat.MinecraftCompat;
import blockmind.compat.VersionCompat;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

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

    private static final Map<String, int[]> FOOD_VALUES = new HashMap<>();
    static {
        FOOD_VALUES.put("bread", new int[]{5, 6});
        FOOD_VALUES.put("apple", new int[]{4, 2});
        FOOD_VALUES.put("golden_apple", new int[]{4, 9});
        FOOD_VALUES.put("enchanted_golden_apple", new int[]{4, 10});
        FOOD_VALUES.put("cooked_beef", new int[]{8, 12});
        FOOD_VALUES.put("cooked_porkchop", new int[]{8, 12});
        FOOD_VALUES.put("cooked_chicken", new int[]{6, 7});
        FOOD_VALUES.put("cooked_mutton", new int[]{6, 9});
        FOOD_VALUES.put("cooked_salmon", new int[]{6, 9});
        FOOD_VALUES.put("cooked_cod", new int[]{5, 6});
        FOOD_VALUES.put("steak", new int[]{8, 12});
        FOOD_VALUES.put("porkchop", new int[]{3, 3});
        FOOD_VALUES.put("beef", new int[]{3, 3});
        FOOD_VALUES.put("chicken", new int[]{3, 3});
        FOOD_VALUES.put("mutton", new int[]{3, 3});
        FOOD_VALUES.put("salmon", new int[]{3, 2});
        FOOD_VALUES.put("cod", new int[]{3, 2});
        FOOD_VALUES.put("carrot", new int[]{3, 3});
        FOOD_VALUES.put("potato", new int[]{1, 3});
        FOOD_VALUES.put("baked_potato", new int[]{5, 6});
        FOOD_VALUES.put("golden_carrot", new int[]{6, 12});
        FOOD_VALUES.put("melon_slice", new int[]{2, 1});
        FOOD_VALUES.put("sweet_berries", new int[]{2, 1});
        FOOD_VALUES.put("glow_berries", new int[]{2, 1});
        FOOD_VALUES.put("cookie", new int[]{2, 1});
        FOOD_VALUES.put("pumpkin_pie", new int[]{8, 4});
        FOOD_VALUES.put("mushroom_stew", new int[]{6, 7});
        FOOD_VALUES.put("rabbit_stew", new int[]{10, 12});
        FOOD_VALUES.put("beetroot_soup", new int[]{6, 7});
        FOOD_VALUES.put("beetroot", new int[]{1, 1});
        FOOD_VALUES.put("dried_kelp", new int[]{1, 6});
        FOOD_VALUES.put("tropical_fish", new int[]{1, 2});
        FOOD_VALUES.put("pufferfish", new int[]{1, 2});
        FOOD_VALUES.put("rotten_flesh", new int[]{4, 8});
        FOOD_VALUES.put("spider_eye", new int[]{2, 3});
    }

    /**
     * Run a task on the server thread, blocking the HTTP thread until complete.
     * Thread safety (issue 8, T2): all game operations run on the tick thread.
     */
    private static JsonObject dispatchToServer(java.util.function.Supplier<JsonObject> task) {
        if (server == null) return error("Server not available");
        CompletableFuture<JsonObject> future = new CompletableFuture<>();
        try {
            server.getClass().getMethod("execute", Runnable.class)
                    .invoke(server, (Runnable) () -> {
                        try {
                            future.complete(task.get());
                        } catch (Exception e) {
                            future.complete(error("Server error: " + e.getMessage()));
                        }
                    });
        } catch (Exception e) {
            return error("Failed to dispatch to server: " + e.getMessage());
        }
        try {
            return future.get();
        } catch (Exception e) {
            return error("Dispatch failed: " + e.getMessage());
        }
    }

    /**
     * 获取目标玩家：优先 Bot，回退到第一个在线玩家
     * T2 fix: synchronized on BotManager for atomic check-then-act
     */
    private static Object getTarget() {
        synchronized (BotManager.class) {
            MinecraftCompat compat = VersionCompat.getCompat();
            if (BotManager.isSpawned()) {
                Object bot = BotManager.getBot();
                if (bot != null && compat.isAlive(bot)) {
                    return bot;
                }
            }
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
    }

    /**
     * 移动到指定位置
     * Body: {"x": 128, "y": 64, "z": -256, "sprint": false}
     */
    public static JsonObject move(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        if (!json.has("x") || !json.has("y") || !json.has("z"))
            return error("Missing required fields: x, y, z");

        double x = json.get("x").getAsDouble();
        double y = json.get("y").getAsDouble();
        double z = json.get("z").getAsDouble();

        return dispatchToServer(() -> {
            Object target = getTarget();
            if (target == null) return error("No player or bot available");

            MinecraftCompat compat = VersionCompat.getCompat();

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
        });
    }

    /**
     * 挖掘方块
     * Body: {"x": 128, "y": 63, "z": -256}
     * S8 fix: use world.breakBlock to simulate actual mining
     */
    public static JsonObject dig(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        if (!json.has("x") || !json.has("y") || !json.has("z"))
            return error("Missing required fields: x, y, z");

        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

        return dispatchToServer(() -> {
            Object target = getTarget();
            if (target == null) return error("No player or bot available");

            try {
                Class<?> blockPosClass = Class.forName("net.minecraft.util.math.BlockPos");
                Object pos = blockPosClass.getConstructor(int.class, int.class, int.class).newInstance(x, y, z);

                Object world = getWorld(target);
                Object blockState = world.getClass().getMethod("getBlockState", blockPosClass).invoke(world, pos);
                boolean isAir = (boolean) blockState.getClass().getMethod("isAir").invoke(blockState);
                if (isAir) return error("Cannot dig air block");

                String blockType = blockState.getClass().getMethod("getBlock").invoke(blockState).toString();

                try {
                    world.getClass().getMethod("breakBlock", blockPosClass, boolean.class, target.getClass())
                            .invoke(world, pos, true, target);
                } catch (NoSuchMethodException e) {
                    Object airState = blockState.getClass().getMethod("getDefaultState").invoke(
                            Class.forName("net.minecraft.block.Blocks").getField("AIR").get(null));
                    world.getClass().getMethod("setBlockState", blockPosClass, blockState.getClass())
                            .invoke(world, pos, airState);
                }

                JsonObject result = new JsonObject();
                result.addProperty("success", true);
                result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
                result.addProperty("details", String.format("挖掘 %s at (%d, %d, %d)", blockType, x, y, z));
                return result;
            } catch (Exception e) {
                return error("Dig failed: " + e.getMessage());
            }
        });
    }

    /**
     * 放置方块
     * Body: {"item": "torch", "x": 128, "y": 64, "z": -256}
     * Issue 10 fix: implement actual block placement
     */
    public static JsonObject place(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        if (!json.has("item"))
            return error("Missing required field: item");
        if (!json.has("x") || !json.has("y") || !json.has("z"))
            return error("Missing required fields: x, y, z");

        String item = json.get("item").getAsString();
        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

        return dispatchToServer(() -> {
            Object target = getTarget();
            if (target == null) return error("No player or bot available");

            try {
                Class<?> blockPosClass = Class.forName("net.minecraft.util.math.BlockPos");
                Object pos = blockPosClass.getConstructor(int.class, int.class, int.class).newInstance(x, y, z);

                Object world = getWorld(target);

                Class<?> registryClass = Class.forName("net.minecraft.registry.Registry");
                Class<?> identifierClass = Class.forName("net.minecraft.util.Identifier");
                Object identifier = identifierClass.getMethod("of", String.class, String.class).invoke(null, "minecraft", item);
                Object block = registryClass.getMethod("get", Class.class, identifierClass).invoke(null,
                        Class.forName("net.minecraft.block.Block"), identifier);

                if (block == null) return error("Unknown block: " + item);

                Object defaultState = block.getClass().getMethod("getDefaultState").invoke(block);
                world.getClass().getMethod("setBlockState", blockPosClass, defaultState.getClass())
                        .invoke(world, pos, defaultState);

                JsonObject result = new JsonObject();
                result.addProperty("success", true);
                result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
                result.addProperty("details", String.format("放置 %s at (%d, %d, %d)", item, x, y, z));
                return result;
            } catch (Exception e) {
                try {
                    Class<?> blockPosClass = Class.forName("net.minecraft.util.math.BlockPos");
                    Object pos = blockPosClass.getConstructor(int.class, int.class, int.class).newInstance(x, y, z);
                    Object world = getWorld(target);
                    Class<?> blocksClass = Class.forName("net.minecraft.block.Blocks");
                    Object airBlock = blocksClass.getField(item.toUpperCase()).get(null);
                    Object defaultState = airBlock.getClass().getMethod("getDefaultState").invoke(airBlock);
                    world.getClass().getMethod("setBlockState", blockPosClass, defaultState.getClass())
                            .invoke(world, pos, defaultState);

                    JsonObject result = new JsonObject();
                    result.addProperty("success", true);
                    result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
                    result.addProperty("details", String.format("放置 %s at (%d, %d, %d)", item, x, y, z));
                    return result;
                } catch (Exception e2) {
                    return error("Place failed: " + e.getMessage());
                }
            }
        });
    }

    /**
     * 攻击实体
     * Body: {"entity_id": 123}
     */
    public static JsonObject attack(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        if (!json.has("entity_id"))
            return error("Missing required field: entity_id");

        int entityId = json.get("entity_id").getAsInt();

        return dispatchToServer(() -> {
            Object target = getTarget();
            if (target == null) return error("No player or bot available");

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
        });
    }

    /**
     * 进食
     * Body: {"item": "bread"}
     * F3 fix: food value lookup map instead of hardcoded values
     */
    public static JsonObject eat(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        if (!json.has("item"))
            return error("Missing required field: item");

        String item = json.get("item").getAsString();

        return dispatchToServer(() -> {
            Object target = getTarget();
            if (target == null) return error("No player or bot available");

            int[] values = FOOD_VALUES.get(item);
            int hunger = values != null ? values[0] : 4;
            float saturation = values != null ? values[1] * 0.1f : 0.3f;

            try {
                Object hungerManager = getHungerManager(target);
                hungerManager.getClass().getMethod("add", int.class, float.class).invoke(hungerManager, hunger, saturation);
            } catch (Exception e) {
                // Ignore — best effort
            }

            JsonObject result = new JsonObject();
            result.addProperty("success", true);
            result.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
            result.addProperty("details", String.format("进食 %s，恢复饥饿值 %d，饱和 %.1f", item, hunger, saturation));
            return result;
        });
    }

    /**
     * 设置朝向
     */
    public static JsonObject look(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        return dispatchToServer(() -> {
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
        });
    }

    /**
     * 发送聊天消息
     * Body: {"message": "Hello!"}
     */
    public static JsonObject chat(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        if (!json.has("message"))
            return error("Missing required field: message");

        String message = json.get("message").getAsString();

        return dispatchToServer(() -> {
            Object target = getTarget();
            if (target == null) return error("No player or bot available");

            MinecraftCompat compat = VersionCompat.getCompat();

            try {
                String playerName = compat.getPlayerName(target);
                Class<?> textClass = Class.forName("net.minecraft.text.Text");
                Object text = textClass.getMethod("literal", String.class).invoke(null, "[" + playerName + "] " + message);
                Object playerManager = server.getClass().getMethod("getPlayerManager").invoke(server);
                playerManager.getClass().getMethod("broadcast", textClass, boolean.class).invoke(playerManager, text, false);
            } catch (Exception e) {
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
        });
    }

    // ─── 辅助方法 ─────────────────────────────────────

    private static Object getWorld(Object player) throws Exception {
        String[] methods = {"getWorld", "level", "serverLevel"};
        for (String method : methods) {
            try {
                return player.getClass().getMethod(method).invoke(player);
            } catch (NoSuchMethodException ignored) {}
        }
        throw new NoSuchMethodException("Cannot find world accessor on " + player.getClass().getName());
    }

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
