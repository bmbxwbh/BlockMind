package blockmind.bot;

import com.mojang.authlib.GameProfile;
import net.minecraft.network.packet.c2s.common.SyncedClientOptions;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;

/**
 * BotPlayer — 继承 ServerPlayerEntity，最小化 tick 避免网络 NPE
 * 不设置 networkHandler，teleport 使用父类实现（会 NPE 所以覆盖）
 */
public class BotPlayer extends ServerPlayerEntity {

    public BotPlayer(MinecraftServer server, ServerWorld world, GameProfile profile, SyncedClientOptions options) {
        super(server, world, profile, options);
        // networkHandler 保持 null
    }

    @Override
    public void tick() {
        // 最小化 tick — 跳过所有需要 networkHandler 的逻辑
        // 只更新实体基础状态
        this.tickPortalCooldown();
    }

    @Override
    public void requestTeleport(double x, double y, double z, float yaw, float pitch) {
        // 直接设置位置，不发送网络包
        this.setPos(x, y, z);
        this.setYaw(yaw);
        this.setPitch(pitch);
    }
}
