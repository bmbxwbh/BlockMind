package blockmind.bot;

import blockmind.BlockMindMod;
import com.google.gson.JsonObject;
import com.mojang.authlib.GameProfile;
import net.minecraft.entity.Entity;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.network.ClientConnection;
import net.minecraft.network.NetworkSide;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.text.Text;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.world.World;

import java.util.List;
import java.util.UUID;

/**
 * Bot 管理器 — 管理 FakePlayer 的生命周期
 *
 * 功能：
 * 1. 生成独立的 Bot 实体（FakePlayer）
 * 2. Bot 可以被其他玩家看到
 * 3. Bot 可以执行所有玩家动作（移动、挖方块、聊天等）
 * 4. 服务端重启自动清理
 */
public class BotManager {

    private static MinecraftServer server;
    private static ServerPlayerEntity botPlayer;
    private static String botName = "BlockMind_Bot";
    private static final UUID BOT_UUID = UUID.fromString("a0b1c2d3-e4f5-6789-abcd-ef0123456789");

    public static void setServer(MinecraftServer srv) {
        server = srv;
    }

    /**
     * 生成 Bot
     */
    public static JsonObject spawn(String name) {
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
            // 创建 GameProfile
            GameProfile profile = new GameProfile(BOT_UUID, botName);

            // 创建 FakePlayer
            ServerWorld world = server.getOverworld();
            botPlayer = new ServerPlayerEntity(server, world, profile);

            // 设置初始位置（世界出生点）
            BlockPos spawnPos = world.getSpawnPos();
            botPlayer.refreshPositionAndAngles(
                spawnPos.getX() + 0.5,
                spawnPos.getY(),
                spawnPos.getZ() + 0.5,
                0, 0
            );

            // 使用假的 ClientConnection 注册到服务器
            ClientConnection fakeConnection = new ClientConnection(NetworkSide.CLIENTBOUND);
            server.getPlayerManager().onPlayerConnect(fakeConnection, botPlayer);

            BlockMindMod.LOGGER.info("[BlockMind] ✅ Bot '{}' spawned at ({}, {}, {})",
                    botName,
                    spawnPos.getX(), spawnPos.getY(), spawnPos.getZ());

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

    /**
     * 移除 Bot
     */
    public static JsonObject despawn() {
        JsonObject result = new JsonObject();

        if (botPlayer == null) {
            result.addProperty("success", false);
            result.addProperty("error", "No bot spawned");
            return result;
        }

        try {
            String name = botName;

            // 从服务器移除
            server.getPlayerManager().remove(botPlayer);
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

    /**
     * 获取 Bot 状态
     */
    public static JsonObject getStatus() {
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

        // 位置
        JsonObject pos = new JsonObject();
        pos.addProperty("x", Math.round(botPlayer.getX() * 10.0) / 10.0);
        pos.addProperty("y", Math.round(botPlayer.getY() * 10.0) / 10.0);
        pos.addProperty("z", Math.round(botPlayer.getZ() * 10.0) / 10.0);
        result.add("position", pos);

        // 朝向
        JsonObject rotation = new JsonObject();
        rotation.addProperty("yaw", botPlayer.getYaw());
        rotation.addProperty("pitch", botPlayer.getPitch());
        result.add("rotation", rotation);

        // 经验
        result.addProperty("experience", botPlayer.totalExperience);
        result.addProperty("level", botPlayer.experienceLevel);

        // 维度
        result.addProperty("dimension", botPlayer.getWorld().getRegistryKey().getValue().toString());

        // 是否存活
        result.addProperty("alive", botPlayer.isAlive());

        return result;
    }

    /**
     * 获取 Bot 实体（供 ActionExecutor 使用）
     */
    public static ServerPlayerEntity getBot() {
        return botPlayer;
    }

    /**
     * Bot 是否已生成
     */
    public static boolean isSpawned() {
        return botPlayer != null;
    }

    /**
     * 获取 Bot 名字
     */
    public static String getBotName() {
        return botName;
    }
}
