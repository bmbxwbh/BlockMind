package blockmind.bot;

import com.mojang.authlib.GameProfile;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;

/**
 * BotPlayer — 继承 ServerPlayerEntity，覆盖 tick 避免网络 NPE
 *
 * 兼容 MC 1.20.0 ~ 1.21.x：
 * - 1.20.0-1.20.1: ServerPlayerEntity 3 参数构造函数
 * - 1.20.2+: ServerPlayerEntity 4 参数构造函数 (含 SyncedClientOptions)
 *
 * 通过 VersionCompat 工厂方法创建，不直接暴露构造函数。
 */
public class BotPlayer extends ServerPlayerEntity {

    /**
     * 内部构造函数 — 由 VersionCompat.createPlayer() 反射调用
     * 直接使用 4 参数版本，VersionCompat 会处理版本差异
     */
    public BotPlayer(MinecraftServer server, ServerWorld world, GameProfile profile, Object... args) {
        super(server, world, profile,
              args.length > 0 && args[0] != null
                  ? (net.minecraft.network.packet.c2s.common.SyncedClientOptions) args[0]
                  : createDefaultOptions());
    }

    /**
     * 创建默认 SyncedClientOptions — 兼容不同版本
     */
    private static net.minecraft.network.packet.c2s.common.SyncedClientOptions createDefaultOptions() {
        try {
            return net.minecraft.network.packet.c2s.common.SyncedClientOptions.createDefault();
        } catch (NoClassDefFoundError e) {
            // MC 1.20.0-1.20.1 没有这个类，不应该走到这里
            throw new UnsupportedOperationException(
                "SyncedClientOptions not available in this MC version. Use VersionCompat.createPlayer() instead.", e);
        }
    }

    @Override
    public void tick() {
        // 最小化 tick — 跳过所有需要 networkHandler 的逻辑
        this.tickPortalCooldown();
    }
}
