package blockmind;

import blockmind.api.BlockMindHttpServer;
import blockmind.bot.BotManager;
import blockmind.collector.StateCollector;
import blockmind.executor.ActionExecutor;
import blockmind.event.EventListener;
import blockmind.pathfinding.PathfinderHandler;
import blockmind.compat.VersionCompat;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BlockMindMod implements ModInitializer {

    public static final String MOD_ID = "blockmind";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);
    public static final int HTTP_PORT = 25580;

    private static BlockMindHttpServer httpServer;
    private static volatile boolean running = false;

    @Override
    public void onInitialize() {
        LOGGER.info("========================================");
        LOGGER.info("  BlockMind Mod v1.2.0 Loading...");
        LOGGER.info("  MC Version: {} (detected by VersionCompat)", VersionCompat.getVersionString());
        LOGGER.info("  Compat impl: {}", VersionCompat.getCompat().getClass().getSimpleName());

        boolean isClient = false;
        try {
            Class.forName("net.minecraft.client.MinecraftClient");
            isClient = true;
        } catch (ClassNotFoundException e) {
            isClient = false;
        }

        if (isClient) {
            LOGGER.info("  Mode: CLIENT (singleplayer/LAN)");
            initClient();
        } else {
            LOGGER.info("  Mode: SERVER (dedicated)");
        }

        ServerLifecycleEvents.SERVER_STARTED.register(server -> {
            LOGGER.info("[BlockMind] Server started, launching HTTP API...");

            Object srv = server;
            StateCollector.setServer(srv);
            ActionExecutor.setServer(srv);
            BotManager.setServer(srv);
            PathfinderHandler.setServer(srv);

            startHttpServer();
            new EventListener().register();
            running = true;

            LOGGER.info("[BlockMind] BlockMind Mod ready! API on port {}", HTTP_PORT);
        });

        ServerLifecycleEvents.SERVER_STOPPING.register(server -> {
            LOGGER.info("[BlockMind] Server stopping...");
            if (BotManager.isSpawned()) {
                BotManager.despawn();
            }
            stopHttpServer();
            running = false;
        });

        LOGGER.info("========================================");
    }

    private void initClient() {
        try {
            Class<?> eventsClass = Class.forName("net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientLifecycleEvents");

            registerClientEvent(eventsClass, "CLIENT_STARTED", () -> {
                LOGGER.info("[BlockMind-Client] Client started, launching HTTP API...");
                startHttpServer();
                try { new EventListener().register(); } catch (Exception e) { LOGGER.warn("[BlockMind-Client] Event listener failed: {}", e.getMessage()); }
                running = true;
                LOGGER.info("[BlockMind-Client] BlockMind Client ready! API on port {}", HTTP_PORT);
            });

            registerClientEvent(eventsClass, "CLIENT_STOPPING", () -> {
                LOGGER.info("[BlockMind-Client] Client stopping...");
                stopHttpServer();
                running = false;
            });

        } catch (Exception e) {
            LOGGER.warn("[BlockMind-Client] Client init failed: {}", e.getMessage());
        }
    }

    @SuppressWarnings("unchecked")
    private void registerClientEvent(Class<?> eventsClass, String fieldName, Runnable handler) {
        try {
            Object eventObj = eventsClass.getField(fieldName).get(null);
            java.lang.reflect.Field typeField = eventObj.getClass().getDeclaredField("type");
            typeField.setAccessible(true);
            Class<?> handlerInterface = (Class<?>) typeField.get(eventObj);

            Object proxy = java.lang.reflect.Proxy.newProxyInstance(
                handlerInterface.getClassLoader(),
                new Class<?>[]{handlerInterface},
                (p, method, args) -> {
                    if ("toString".equals(method.getName())) return "BlockMindHandler";
                    if ("hashCode".equals(method.getName())) return System.identityHashCode(p);
                    if ("equals".equals(method.getName())) return p == args[0];
                    handler.run();
                    return null;
                }
            );

            java.lang.reflect.Method registerMethod = eventObj.getClass().getMethod("register", Object.class);
            registerMethod.invoke(eventObj, proxy);
        } catch (Exception e) {
            LOGGER.warn("[BlockMind-Client] Could not register {}: {}", fieldName, e.getMessage());
        }
    }

    private void startHttpServer() {
        try {
            String apiToken = System.getenv("BLOCKMIND_API_TOKEN");
            if (apiToken == null || apiToken.isEmpty()) {
                try {
                    java.util.Properties props = new java.util.Properties();
                    java.io.File cfg = new java.io.File("config/blockmind.properties");
                    if (cfg.exists()) {
                        try (java.io.FileInputStream fis = new java.io.FileInputStream(cfg)) {
                            props.load(fis);
                        }
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
