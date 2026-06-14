package blockmind.client;

import blockmind.api.BlockMindHttpServer;
import com.google.gson.JsonObject;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.message.v1.ClientReceiveMessageEvents;
import net.minecraft.client.MinecraftClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClientEventListener {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.client.event");
    private BlockMindHttpServer httpServer;

    public ClientEventListener(BlockMindHttpServer httpServer) {
        this.httpServer = httpServer;
    }

    public void register() {
        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            // Tick event — can be used for periodic tasks
        });

        ClientReceiveMessageEvents.CHAT.register((message, sender, params) -> {
            String text = message.getString();
            String senderName = sender != null ? sender.getString() : "unknown";

            JsonObject event = new JsonObject();
            event.addProperty("type", "chat");
            JsonObject data = new JsonObject();
            data.addProperty("player", senderName);
            data.addProperty("message", text);
            event.add("data", data);

            if (httpServer != null) {
                httpServer.broadcastEvent(event);
            }
        });

        LOGGER.info("[BlockMind-Client] Event listeners registered");
    }
}
