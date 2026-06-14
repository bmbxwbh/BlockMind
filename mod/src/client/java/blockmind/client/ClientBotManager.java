package blockmind.client;

import com.google.gson.JsonObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClientBotManager {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.client.bot");
    private static boolean spawned = false;

    public static synchronized JsonObject spawn(String name) {
        JsonObject result = new JsonObject();
        Object player = ClientReflect.getPlayer();
        if (player == null) {
            result.addProperty("success", false);
            result.addProperty("error", "Player not in game");
            return result;
        }

        spawned = true;
        result.addProperty("success", true);
        Object nameObj = ClientReflect.invoke(player, "getName");
        String playerName = nameObj != null ? ClientReflect.invoke(nameObj, "getString").toString() : "unknown";
        result.addProperty("name", playerName);
        JsonObject pos = new JsonObject();
        pos.addProperty("x", ClientReflect.invokeDouble(player, "getX"));
        pos.addProperty("y", ClientReflect.invokeDouble(player, "getY"));
        pos.addProperty("z", ClientReflect.invokeDouble(player, "getZ"));
        result.add("position", pos);
        result.addProperty("mode", "client");
        LOGGER.info("[BlockMind-Client] Using local player: {}", playerName);
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
        return ClientReflect.getPlayer();
    }
}
