package blockmind.bot;

import com.mojang.authlib.GameProfile;
import net.minecraft.network.packet.c2s.common.SyncedClientOptions;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;

/**
 * BotPlayer — 继承 ServerPlayerEntity，覆盖 tick 避免网络 NPE
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
}
