package blockmind.collector;

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
 */
public class StateCollector {

    private static MinecraftServer server;

    public static void setServer(MinecraftServer srv) {
        server = srv;
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

        ServerPlayerEntity player = getFirstPlayer();
        if (player == null) {
            json.addProperty("connected", false);
            return json;
        }

        json.addProperty("connected", true);
        json.addProperty("health", player.getHealth());
        json.addProperty("hunger", player.getHungerManager().getFoodLevel());
        json.addProperty("saturation", player.getHungerManager().getSaturationLevel());

        // 位置
        JsonObject pos = new JsonObject();
        pos.addProperty("x", player.getX());
        pos.addProperty("y", player.getY());
        pos.addProperty("z", player.getZ());
        json.add("position", pos);

        // 朝向
        JsonObject rotation = new JsonObject();
        rotation.addProperty("yaw", player.getYaw());
        rotation.addProperty("pitch", player.getPitch());
        json.add("rotation", rotation);

        // 经验
        json.addProperty("experience", player.totalExperience);
        json.addProperty("level", player.experienceLevel);

        // 维度
        json.addProperty("dimension", player.getWorld().getRegistryKey().getValue().toString());
        json.addProperty("time_of_day", player.getWorld().getTimeOfDay());
        json.addProperty("weather", getWeather(player));

        return json;
    }

    /**
     * 获取世界状态
     */
    public static JsonObject getWorld() {
        JsonObject json = new JsonObject();
        if (server == null) return json;

        ServerPlayerEntity player = getFirstPlayer();
        if (player == null) return json;

        World world = player.getWorld();
        json.addProperty("dimension", world.getRegistryKey().getValue().toString());
        json.addProperty("time_of_day", world.getTimeOfDay());
        json.addProperty("weather", getWeather(player));
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

        ServerPlayerEntity player = getFirstPlayer();
        if (player == null) return json;

        JsonArray items = new JsonArray();
        int emptySlots = 0;

        for (int i = 0; i < player.getInventory().size(); i++) {
            ItemStack stack = player.getInventory().getStack(i);
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

        ServerPlayerEntity player = getFirstPlayer();
        if (player == null) {
            json.add("entities", entities);
            return json;
        }

        for (Entity entity : player.getWorld().getEntitiesByClass(
                Entity.class,
                new Box(
                    player.getX() - radius, player.getY() - radius, player.getZ() - radius,
                    player.getX() + radius, player.getY() + radius, player.getZ() + radius
                ),
                e -> e != player
        )) {
            double distance = entity.distanceTo(player);
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

        ServerPlayerEntity player = getFirstPlayer();
        if (player == null) {
            json.add("blocks", blocks);
            return json;
        }

        BlockPos playerPos = player.getBlockPos();
        World world = player.getWorld();

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
