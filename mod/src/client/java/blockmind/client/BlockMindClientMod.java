package blockmind.client;

import blockmind.BlockMindMod;
import blockmind.api.BlockMindHttpServer;
import blockmind.compat.VersionCompat;
import net.fabricmc.api.ClientModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

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

        registerLifecycleEvents();
    }

    private void registerLifecycleEvents() {
        try {
            Class<?> eventsClass = Class.forName("net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientLifecycleEvents");

            registerFabricEvent(eventsClass, "CLIENT_STARTED", () -> {
                LOGGER.info("[BlockMind-Client] Client started, launching HTTP API...");

                startHttpServer();
                new ClientEventListener(httpServer).register();
                running = true;

                LOGGER.info("[BlockMind-Client] ✅ BlockMind Client ready! API on port {}", BlockMindMod.HTTP_PORT);
                LOGGER.info("[BlockMind-Client] Controlling local player");
            });

            registerFabricEvent(eventsClass, "CLIENT_STOPPING", () -> {
                LOGGER.info("[BlockMind-Client] Client stopping...");
                stopHttpServer();
                running = false;
            });
        } catch (Exception e) {
            LOGGER.warn("[BlockMind-Client] Could not register lifecycle events: {}", e.getMessage());
        }
    }

    @SuppressWarnings("unchecked")
    private void registerFabricEvent(Class<?> eventsClass, String fieldName, Runnable handler) throws Exception {
        Object eventObj = eventsClass.getField(fieldName).get(null);

        Field typeField = eventObj.getClass().getDeclaredField("type");
        typeField.setAccessible(true);
        Class<?> handlerInterface = (Class<?>) typeField.get(eventObj);

        Object proxy = Proxy.newProxyInstance(
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

        Method registerMethod = eventObj.getClass().getMethod("register", Object.class);
        registerMethod.invoke(eventObj, proxy);
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
