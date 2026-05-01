package blockmind.bot;

import com.mojang.authlib.GameProfile;
import net.minecraft.network.packet.Packet;
import net.minecraft.network.packet.c2s.common.SyncedClientOptions;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.text.Text;

/**
 * BotPlayer — 继承 ServerPlayerEntity，覆盖所有网络相关方法
 * 不设置 networkHandler，所有发包操作为 no-op
 */
public class BotPlayer extends ServerPlayerEntity {

    public BotPlayer(MinecraftServer server, ServerWorld world, GameProfile profile, SyncedClientOptions options) {
        super(server, world, profile, options);
        // networkHandler 保持 null — 所有需要它的方法都已覆盖
    }

    @Override
    public void tick() {
        // 跳过正常玩家 tick（会触发网络包发送）
        // 只做最基本的实体更新
        this.bodyTrackingIncrements.clear();
    }

    @Override
    public void teleport(double x, double y, double z, float yaw, float pitch) {
        // 直接设置位置，不发送网络包
        this.setPos(x, y, z);
        this.setYaw(yaw);
        this.setPitch(pitch);
    }

    @Override
    public void teleport(double x, double y, double z) {
        this.setPos(x, y, z);
    }

    @Override
    public void sendPacket(Packet<?> packet) {
        // no-op: Bot 不发送网络包
    }

    @Override
    public void disconnect(Text reason) {
        // no-op: Bot 不需要断开连接
    }

    @Override
    public boolean isDisconnected() {
        return false;  // Bot 永远不掉线
    }
}
