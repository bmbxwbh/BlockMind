package blockmind.client;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.network.ClientPlayerEntity;
import net.minecraft.util.math.BlockPos;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClientActionExecutor {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.client.executor");

    private static ClientPlayerEntity getPlayer() {
        MinecraftClient client = MinecraftClient.getInstance();
        return client != null ? client.player : null;
    }

    public static JsonObject move(String body) {
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();
        ClientPlayerEntity player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        double x = json.get("x").getAsDouble();
        double y = json.get("y").getAsDouble();
        double z = json.get("z").getAsDouble();

        try {
            player.setPos(x, y, z);
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
        ClientPlayerEntity player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

        try {
            MinecraftClient client = MinecraftClient.getInstance();
            var interactionManager = client.interactionManager;
            if (interactionManager != null) {
                BlockPos pos = new BlockPos(x, y, z);
                interactionManager.attackBlock(pos, net.minecraft.util.math.Direction.UP);
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
        ClientPlayerEntity player = getPlayer();
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
        ClientPlayerEntity player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        result.addProperty("success", true);
        result.addProperty("details", "Eat requested [client-side]");
        return result;
    }

    public static JsonObject look(String body) {
        JsonObject json = JsonParser.parseString(body).getAsJsonObject();
        ClientPlayerEntity player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        double x = json.get("x").getAsDouble();
        double y = json.get("y").getAsDouble();
        double z = json.get("z").getAsDouble();

        try {
            double dx = x - player.getX();
            double dy = y - player.getY();
            double dz = z - player.getZ();
            double dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
            if (dist > 0) {
                float yaw = (float)(Math.atan2(-dx, dz) * 180.0 / Math.PI);
                float pitch = (float)(Math.atan2(-dy, Math.sqrt(dx*dx + dz*dz)) * 180.0 / Math.PI);
                player.setYaw(yaw);
                player.setPitch(pitch);
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
        ClientPlayerEntity player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        String message = json.get("message").getAsString();
        try {
            player.sendChatMessage(message, null);
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
        ClientPlayerEntity player = getPlayer();
        JsonObject result = new JsonObject();
        if (player == null) { result.addProperty("success", false); result.addProperty("error", "No player"); return result; }

        result.addProperty("success", true);
        result.addProperty("details", "Attack requested [client-side]");
        return result;
    }
}
