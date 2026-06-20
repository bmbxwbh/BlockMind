package blockmind.client;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Method;

public class ClientActionExecutor {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.client.executor");

    private static Object getPlayer() {
        return ClientReflect.getPlayer();
    }

    public static JsonObject move(String body) {
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();
        Object player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        double x = json.get("x").getAsDouble();
        double y = json.get("y").getAsDouble();
        double z = json.get("z").getAsDouble();

        try {
            ClientReflect.invoke(player, "setPos", new Class<?>[]{double.class, double.class, double.class}, x, y, z);
            result.addProperty("success", true);
            result.addProperty("details", String.format("Moved to (%.1f, %.1f, %.1f)", x, y, z));
        } catch (Exception e) {
            result.addProperty("success", false);
            result.addProperty("error", e.getMessage());
        }
        return result;
    }

    public static JsonObject dig(String body) {
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();
        Object player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

        try {
            Object client = ClientReflect.getClient();
            Object im = ClientReflect.getField(client, "interactionManager");
            if (im != null) {
                Class<?> blockPosClass = Class.forName("net.minecraft.util.math.BlockPos");
                Object pos = blockPosClass.getConstructor(int.class, int.class, int.class).newInstance(x, y, z);

                Class<?> directionClass = Class.forName("net.minecraft.util.math.Direction");
                Object up = directionClass.getField("UP").get(null);

                ClientReflect.invoke(im, "attackBlock", new Class<?>[]{blockPosClass, directionClass}, pos, up);
                result.addProperty("success", true);
                result.addProperty("details", String.format("Dig at (%d, %d, %d)", x, y, z));
            } else {
                result.addProperty("success", false);
                result.addProperty("error", "No interaction manager");
            }
        } catch (Exception e) {
            result.addProperty("success", false);
            result.addProperty("error", e.getMessage());
        }
        return result;
    }

    public static JsonObject place(String body) {
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();
        Object player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

        result.addProperty("success", true);
        result.addProperty("details", String.format("Place at (%d, %d, %d) [client-side simulated]", x, y, z));
        return result;
    }

    public static JsonObject eat(String body) {
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();
        Object player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        result.addProperty("success", true);
        result.addProperty("details", "Eat requested [client-side]");
        return result;
    }

    public static JsonObject look(String body) {
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();
        Object player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        double x = json.get("x").getAsDouble();
        double y = json.get("y").getAsDouble();
        double z = json.get("z").getAsDouble();

        try {
            double px = ClientReflect.invokeDouble(player, "getX");
            double py = ClientReflect.invokeDouble(player, "getY");
            double pz = ClientReflect.invokeDouble(player, "getZ");
            double dx = x - px;
            double dy = y - py;
            double dz = z - pz;
            double dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
            if (dist > 0) {
                float yaw = (float) (Math.atan2(-dx, dz) * 180.0 / Math.PI);
                float pitch = (float) (Math.atan2(-dy, Math.sqrt(dx * dx + dz * dz)) * 180.0 / Math.PI);
                ClientReflect.invoke(player, "setYaw", new Class<?>[]{float.class}, yaw);
                ClientReflect.invoke(player, "setPitch", new Class<?>[]{float.class}, pitch);
            }
            result.addProperty("success", true);
        } catch (Exception e) {
            result.addProperty("success", false);
            result.addProperty("error", e.getMessage());
        }
        return result;
    }

    public static JsonObject chat(String body) {
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();
        Object player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        String message = json.get("message").getAsString();
        try {
            for (Method m : player.getClass().getMethods()) {
                if ("sendChatMessage".equals(m.getName()) && m.getParameterCount() >= 1) {
                    Class<?>[] params = m.getParameterTypes();
                    if (params[0] == String.class) {
                        if (params.length == 1) {
                            m.invoke(player, message);
                        } else {
                            m.invoke(player, message, null);
                        }
                        break;
                    }
                }
            }
            result.addProperty("success", true);
            result.addProperty("details", "Sent: " + message);
        } catch (Exception e) {
            result.addProperty("success", false);
            result.addProperty("error", e.getMessage());
        }
        return result;
    }

    public static JsonObject attack(String body) {
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();
        Object player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        result.addProperty("success", true);
        result.addProperty("details", "Attack requested [client-side]");
        return result;
    }
}
