package blockmind.client;

import blockmind.BlockMindMod;
import blockmind.api.BlockMindHttpServer;
import blockmind.compat.VersionCompat;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientLifecycleEvents;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BlockMindClientMod implements ClientModInitializer {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.client");
    private static BlockMindHttpServer httpServer;
    private static volatile boolean running = false;

    @Override
    public void onInitializeClient() {
        LOGGER.info("========================================");
        LOGGER.info("  BlockMind Mod v1.2.0 Loading...");
        LOGGER.info("  MC Version: {}", VersionCompat.getVersionString());
        LOGGER.info("  Mode: CLIENT");
        LOGGER.info("========================================");

        ClientLifecycleEvents.CLIENT_STARTED.register(client -> {
            LOGGER.info("[BlockMind-Client] Client started, launching HTTP API...");

            startHttpServer();
            new ClientEventListener(httpServer).register();
            running = true;

            LOGGER.info("[BlockMind-Client] ✅ BlockMind Client ready! API on port {}", BlockMindMod.HTTP_PORT);
            LOGGER.info("[BlockMind-Client] Controlling local player");
        });

        ClientLifecycleEvents.CLIENT_STOPPING.register(client -> {
            LOGGER.info("[BlockMind-Client] Client stopping...");
            stopHttpServer();
            running = false;
        });
    }

    private void startHttpServer() {
        try {
            String apiToken = System.getenv("BLOCKMIND_API_TOKEN");
            httpServer = new BlockMindHttpServer(BlockMindMod.HTTP_PORT, apiToken != null ? apiToken : "");
            httpServer.start();
            LOGGER.info("[BlockMind-Client] HTTP API started on port {}", BlockMindMod.HTTP_PORT);
        } catch (Exception e) {
            LOGGER.error("[BlockMind-Client] Failed to start HTTP API: {}", e.getMessage());
        }
    }

    private void stopHttpServer() {
        if (httpServer != null) {
            httpServer.stop();
            LOGGER.info("[BlockMind-Client] HTTP API stopped");
        }
    }

    public static boolean isRunning() { return running; }
    public static BlockMindHttpServer getHttpServer() { return httpServer; }
}
