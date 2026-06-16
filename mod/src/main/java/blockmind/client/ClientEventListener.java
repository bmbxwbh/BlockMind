package blockmind.client;

import blockmind.api.BlockMindHttpServer;
import com.google.gson.JsonObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

public class ClientEventListener {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.client.event");
    private BlockMindHttpServer httpServer;

    public ClientEventListener(BlockMindHttpServer httpServer) {
        this.httpServer = httpServer;
    }

    public void register() {
        try {
            Class<?> tickEvents = Class.forName("net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents");
            registerFabricEvent(tickEvents, "END_CLIENT_TICK", () -> {
            });
        } catch (Exception e) {
            LOGGER.warn("[BlockMind-Client] Could not register tick events: {}", e.getMessage());
        }

        try {
            Class<?> msgEvents = Class.forName("net.fabricmc.fabric.api.client.message.v1.ClientReceiveMessageEvents");
            Object chatEvent = msgEvents.getField("CHAT").get(null);

            Field typeField = chatEvent.getClass().getDeclaredField("type");
            typeField.setAccessible(true);
            Class<?> handlerInterface = (Class<?>) typeField.get(chatEvent);

            Object chatHandler = Proxy.newProxyInstance(
                handlerInterface.getClassLoader(),
                new Class<?>[]{handlerInterface},
                (proxy, method, args) -> {
                    if ("toString".equals(method.getName())) return "BlockMindChatHandler";
                    if ("hashCode".equals(method.getName())) return System.identityHashCode(proxy);
                    if ("equals".equals(method.getName())) return proxy == args[0];

                    if (args != null && args.length >= 2) {
                        Object message = args[0];
                        Object sender = args[1];

                        String text = message != null ? ClientReflect.invoke(message, "getString").toString() : "";
                        String senderName = "unknown";
                        if (sender != null) {
                            Object nameObj = ClientReflect.invoke(sender, "getName");
                            if (nameObj == null) nameObj = ClientReflect.invoke(sender, "getString");
                            senderName = nameObj != null ? nameObj.toString() : "unknown";
                        }

                        JsonObject event = new JsonObject();
                        event.addProperty("type", "chat");
                        JsonObject data = new JsonObject();
                        data.addProperty("player", senderName);
                        data.addProperty("message", text);
                        event.add("data", data);

                        if (httpServer != null) {
                            httpServer.broadcastEvent(event);
                        }
                    }
                    return null;
                }
            );
            Method regMethod = chatEvent.getClass().getMethod("register", Object.class);
            regMethod.invoke(chatEvent, chatHandler);
        } catch (Exception e) {
            LOGGER.warn("[BlockMind-Client] Could not register chat events: {}", e.getMessage());
        }

        LOGGER.info("[BlockMind-Client] Event listeners registered");
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
}
