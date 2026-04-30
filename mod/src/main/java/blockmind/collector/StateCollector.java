package blockmind.collector;

import blockmind.bot.BotManager;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.entity.Entity;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.entity.ItemEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.world.World;

/**
 * 游戏状态采集器
 * 从 Minecraft 服务器内部 API 采集状态数据
 * 优先采集 Bot 数据（如果已 spawn）
 */
public class StateCollector {

    private static MinecraftServer server;

    public static void setServer(MinecraftServer srv) {
        server = srv;
    }

    /**
     * 获取目标玩家：优先 Bot，回退到第一个在线玩家
     */
    private static ServerPlayerEntity getTarget() {
        if (BotManager.isSpawned()) {
            ServerPlayerEntity bot = BotManager.getBot();
            if (bot != null && bot.isAlive()) return bot;
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

        ServerPlayerEntity target = getTarget();
        if (target == null) {
            json.addProperty("connected", false);
            json.addProperty("bot_spawned", BotManager.isSpawned());
            return json;
        }

        json.addProperty("connected", true);
        json.addProperty("target", BotManager.isSpawned() ? "bot" : "player");
        json.addProperty("name", target.getName().getString());
        json.addProperty("health", target.getHealth());
        json.addProperty("hunger", target.getHungerManager().getFoodLevel());
        json.addProperty("saturation", target.getHungerManager().getSaturationLevel());

        // 位置
        JsonObject pos = new JsonObject();
        pos.addProperty("x", target.getX());
        pos.addProperty("y", target.getY());
        pos.addProperty("z", target.getZ());
        json.add("position", pos);

        // 朝向
        JsonObject rotation = new JsonObject();
        rotation.addProperty("yaw", target.getYaw());
        rotation.addProperty("pitch", target.getPitch());
        json.add("rotation", rotation);

        // 经验
        json.addProperty("experience", target.totalExperience);
        json.addProperty("level", target.experienceLevel);

        // 维度
        json.addProperty("dimension", target.getWorld().getRegistryKey().getValue().toString());
        json.addProperty("time_of_day", target.getWorld().getTimeOfDay());
        json.addProperty("weather", getWeather(target));

        return json;
    }

    /**
     * 获取世界状态
     */
    public static JsonObject getWorld() {
        JsonObject json = new JsonObject();
        if (server == null) return json;

        ServerPlayerEntity target = getTarget();
        if (target == null) return json;

        World world = target.getWorld();
        json.addProperty("dimension", world.getRegistryKey().getValue().toString());
        json.addProperty("time_of_day", world.getTimeOfDay());
        json.addProperty("weather", getWeather(target));
        json.addProperty("difficulty", world.getDifficulty().getName());
        json.addProperty("day_count", world.getTimeOfDay() / 24000L);

        return json;
    }

    /**
     * 获取背包
     */
    public static JsonObject getInventory() {
        JsonObject json = new JsonObject();
        if (server == null) return json;

        ServerPlayerEntity target = getTarget();
        if (target == null) return json;

        JsonArray items = new JsonArray();
        int emptySlots = 0;

        for (int i = 0; i < target.getInventory().size(); i++) {
            ItemStack stack = target.getInventory().getStack(i);
            if (stack.isEmpty()) {
                emptySlots++;
                continue;
            }

            JsonObject item = new JsonObject();
            item.addProperty("name", stack.getItem().toString());
            item.addProperty("slot", i);
            item.addProperty("count", stack.getCount());
            item.addProperty("durability", stack.getMaxDamage() - stack.getDamage());
            item.addProperty("max_durability", stack.getMaxDamage());
            items.add(item);
        }

        json.add("items", items);
        json.addProperty("empty_slots", emptySlots);
        json.addProperty("is_full", emptySlots == 0);

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

        ServerPlayerEntity target = getTarget();
        if (target == null) {
            json.add("entities", entities);
            return json;
        }

        for (Entity entity : target.getWorld().getEntitiesByClass(
                Entity.class,
                new Box(
                    target.getX() - radius, target.getY() - radius, target.getZ() - radius,
                    target.getX() + radius, target.getY() + radius, target.getZ() + radius
                ),
                e -> e != target
        )) {
            double distance = entity.distanceTo(target);
            if (distance > radius) continue;

            JsonObject ent = new JsonObject();
            ent.addProperty("id", entity.getId());
            ent.addProperty("type", entity.getType().toString());
            ent.addProperty("distance", Math.round(distance * 10.0) / 10.0);

            JsonObject pos = new JsonObject();
            pos.addProperty("x", entity.getX());
            pos.addProperty("y", entity.getY());
            pos.addProperty("z", entity.getZ());
            ent.add("position", pos);

            if (entity instanceof HostileEntity) {
                ent.addProperty("hostile", true);
                ent.addProperty("health", ((HostileEntity) entity).getHealth());
            } else {
                ent.addProperty("hostile", false);
            }

            entities.add(ent);
        }

        json.add("entities", entities);
        return json;
    }

    /**
     * 获取附近方块
     */
    public static JsonObject getBlocks(int radius, String type) {
        JsonObject json = new JsonObject();
        JsonArray blocks = new JsonArray();

        if (server == null) {
            json.add("blocks", blocks);
            return json;
        }

        ServerPlayerEntity target = getTarget();
        if (target == null) {
            json.add("blocks", blocks);
            return json;
        }

        BlockPos playerPos = target.getBlockPos();
        World world = target.getWorld();

        for (int x = -radius; x <= radius; x++) {
            for (int y = -radius; y <= radius; y++) {
                for (int z = -radius; z <= radius; z++) {
                    BlockPos pos = playerPos.add(x, y, z);
                    String blockType = world.getBlockState(pos).getBlock().toString();

                    if (type != null && !blockType.contains(type)) continue;

                    JsonObject block = new JsonObject();
                    JsonObject blockPos = new JsonObject();
                    blockPos.addProperty("x", pos.getX());
                    blockPos.addProperty("y", pos.getY());
                    blockPos.addProperty("z", pos.getZ());
                    block.add("position", blockPos);
                    block.addProperty("type", blockType);
                    blocks.add(block);
                }
            }
        }

        json.add("blocks", blocks);
        return json;
    }

    // ─── 辅助方法 ─────────────────────────────────────

    private static ServerPlayerEntity getFirstPlayer() {
        if (server == null) return null;
        var players = server.getPlayerManager().getPlayerList();
        return players.isEmpty() ? null : players.get(0);
    }

    private static String getWeather(ServerPlayerEntity player) {
        World world = player.getWorld();
        if (world.isThundering()) return "thunder";
        if (world.isRaining()) return "rain";
        return "clear";
    }
}
