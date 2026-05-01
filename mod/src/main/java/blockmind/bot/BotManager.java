package blockmind.bot;

import blockmind.BlockMindMod;
import com.google.gson.JsonObject;
import com.mojang.authlib.GameProfile;
import net.minecraft.network.packet.Packet;
import net.minecraft.network.packet.c2s.common.SyncedClientOptions;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayNetworkHandler;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.text.Text;
import net.minecraft.util.math.BlockPos;

import java.lang.reflect.Field;
import java.util.UUID;

/**
 * Bot 管理器 — 管理 FakePlayer 的生命周期
 *
 * 使用 BotNetworkHandler（no-op 发包）避免 NPE。
 * Bot 可以执行所有游戏动作但不实际发送网络包。
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
            GameProfile profile = new GameProfile(BOT_UUID, botName);
            ServerWorld world = server.getOverworld();
            SyncedClientOptions clientOptions = SyncedClientOptions.createDefault();
            botPlayer = new ServerPlayerEntity(server, world, profile, clientOptions);

            // 设置初始位置
            BlockPos spawnPos = world.getSpawnPos();
            botPlayer.refreshPositionAndAngles(
                spawnPos.getX() + 0.5,
                spawnPos.getY(),
                spawnPos.getZ() + 0.5,
                0, 0
            );

            // 使用 no-op 网络处理器
            botPlayer.networkHandler = new BotNetworkHandler(server, botPlayer);

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

    public static ServerPlayerEntity getBot() {
        return botPlayer;
    }

    public static boolean isSpawned() {
        return botPlayer != null;
    }

    public static String getBotName() {
        return botName;
    }

    /**
     * No-op 网络处理器 — 所有发包操作静默忽略
     * 继承 ServerPlayNetworkHandler 以通过类型检查
     */
    /**
     * 创建带 EmbeddedChannel 的假 ClientConnection
     */
    private static net.minecraft.network.ClientConnection createFakeConnection() {
        try {
            net.minecraft.network.ClientConnection conn =
                new net.minecraft.network.ClientConnection(net.minecraft.network.NetworkSide.SERVERBOUND);
            // 反射注入 EmbeddedChannel
            for (Field f : net.minecraft.network.ClientConnection.class.getDeclaredFields()) {
                if (f.getType() == io.netty.channel.Channel.class) {
                    f.setAccessible(true);
                    f.set(conn, new io.netty.channel.embedded.EmbeddedChannel());
                    BlockMindMod.LOGGER.info("[BlockMind] FakeChannel injected: {}", f.getName());
                    return conn;
                }
            }
            BlockMindMod.LOGGER.error("[BlockMind] Cannot find Channel field");
        } catch (Exception e) {
            BlockMindMod.LOGGER.error("[BlockMind] Failed to create fake connection: {}", e.getMessage());
        }
        return new net.minecraft.network.ClientConnection(net.minecraft.network.NetworkSide.SERVERBOUND);
    }

    private static class BotNetworkHandler extends ServerPlayNetworkHandler {
        BotNetworkHandler(MinecraftServer server, ServerPlayerEntity player) {
            super(server, createFakeConnection(), player,
                  new net.minecraft.server.network.ConnectedClientData(
                      player.getGameProfile(), 0,
                      net.minecraft.network.packet.c2s.common.SyncedClientOptions.createDefault()));
        }

        @Override
        public void sendPacket(Packet<?> packet) {
            // no-op: Bot 不需要发送网络包
        }

        @Override
        public void disconnect(Text reason) {
            // no-op: Bot 不需要断开连接
        }

        @Override
        public void requestTeleport(double x, double y, double z, float yaw, float pitch) {
            // no-op: Bot 的位置由服务端直接设置
        }
    }
}
