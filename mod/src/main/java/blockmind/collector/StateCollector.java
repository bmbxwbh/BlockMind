package blockmind.collector;

import blockmind.bot.BotManager;
import blockmind.compat.MinecraftCompat;
import blockmind.compat.VersionCompat;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;

import java.util.List;

/**
 * 游戏状态采集器
 * 从 Minecraft 服务器内部 API 采集状态数据
 * 优先采集 Bot 数据（如果已 spawn）
 *
 * 使用 MinecraftCompat 接口隔离版本差异。
 */
public class StateCollector {

    private static Object server;

    public static void setServer(Object srv) {
        server = srv;
    }

    /**
     * 获取目标玩家：优先 Bot，回退到第一个在线玩家
     */
    private static Object getTarget() {
        MinecraftCompat compat = VersionCompat.getCompat();
        if (BotManager.isSpawned()) {
            Object bot = BotManager.getBot();
            if (bot != null && compat.isAlive(bot)) return bot;
        }
        return getFirstPlayer();
    }

    /**
     * 获取玩家状态
     */
    public static JsonObject getStatus() {
        JsonObject json = new JsonObject();
        if (server == null) {
            json.addProperty("error", "Server not ready");
            return json;
        }

        Object target = getTarget();
        if (target == null) {
            json.addProperty("connected", false);
            json.addProperty("bot_spawned", BotManager.isSpawned());
            return json;
        }

        MinecraftCompat compat = VersionCompat.getCompat();

        json.addProperty("connected", true);
        json.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        json.addProperty("name", compat.getPlayerName(target));
        json.addProperty("health", compat.getHealth(target));
        json.addProperty("hunger", compat.getFoodLevel(target));
        json.addProperty("saturation", compat.getSaturationLevel(target));

        // 位置
        JsonObject pos = new JsonObject();
        pos.addProperty("x", compat.getX(target));
        pos.addProperty("y", compat.getY(target));
        pos.addProperty("z", compat.getZ(target));
        json.add("position", pos);

        // 朝向
        JsonObject rotation = new JsonObject();
        rotation.addProperty("yaw", compat.getYaw(target));
        rotation.addProperty("pitch", compat.getPitch(target));
        json.add("rotation", rotation);

        // 经验
        json.addProperty("experience", compat.getTotalExperience(target));
        json.addProperty("level", compat.getExperienceLevel(target));

        // 维度
        json.addProperty("dimension", compat.getDimension(target));

        // 世界时间
        json.addProperty("time_of_day", compat.getWorldTimeOfDay(target));

        // 天气
        json.addProperty("weather", getWeather(target, compat));

        return json;
    }

    /**
     * 获取世界状态
     */
    public static JsonObject getWorld() {
        JsonObject json = new JsonObject();
        if (server == null) return json;

        Object target = getTarget();
        if (target == null) return json;

        MinecraftCompat compat = VersionCompat.getCompat();

        json.addProperty("dimension", compat.getDimension(target));
        json.addProperty("time_of_day", compat.getWorldTimeOfDay(target));
        json.addProperty("weather", getWeather(target, compat));

        try {
            Object world = getWorldObj(target);
            String difficulty = (String) world.getClass().getMethod("getDifficulty").invoke(world)
                    .getClass().getMethod("getName").invoke(world.getClass().getMethod("getDifficulty").invoke(world));
            json.addProperty("difficulty", difficulty);
        } catch (Exception ignored) {}

        json.addProperty("day_count", compat.getWorldTimeOfDay(target) / 24000L);

        return json;
    }

    /**
     * 获取背包
     */
    public static JsonObject getInventory() {
        JsonObject json = new JsonObject();
        if (server == null) return json;

        Object target = getTarget();
        if (target == null) return json;

        try {
            Object inventory = target.getClass().getMethod("getInventory").invoke(target);
            int size = (int) inventory.getClass().getMethod("size").invoke(inventory);

            JsonArray items = new JsonArray();
            int emptySlots = 0;

            for (int i = 0; i < size; i++) {
                Object stack = inventory.getClass().getMethod("getStack", int.class).invoke(inventory, i);
                boolean isEmpty = (boolean) stack.getClass().getMethod("isEmpty").invoke(stack);
                if (isEmpty) {
                    emptySlots++;
                    continue;
                }

                JsonObject item = new JsonObject();
                item.addProperty("name", stack.getClass().getMethod("getItem").invoke(stack).toString());
                item.addProperty("slot", i);
                item.addProperty("count", (int) stack.getClass().getMethod("getCount").invoke(stack));
                int maxDamage = (int) stack.getClass().getMethod("getMaxDamage").invoke(stack);
                int damage = (int) stack.getClass().getMethod("getDamage").invoke(stack);
                item.addProperty("durability", maxDamage - damage);
                item.addProperty("max_durability", maxDamage);
                items.add(item);
            }

            json.add("items", items);
            json.addProperty("empty_slots", emptySlots);
            json.addProperty("is_full", emptySlots == 0);
        } catch (Exception e) {
            json.addProperty("error", "Failed to read inventory: " + e.getMessage());
        }

        return json;
    }

