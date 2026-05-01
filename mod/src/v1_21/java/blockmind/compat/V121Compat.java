package blockmind.compat;

import com.mojang.authlib.GameProfile;
import net.fabricmc.fabric.api.message.v1.ServerMessageEvents;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.network.message.SignedMessage;

import java.lang.reflect.Constructor;
import java.util.UUID;
import java.util.function.BiConsumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * MinecraftCompat implementation for MC 1.21.x using Yarn mappings.
 *
 * Source set: src/v1_21/java — only compiled when targeting MC 1.21.x
 *
 * 1.21.x uses the same Yarn-mapped class names as 1.20.x but the
 * ServerPlayerEntity constructor always requires SyncedClientOptions.
 */
public class V121Compat implements MinecraftCompat {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.compat.v121");

    @Override
    public Object createPlayer(Object server, Object world, GameProfile profile) {
        MinecraftServer mcServer = (MinecraftServer) server;
        ServerWorld mcWorld = (ServerWorld) world;

        try {
            // MC 1.21.x always has SyncedClientOptions
            Class<?> syncedClass = Class.forName("net.minecraft.network.packet.c2s.common.SyncedClientOptions");
            Object defaultOptions = syncedClass.getMethod("createDefault").invoke(null);
            Constructor<?> ctor = ServerPlayerEntity.class.getConstructor(
                    MinecraftServer.class, ServerWorld.class, GameProfile.class, syncedClass);
            return ctor.newInstance(mcServer, mcWorld, profile, defaultOptions);
        } catch (Exception e) {
            throw new RuntimeException("Failed to create ServerPlayerEntity for MC 1.21.x", e);
        }
    }

    @Override
    public void registerChatListener(BiConsumer<String, String> handler) {
        ServerMessageEvents.CHAT_MESSAGE.register((message, sender, params) -> {
            try {
                String playerName = sender.getName().getString();
                String text = message.getContent().getString();
                handler.accept(playerName, text);
            } catch (Exception e) {
                LOGGER.debug("[BlockMind] Chat event parse error: {}", e.getMessage());
            }
        });
        LOGGER.info("[BlockMind] Chat event listener registered (V121Compat)");
    }

    @Override
    public String getPlayerName(Object player) {
        return ((ServerPlayerEntity) player).getName().getString();
    }

    @Override
    public String getMessageText(Object message) {
        if (message instanceof SignedMessage signed) {
            return signed.getContent().getString();
        }
        return message.toString();
    }

    @Override
    public String getVersionString() {
        try {
            Class<?> sharedConstants = Class.forName("net.minecraft.SharedConstants");
            Object gameVersion = sharedConstants.getMethod("getGameVersion").invoke(null);
            return (String) gameVersion.getClass().getMethod("getName").invoke(gameVersion);
        } catch (Exception e) {
            return "1.21.x";
        }
    }

    // ── Player property access ──

    @Override
    public float getHealth(Object player) {
        return ((ServerPlayerEntity) player).getHealth();
    }

    @Override
    public double getX(Object player) {
        return ((ServerPlayerEntity) player).getX();
    }

    @Override
    public double getY(Object player) {
        return ((ServerPlayerEntity) player).getY();
    }

    @Override
    public double getZ(Object player) {
        return ((ServerPlayerEntity) player).getZ();
    }

    @Override
    public float getYaw(Object player) {
        return ((ServerPlayerEntity) player).getYaw();
    }

    @Override
    public float getPitch(Object player) {
        return ((ServerPlayerEntity) player).getPitch();
    }

    @Override
    public boolean isAlive(Object player) {
        return ((ServerPlayerEntity) player).isAlive();
    }

    @Override
    public void discard(Object player) {
        ((ServerPlayerEntity) player).discard();
    }

    @Override
    public void setPos(Object player, double x, double y, double z) {
        ((ServerPlayerEntity) player).setPos(x, y, z);
    }

    @Override
    public void refreshPositionAndAngles(Object player, double x, double y, double z, float yaw, float pitch) {
        ((ServerPlayerEntity) player).refreshPositionAndAngles(x, y, z, yaw, pitch);
    }

    @Override
    public void setRotation(Object player, float yaw, float pitch) {
        ServerPlayerEntity p = (ServerPlayerEntity) player;
        p.setYaw(yaw);
        p.setPitch(pitch);
    }

    @Override
    public int getFoodLevel(Object player) {
        return ((ServerPlayerEntity) player).getHungerManager().getFoodLevel();
    }

    @Override
    public float getSaturationLevel(Object player) {
        return ((ServerPlayerEntity) player).getHungerManager().getSaturationLevel();
    }

    @Override
    public int getTotalExperience(Object player) {
        return ((ServerPlayerEntity) player).totalExperience;
    }

    @Override
    public int getExperienceLevel(Object player) {
        return ((ServerPlayerEntity) player).experienceLevel;
    }

    @Override
    public UUID getUuid(Object player) {
        return ((ServerPlayerEntity) player).getUuid();
    }

    @Override
    public String getDimension(Object player) {
        return ((ServerPlayerEntity) player).getWorld().getRegistryKey().getValue().toString();
    }

    @Override
    public int[] getBlockPos(Object player) {
        var pos = ((ServerPlayerEntity) player).getBlockPos();
        return new int[]{pos.getX(), pos.getY(), pos.getZ()};
    }

    @Override
    public long getWorldTimeOfDay(Object player) {
        return ((ServerPlayerEntity) player).getWorld().getTimeOfDay();
    }

    @Override
    public boolean isBotPlayer(Object player) {
        return false;
    }
}
