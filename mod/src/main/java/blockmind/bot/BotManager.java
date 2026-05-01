package blockmind.bot;

import blockmind.BlockMindMod;
import com.google.gson.JsonObject;
import com.mojang.authlib.GameProfile;
import net.minecraft.network.packet.c2s.common.SyncedClientOptions;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.BlockPos;

import java.util.UUID;

/**
 * Bot 管理器 — 管理 FakePlayer 的生命周期
 *
 * 使用 BotPlayer（继承 ServerPlayerEntity）避免所有网络相关 NPE。
 * Bot 可以执行游戏动作但不发送网络包。
 */
public class BotManager {

    private static MinecraftServer server;
    private static BotPlayer botPlayer;
    private static String botName = "BlockMind_Bot";
    private static final UUID BOT_UUID = UUID.fromString("a0b1c2d3-e4f5-6789-abcd-ef0123456789");

    public static synchronized void setServer(MinecraftServer srv) {
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
            GameProfile profile = new GameProfile(BOT_UUID, botName);
            ServerWorld world = server.getOverworld();
            SyncedClientOptions clientOptions = SyncedClientOptions.createDefault();

            // 使用 BotPlayer 子类，覆盖所有网络相关方法
            botPlayer = new BotPlayer(server, world, profile, clientOptions);

            BlockPos spawnPos = world.getSpawnPos();
            botPlayer.refreshPositionAndAngles(
                spawnPos.getX() + 0.5,
                spawnPos.getY(),
                spawnPos.getZ() + 0.5,
                0, 0
            );

            BlockMindMod.LOGGER.info("[BlockMind] ✅ Bot '{}' spawned at ({}, {}, {})",
                    botName, spawnPos.getX(), spawnPos.getY(), spawnPos.getZ());

            result.addProperty("success", true);
            result.addProperty("name", botName);
            result.addProperty("uuid", BOT_UUID.toString());

            JsonObject pos = new JsonObject();
            pos.addProperty("x", spawnPos.getX());
            pos.addProperty("y", spawnPos.getY());
            pos.addProperty("z", spawnPos.getZ());
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
            botPlayer.discard();
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
        result.addProperty("spawned", true);
        result.addProperty("name", botName);
        result.addProperty("uuid", BOT_UUID.toString());
        result.addProperty("health", botPlayer.getHealth());
        result.addProperty("hunger", botPlayer.getHungerManager().getFoodLevel());
        result.addProperty("saturation", botPlayer.getHungerManager().getSaturationLevel());

        JsonObject pos = new JsonObject();
        pos.addProperty("x", Math.round(botPlayer.getX() * 10.0) / 10.0);
        pos.addProperty("y", Math.round(botPlayer.getY() * 10.0) / 10.0);
        pos.addProperty("z", Math.round(botPlayer.getZ() * 10.0) / 10.0);
        result.add("position", pos);

        JsonObject rotation = new JsonObject();
        rotation.addProperty("yaw", botPlayer.getYaw());
        rotation.addProperty("pitch", botPlayer.getPitch());
        result.add("rotation", rotation);

        result.addProperty("experience", botPlayer.totalExperience);
        result.addProperty("level", botPlayer.experienceLevel);
        result.addProperty("dimension", botPlayer.getWorld().getRegistryKey().getValue().toString());
        result.addProperty("alive", botPlayer.isAlive());
        return result;
    }

    public static synchronized ServerPlayerEntity getBot() { return botPlayer; }
    public static synchronized boolean isSpawned() { return botPlayer != null; }
    public static synchronized String getBotName() { return botName; }
}
