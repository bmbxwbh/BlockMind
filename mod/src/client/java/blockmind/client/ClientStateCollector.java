package blockmind.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.network.ClientPlayerEntity;
import net.minecraft.entity.Entity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.util.math.Box;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Collection;

public class ClientStateCollector {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.client.collector");

    public static JsonObject getPlayerStatus() {
        ClientPlayerEntity player = getPlayer();
        JsonObject status = new JsonObject();
        if (player == null) {
            status.addProperty("health", 0);
            status.addProperty("hunger", 0);
            status.addProperty("position", "(0, 64, 0)");
            status.addProperty("dimension", "unknown");
            status.addProperty("weather", "unknown");
            return status;
        }

        status.addProperty("health", player.getHealth());
        status.addProperty("hunger", player.getHungerManager().getFoodLevel());
        JsonObject pos = new JsonObject();
        pos.addProperty("x", player.getX());
        pos.addProperty("y", player.getY());
        pos.addProperty("z", player.getZ());
        status.add("position", pos);
        status.addProperty("dimension", player.getWorld().getRegistryKey().getValue().toString());
        status.addProperty("weather", player.getWorld().isRaining() ? "rain" : "clear");
        return status;
    }

    public static JsonObject getInventory() {
        ClientPlayerEntity player = getPlayer();
        JsonObject inv = new JsonObject();
        if (player == null) {
            inv.addProperty("empty_slots", 36);
            inv.add("items", new JsonArray());
            return inv;
        }

        JsonArray items = new JsonArray();
        int usedSlots = 0;
        for (int i = 0; i < player.getInventory().size(); i++) {
            var stack = player.getInventory().getStack(i);
            if (!stack.isEmpty()) {
                usedSlots++;
                JsonObject item = new JsonObject();
                item.addProperty("slot", i);
                item.addProperty("name", stack.getItem().toString());
                item.addProperty("count", stack.getCount());
                items.add(item);
            }
        }
        inv.addProperty("empty_slots", 36 - usedSlots);
        inv.add("items", items);
        return inv;
    }

    public static JsonObject getEntities(int radius) {
        ClientPlayerEntity player = getPlayer();
        JsonObject result = new JsonObject();
        JsonArray entities = new JsonArray();

        if (player != null && player.getWorld() != null) {
            Box box = player.getBoundingBox().expand(radius);
            Collection<Entity> nearby = player.getWorld().getEntitiesByClass(Entity.class, box, e -> e != player);
            for (Entity e : nearby) {
                JsonObject entity = new JsonObject();
                entity.addProperty("id", e.getId());
                entity.addProperty("type", e.getType().toString());
                entity.addProperty("x", e.getX());
                entity.addProperty("y", e.getY());
                entity.addProperty("z", e.getZ());
                entity.addProperty("health", e instanceof PlayerEntity pe ? pe.getHealth() : 0);
                entities.add(entity);
            }
        }

        result.add("entities", entities);
        return result;
    }

    public static JsonObject getBlocks(int radius) {
        JsonObject result = new JsonObject();
        result.add("blocks", new JsonArray());
        return result;
    }

    private static ClientPlayerEntity getPlayer() {
        MinecraftClient client = MinecraftClient.getInstance();
        return client != null ? client.player : null;
    }
}
