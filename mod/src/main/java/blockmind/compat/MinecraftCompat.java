package blockmind.compat;

import com.mojang.authlib.GameProfile;

import java.util.UUID;
import java.util.function.BiConsumer;

/**
 * 版本无关的 Minecraft 操作接口
 * 不同 MC 版本有各自的实现（V120Compat / V121Compat / V26Compat）
 */
public interface MinecraftCompat {

    // ── 核心操作 ──

    /** 创建假玩家 (BotPlayer) */
    Object createPlayer(Object server, Object world, GameProfile profile);

    /** 注册聊天事件监听 */
    void registerChatListener(BiConsumer<String, String> handler);

    /** 获取 MC 版本字符串 */
    String getVersionString();

    // ── 玩家属性 ──

    String getPlayerName(Object player);
    String getMessageText(Object message);
    float getHealth(Object player);
    double getX(Object player);
    double getY(Object player);
    double getZ(Object player);
    float getYaw(Object player);
    float getPitch(Object player);
    boolean isAlive(Object player);
    UUID getUuid(Object player);
    String getDimension(Object player);
    int[] getBlockPos(Object player);
    long getWorldTimeOfDay(Object player);
    boolean isBotPlayer(Object player);

    // ── 玩家操作 ──

    void discard(Object player);
    void setPos(Object player, double x, double y, double z);
    void refreshPositionAndAngles(Object player, double x, double y, double z, float yaw, float pitch);
    void setRotation(Object player, float yaw, float pitch);

    // ── 经验/饥饿 ──

    int getFoodLevel(Object player);
    float getSaturationLevel(Object player);
    int getTotalExperience(Object player);
    int getExperienceLevel(Object player);
}
