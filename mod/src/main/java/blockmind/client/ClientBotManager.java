package blockmind.client;

import com.google.gson.JsonObject;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.network.ClientPlayerEntity;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClientBotManager {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.client.bot");
    private static boolean spawned = false;

    public static synchronized JsonObject spawn(String name) {
        JsonObject result = new JsonObject();
        ClientPlayerEntity player = MinecraftClient.getInstance().player;
        if (player == null) {
            result.addProperty("success", false);
            result.addProperty("error", "Player not in game");
            return result;
        }

        spawned = true;
        result.addProperty("success", true);
        result.addProperty("name", player.getName().getString());
        JsonObject pos = new JsonObject();
        pos.addProperty("x", player.getX());
        pos.addProperty("y", player.getY());
        pos.addProperty("z", player.getZ());
        result.add("position", pos);
        result.addProperty("mode", "client");
        LOGGER.info("[BlockMind-Client] Using local player: {}", player.getName().getString());
        return result;
    }

    public static synchronized JsonObject despawn() {
        JsonObject result = new JsonObject();
        spawned = false;
        result.addProperty("success", true);
        result.addProperty("details", "Released local player control");
        return result;
    }

    public static boolean isSpawned() { return spawned; }

    public static Object getBot() {
        return MinecraftClient.getInstance().player;
    }
}