    /**
     * 获取附近实体
     */
    public static JsonObject getEntities(int radius) {
        JsonObject json = new JsonObject();
        JsonArray entities = new JsonArray();

        if (server == null) {
            json.add("entities", entities);
            return json;
        }

        Object target = getTarget();
        if (target == null) {
            json.add("entities", entities);
            return json;
        }

        MinecraftCompat compat = VersionCompat.getCompat();

        try {
            Object world = getWorldObj(target);
            Class<?> entityClass = Class.forName("net.minecraft.entity.Entity");
            Class<?> boxClass = Class.forName("net.minecraft.util.math.Box");

            double px = compat.getX(target);
            double py = compat.getY(target);
            double pz = compat.getZ(target);

            Object box = boxClass.getConstructor(
                    double.class, double.class, double.class,
                    double.class, double.class, double.class)
                    .newInstance(px - radius, py - radius, pz - radius,
                                 px + radius, py + radius, pz + radius);

            @SuppressWarnings("unchecked")
            List<?> entityList = (List<?>) world.getClass()
                    .getMethod("getEntitiesByClass", Class.class, boxClass, entityClass)
                    .invoke(world, entityClass, box, null);

            for (Object entity : entityList) {
                if (entity == target) continue;

                double distance = (double) entity.getClass().getMethod("distanceTo", entityClass)
                        .invoke(entity, target);
                if (distance > radius) continue;

                JsonObject ent = new JsonObject();
                ent.addProperty("id", (int) entity.getClass().getMethod("getId").invoke(entity));
                ent.addProperty("type", entity.getClass().getMethod("getType").invoke(entity).toString());
                ent.addProperty("distance", Math.round(distance * 10.0) / 10.0);

                JsonObject pos = new JsonObject();
                pos.addProperty("x", (double) entity.getClass().getMethod("getX").invoke(entity));
                pos.addProperty("y", (double) entity.getClass().getMethod("getY").invoke(entity));
                pos.addProperty("z", (double) entity.getClass().getMethod("getZ").invoke(entity));
                ent.add("position", pos);

                // Check if hostile
                try {
                    Class<?> hostileClass = Class.forName("net.minecraft.entity.mob.HostileEntity");
                    if (hostileClass.isInstance(entity)) {
                        ent.addProperty("hostile", true);
                        ent.addProperty("health", (float) entity.getClass().getMethod("getHealth").invoke(entity));
                    } else {
                        ent.addProperty("hostile", false);
                    }
                } catch (Exception e) {
                    ent.addProperty("hostile", false);
                }

                entities.add(ent);
            }
        } catch (Exception e) {
            // Silently return empty on error
        }

        json.add("entities", entities);
        return json;
    }

    /**
     * 获取附近方块
     */
    public static JsonObject getBlocks(int radius, String type) {
        return getBlocks(radius, type, 1000);
    }

    public static JsonObject getBlocks(int radius, String type, int maxBlocks) {
        JsonObject json = new JsonObject();
        JsonArray blocks = new JsonArray();

        if (server == null) {
            json.add("blocks", blocks);
            return json;
        }

        Object target = getTarget();
        if (target == null) {
            json.add("blocks", blocks);
            return json;
        }

        MinecraftCompat compat = VersionCompat.getCompat();

        try {
            int[] playerPos = compat.getBlockPos(target);
            Object world = getWorldObj(target);

            Class<?> blockPosClass = Class.forName("net.minecraft.util.math.BlockPos");

            int count = 0;
            boolean limitReached = false;
            for (int x = -radius; x <= radius && !limitReached; x++) {
                for (int y = -radius; y <= radius && !limitReached; y++) {
                    for (int z = -radius; z <= radius && !limitReached; z++) {
                        Object pos = blockPosClass.getConstructor(int.class, int.class, int.class)
                                .newInstance(playerPos[0] + x, playerPos[1] + y, playerPos[2] + z);
                        Object blockState = world.getClass().getMethod("getBlockState", blockPosClass)
                                .invoke(world, pos);

                        boolean isAir = (boolean) blockState.getClass().getMethod("isAir").invoke(blockState);
                        if (isAir) continue;

                        String blockType = blockState.getClass().getMethod("getBlock").invoke(blockState).toString();
                        if (type != null && !blockType.contains(type)) continue;

                        JsonObject block = new JsonObject();
                        JsonObject blockPos = new JsonObject();
                        blockPos.addProperty("x", (int) blockPosClass.getMethod("getX").invoke(pos));
                        blockPos.addProperty("y", (int) blockPosClass.getMethod("getY").invoke(pos));
                        blockPos.addProperty("z", (int) blockPosClass.getMethod("getZ").invoke(pos));
                        block.add("position", blockPos);
                        block.addProperty("type", blockType);
                        blocks.add(block);
                        count++;
                        if (count >= maxBlocks) {
                            limitReached = true;
                            break;
                        }
                    }
                }
            }

            json.addProperty("count", count);
            json.addProperty("max_blocks", maxBlocks);
        } catch (Exception e) {
            // Return what we have
        }

        json.add("blocks", blocks);
        return json;
    }

    // ─── 辅助方法 ─────────────────────────────────────

    private static Object getFirstPlayer() {
        if (server == null) return null;
        try {
            Object playerManager = server.getClass().getMethod("getPlayerManager").invoke(server);
            @SuppressWarnings("unchecked")
            List<?> players = (List<?>) playerManager.getClass().getMethod("getPlayerList").invoke(playerManager);
            return players.isEmpty() ? null : players.get(0);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * 获取世界对象（兼容不同版本的方法名）
     */
    private static Object getWorldObj(Object player) throws Exception {
        String[] methods = {"getWorld", "level", "serverLevel"};
        for (String method : methods) {
            try {
                return player.getClass().getMethod(method).invoke(player);
            } catch (NoSuchMethodException ignored) {}
        }
        throw new NoSuchMethodException("Cannot find world accessor");
    }

    private static String getWeather(Object player, MinecraftCompat compat) {
        try {
            Object world = getWorldObj(player);
            boolean thundering = (boolean) world.getClass().getMethod("isThundering").invoke(world);
            if (thundering) return "thunder";
            boolean raining = (boolean) world.getClass().getMethod("isRaining").invoke(world);
            if (raining) return "rain";
            return "clear";
        } catch (Exception e) {
            return "unknown";
        }
    }
}
