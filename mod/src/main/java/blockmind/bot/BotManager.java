package blockmind.bot;

import blockmind.BlockMindMod;
import blockmind.compat.MinecraftCompat;
import blockmind.compat.VersionCompat;
import com.google.gson.JsonObject;
import com.mojang.authlib.GameProfile;

import java.util.UUID;

/**
 * Bot 管理器 — 管理 FakePlayer 的生命周期
 *
 * 使用 MinecraftCompat 接口隔离版本差异。
 * 玩家对象存储为 Object，通过 compat 接口访问属性。
 * BotPlayer 包装类提供便捷的方法访问。
 */
public class BotManager {

    private static Object server;
    private static BotPlayer botPlayer;
    private static String botName = "BlockMind_Bot";
    private static final UUID BOT_UUID = UUID.fromString("a0b1c2d3-e4f5-6789-abcd-ef0123456789");

    public static synchronized void setServer(Object srv) {
        server = srv;
    }

    public static synchronized JsonObject spawn(String name) {
        JsonObject result = new JsonObject();

        if (server == null) {
            result.addProperty("success", false);
            result.addProperty("error", "Server not ready");
            return result;
        }

        if (botPlayer != null) {
            result.addProperty("success", false);
            result.addProperty("error", "Bot already spawned");
            result.addProperty("name", botName);
            return result;
        }

        if (name != null && !name.isEmpty()) {
            botName = name;
        }

        try {
            MinecraftCompat compat = VersionCompat.getCompat();
            GameProfile profile = new GameProfile(BOT_UUID, botName);

            // 获取 overworld — 通过反射（不同版本方法名不同）
            Object world = getOverworld(server);

            // 使用 MinecraftCompat 创建玩家（版本无关）
            Object player = compat.createPlayer(server, world, profile);

            // 包装为 BotPlayer
            botPlayer = new BotPlayer(player, compat);

            // 设置出生点位置
            int[] spawnPos = getSpawnPos(world);
            compat.refreshPositionAndAngles(player,
                spawnPos[0] + 0.5, spawnPos[1], spawnPos[2] + 0.5, 0, 0);

            BlockMindMod.LOGGER.info("[BlockMind] ✅ Bot '{}' spawned at ({}, {}, {})",
                    botName, spawnPos[0], spawnPos[1], spawnPos[2]);

            result.addProperty("success", true);
            result.addProperty("name", botName);
            result.addProperty("uuid", BOT_UUID.toString());

            JsonObject pos = new JsonObject();
            pos.addProperty("x", spawnPos[0]);
            pos.addProperty("y", spawnPos[1]);
            pos.addProperty("z", spawnPos[2]);
            result.add("position", pos);

        } catch (Exception e) {
            BlockMindMod.LOGGER.error("[BlockMind] Failed to spawn bot: {}", e.getMessage(), e);
            result.addProperty("success", false);
            result.addProperty("error", e.getMessage());
            botPlayer = null;
        }

        return result;
    }

    public static synchronized JsonObject despawn() {
        JsonObject result = new JsonObject();
        if (botPlayer == null) {
            result.addProperty("success", false);
            result.addProperty("error", "No bot spawned");
            return result;
        }
        try {
            String name = botName;
            MinecraftCompat compat = VersionCompat.getCompat();
            compat.discard(botPlayer.getHandle());
            botPlayer = null;
            BlockMindMod.LOGGER.info("[BlockMind] Bot '{}' despawned", name);
            result.addProperty("success", true);
            result.addProperty("message", "Bot '" + name + "' removed");
        } catch (Exception e) {
            BlockMindMod.LOGGER.error("[BlockMind] Failed to despawn bot: {}", e.getMessage(), e);
            result.addProperty("success", false);
            result.addProperty("error", e.getMessage());
        }
        return result;
    }

    public static synchronized JsonObject getStatus() {
        JsonObject result = new JsonObject();
        if (botPlayer == null) {
            result.addProperty("spawned", false);
            return result;
        }

        MinecraftCompat compat = VersionCompat.getCompat();
        Object handle = botPlayer.getHandle();

        result.addProperty("spawned", true);
        result.addProperty("name", botName);
        result.addProperty("uuid", BOT_UUID.toString());
        result.addProperty("health", compat.getHealth(handle));
        result.addProperty("hunger", compat.getFoodLevel(handle));
        result.addProperty("saturation", compat.getSaturationLevel(handle));

        JsonObject pos = new JsonObject();
        pos.addProperty("x", Math.round(compat.getX(handle) * 10.0) / 10.0);
        pos.addProperty("y", Math.round(compat.getY(handle) * 10.0) / 10.0);
        pos.addProperty("z", Math.round(compat.getZ(handle) * 10.0) / 10.0);
        result.add("position", pos);

        JsonObject rotation = new JsonObject();
        rotation.addProperty("yaw", compat.getYaw(handle));
        rotation.addProperty("pitch", compat.getPitch(handle));
        result.add("rotation", rotation);

        result.addProperty("experience", compat.getTotalExperience(handle));
        result.addProperty("level", compat.getExperienceLevel(handle));
        result.addProperty("dimension", compat.getDimension(handle));
        result.addProperty("alive", compat.isAlive(handle));
        return result;
    }

    public static synchronized Object getBot() {
        return botPlayer != null ? botPlayer.getHandle() : null;
    }

    public static synchronized BotPlayer getBotPlayer() {
        return botPlayer;
    }

    public static synchronized boolean isSpawned() { return botPlayer != null; }
    public static synchronized String getBotName() { return botName; }

    // ── Reflection helpers for version-specific server/world methods ──

    /**
     * Get the overworld from the server.
     * MC 1.20.x/1.21.x (Yarn): server.getOverworld()
     * MC 26.x (Mojang): server.overworld() or server.getOverworld()
     */
    private static Object getOverworld(Object server) {
        // Try common method names
        String[] methods = {"getOverworld", "overworld"};
        for (String method : methods) {
            try {
                return server.getClass().getMethod(method).invoke(server);
            } catch (Exception ignored) {}
        }
        throw new RuntimeException("Cannot get overworld from server");
    }

    /**
     * Get spawn position from the world.
     * Returns int[3] {x, y, z}.
     */
    private static int[] getSpawnPos(Object world) {
        try {
            Object spawnPos = world.getClass().getMethod("getSpawnPos").invoke(world);
            int x = (int) spawnPos.getClass().getMethod("getX").invoke(spawnPos);
            int y = (int) spawnPos.getClass().getMethod("getY").invoke(spawnPos);
            int z = (int) spawnPos.getClass().getMethod("getZ").invoke(spawnPos);
            return new int[]{x, y, z};
        } catch (Exception e) {
            // Fallback: default spawn
            BlockMindMod.LOGGER.warn("[BlockMind] Could not get spawn pos, using (0, 64, 0)");
            return new int[]{0, 64, 0};
        }
    }
}
