package blockmind;

import blockmind.api.BlockMindHttpServer;
import blockmind.event.EventListener;
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
        LOGGER.info("  BlockMind Mod v1.0.0 Loading...");
        LOGGER.info("========================================");

        // 注册服务器启动/停止事件
        ServerLifecycleEvents.SERVER_STARTED.register(server -> {
            LOGGER.info("[BlockMind] Server started, launching HTTP API...");
            startHttpServer();
            new EventListener().register();
            running = true;
            LOGGER.info("[BlockMind] ✅ BlockMind Mod ready! API on port {}", HTTP_PORT);
        });

        ServerLifecycleEvents.SERVER_STOPPING.register(server -> {
            LOGGER.info("[BlockMind] Server stopping, shutting down...");
            stopHttpServer();
            running = false;
        });
    }

    private void startHttpServer() {
        try {
            httpServer = new BlockMindHttpServer(HTTP_PORT);
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

    public static HttpServer getHttpServer() {
        return httpServer;
    }
}
