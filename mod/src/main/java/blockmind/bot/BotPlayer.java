package blockmind.bot;

import com.mojang.authlib.GameProfile;
import net.minecraft.network.packet.c2s.common.SyncedClientOptions;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;

/**
 * BotPlayer — 继承 ServerPlayerEntity，覆盖所有网络相关方法
 * 不设置 networkHandler，避免所有 NPE
 */
public class BotPlayer extends ServerPlayerEntity {

    public BotPlayer(MinecraftServer server, ServerWorld world, GameProfile profile, SyncedClientOptions options) {
        super(server, world, profile, options);
    }

    @Override
    public void tick() {
        // 最小化 tick — 跳过所有需要 networkHandler 的逻辑
        this.tickPortalCooldown();
    }

    @Override
    public void teleport(double x, double y, double z) {
        // 直接设置位置，不发送网络包
        this.setPos(x, y, z);
    }

    @Override
    public boolean teleport(double x, double y, double z, boolean dest) {
        this.setPos(x, y, z);
        return true;
    }

    @Override
    public void requestTeleport(double x, double y, double z) {
        this.setPos(x, y, z);
    }

    @Override
    public void requestTeleport(double x, double y, double z, float yaw, float pitch) {
        this.setPos(x, y, z);
        this.setYaw(yaw);
        this.setPitch(pitch);
    }
}
