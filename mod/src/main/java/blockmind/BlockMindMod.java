package blockmind;

import blockmind.api.BlockMindHttpServer;
import blockmind.bot.BotManager;
import blockmind.collector.StateCollector;
import blockmind.executor.ActionExecutor;
import blockmind.event.EventListener;
import blockmind.compat.VersionCompat;
import net.fabricmc.api.DedicatedServerModInitializer;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * BlockMind Fabric Mod 入口
 *
 * 职责：
 * 1. 启动 HTTP API 服务（端口 25580）
 * 2. 注册游戏事件监听
 * 3. 管理 Mod 生命周期
 * 4. 管理 Bot（FakePlayer）生命周期
 */
public class BlockMindMod implements DedicatedServerModInitializer {

    public static final String MOD_ID = "blockmind";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);
    public static final int HTTP_PORT = 25580;

    private static BlockMindHttpServer httpServer;
    private static boolean running = false;

    @Override
    public void onInitializeServer() {
        LOGGER.info("========================================");
        LOGGER.info("  BlockMind Mod v1.1.0 Loading...");
        LOGGER.info("  MC Version: {} (detected by VersionCompat)", VersionCompat.getVersionString());
        LOGGER.info("  SyncedClientOptions: {}", VersionCompat.hasSyncedClientOptions() ? "YES" : "NO (legacy mode)");
        LOGGER.info("  [NEW] FakePlayer Bot Support");
        LOGGER.info("========================================");

        // 注册服务器启动/停止事件
        ServerLifecycleEvents.SERVER_STARTED.register(server -> {
            LOGGER.info("[BlockMind] Server started, launching HTTP API...");

            // 初始化所有模块
            StateCollector.setServer(server);
            ActionExecutor.setServer(server);
            BotManager.setServer(server);

            startHttpServer();
            new EventListener().register();
            running = true;

            LOGGER.info("[BlockMind] ✅ BlockMind Mod ready! API on port {}", HTTP_PORT);
            LOGGER.info("[BlockMind] Bot management: POST /api/bot/spawn to create a bot");
        });

        ServerLifecycleEvents.SERVER_STOPPING.register(server -> {
            LOGGER.info("[BlockMind] Server stopping...");
            // 先清理 Bot
            if (BotManager.isSpawned()) {
                BotManager.despawn();
            }
            stopHttpServer();
            running = false;
        });
    }

    private void startHttpServer() {
        try {
            // 读取 API Token（优先环境变量，其次配置文件）
            String apiToken = System.getenv("BLOCKMIND_API_TOKEN");
            if (apiToken == null || apiToken.isEmpty()) {
                try {
                    java.util.Properties props = new java.util.Properties();
                    java.io.File cfg = new java.io.File("config/blockmind.properties");
                    if (cfg.exists()) {
                        props.load(new java.io.FileInputStream(cfg));
                        apiToken = props.getProperty("api_token", "");
                    }
                } catch (Exception ignored) {}
            }
            httpServer = new BlockMindHttpServer(HTTP_PORT, apiToken);
            httpServer.start();
            LOGGER.info("[BlockMind] HTTP API started on port {}", HTTP_PORT);
        } catch (Exception e) {
            LOGGER.error("[BlockMind] Failed to start HTTP API: {}", e.getMessage());
        }
    }

    private void stopHttpServer() {
        if (httpServer != null) {
            httpServer.stop();
            LOGGER.info("[BlockMind] HTTP API stopped");
        }
    }

    public static boolean isRunning() {
        return running;
    }

    public static BlockMindHttpServer getHttpServer() {
        return httpServer;
    }
}
