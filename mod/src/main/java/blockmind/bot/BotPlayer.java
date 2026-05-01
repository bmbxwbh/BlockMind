package blockmind.bot;

import blockmind.compat.MinecraftCompat;

/**
 * BotPlayer — 版本无关的 FakePlayer 包装类
 *
 * 不再直接继承 ServerPlayerEntity（Yarn）/ ServerPlayer（Mojang），
 * 而是包装底层玩家对象，通过 MinecraftCompat 接口访问所有属性。
 *
 * 这样同一个 BotPlayer 类可以编译并运行在所有 MC 版本上：
 * - 1.20.x (Yarn mappings, ServerPlayerEntity)
 * - 1.21.x (Yarn mappings, ServerPlayerEntity)
 * - 26.x   (Mojang mappings, ServerPlayer)
 */
public class BotPlayer {

    /** 底层 MC 玩家对象（实际类型为 ServerPlayerEntity 或 ServerPlayer） */
    private final Object handle;

    /** 版本兼容层 */
    private final MinecraftCompat compat;

    /**
     * @param handle 底层 MC 玩家对象
     * @param compat 版本兼容层
     */
    public BotPlayer(Object handle, MinecraftCompat compat) {
        this.handle = handle;
        this.compat = compat;
    }

    /** 获取底层 MC 玩家对象 */
    public Object getHandle() {
        return handle;
    }

    /** 获取版本兼容层 */
    public MinecraftCompat getCompat() {
        return compat;
    }

    // ── 便捷方法（委托给 compat）──

    public float getHealth() { return compat.getHealth(handle); }
    public double getX() { return compat.getX(handle); }
    public double getY() { return compat.getY(handle); }
    public double getZ() { return compat.getZ(handle); }
    public float getYaw() { return compat.getYaw(handle); }
    public float getPitch() { return compat.getPitch(handle); }
    public boolean isAlive() { return compat.isAlive(handle); }
    public void discard() { compat.discard(handle); }
    public int getFoodLevel() { return compat.getFoodLevel(handle); }
    public float getSaturationLevel() { return compat.getSaturationLevel(handle); }
    public int getTotalExperience() { return compat.getTotalExperience(handle); }
    public int getExperienceLevel() { return compat.getExperienceLevel(handle); }
    public java.util.UUID getUuid() { return compat.getUuid(handle); }
    public String getDimension() { return compat.getDimension(handle); }
    public int[] getBlockPos() { return compat.getBlockPos(handle); }
    public String getName() { return compat.getPlayerName(handle); }
}
