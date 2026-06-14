package blockmind.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.Collection;

public class ClientStateCollector {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.client.collector");

    public static JsonObject getPlayerStatus() {
        Object player = getPlayer();
        JsonObject status = new JsonObject();
        if (player == null) {
            status.addProperty("health", 0);
            status.addProperty("hunger", 0);
            status.addProperty("position", "(0, 64, 0)");
            status.addProperty("dimension", "unknown");
            status.addProperty("weather", "unknown");
            return status;
        }

        status.addProperty("health", ClientReflect.invokeFloat(player, "getHealth"));
        Object hungerManager = ClientReflect.invoke(player, "getHungerManager");
        int hunger = hungerManager != null ? ClientReflect.invokeInt(hungerManager, "getFoodLevel") : 0;
        status.addProperty("hunger", hunger);

        JsonObject pos = new JsonObject();
        pos.addProperty("x", ClientReflect.invokeDouble(player, "getX"));
        pos.addProperty("y", ClientReflect.invokeDouble(player, "getY"));
        pos.addProperty("z", ClientReflect.invokeDouble(player, "getZ"));
        status.add("position", pos);

        Object world = ClientReflect.invoke(player, "getWorld");
        String dimension = "unknown";
        String weather = "unknown";
        if (world != null) {
            Object registryKey = ClientReflect.invoke(world, "getRegistryKey");
            if (registryKey != null) {
                Object value = ClientReflect.invoke(registryKey, "getValue");
                if (value != null) dimension = value.toString();
            }
            boolean isRaining = ClientReflect.invokeBool(world, "isRaining");
            weather = isRaining ? "rain" : "clear";
        }
        status.addProperty("dimension", dimension);
        status.addProperty("weather", weather);
        return status;
    }

    public static JsonObject getInventory() {
        Object player = getPlayer();
        JsonObject inv = new JsonObject();
        if (player == null) {
            inv.addProperty("empty_slots", 36);
            inv.add("items", new JsonArray());
            return inv;
        }

        try {
            Object inventory = ClientReflect.invoke(player, "getInventory");
            if (inventory == null) {
                inv.addProperty("empty_slots", 36);
                inv.add("items", new JsonArray());
                return inv;
            }

            JsonArray items = new JsonArray();
            int usedSlots = 0;
            int size = ClientReflect.invokeInt(inventory, "size");
            for (int i = 0; i < size; i++) {
                Object stack = ClientReflect.invoke(inventory, "getStack", new Class<?>[]{int.class}, i);
                if (stack != null && !ClientReflect.invokeBool(stack, "isEmpty")) {
                    usedSlots++;
                    JsonObject item = new JsonObject();
                    item.addProperty("slot", i);
                    Object stackItem = ClientReflect.invoke(stack, "getItem");
                    item.addProperty("name", stackItem != null ? stackItem.toString() : "unknown");
                    item.addProperty("count", ClientReflect.invokeInt(stack, "getCount"));
                    items.add(item);
                }
            }
            inv.addProperty("empty_slots", 36 - usedSlots);
            inv.add("items", items);
        } catch (Exception e) {
            LOGGER.debug("getInventory failed: {}", e.getMessage());
            inv.addProperty("empty_slots", 36);
            inv.add("items", new JsonArray());
        }
        return inv;
    }

    public static JsonObject getEntities(int radius) {
        Object player = getPlayer();
        JsonObject result = new JsonObject();
        JsonArray entities = new JsonArray();

        if (player != null) {
            try {
                Object world = ClientReflect.invoke(player, "getWorld");
                if (world != null) {
                    Class<?> entityClass = Class.forName("net.minecraft.entity.Entity");
                    Class<?> boxClass = Class.forName("net.minecraft.util.math.Box");
                    Class<?> predicateClass = Class.forName("java.util.function.Predicate");

                    Object box = ClientReflect.invoke(player, "getBoundingBox");
                    Object expandedBox = ClientReflect.invoke(box, "expand", new Class<?>[]{double.class}, (double) radius);

                    Object filter = Proxy.newProxyInstance(
                        predicateClass.getClassLoader(),
                        new Class<?>[]{predicateClass},
                        (p, method, args) -> {
                            if ("test".equals(method.getName())) return args[0] != player ? Boolean.TRUE : Boolean.FALSE;
                            if ("toString".equals(method.getName())) return "BlockMindEntityFilter";
                            if ("hashCode".equals(method.getName())) return System.identityHashCode(p);
                            if ("equals".equals(method.getName())) return p == args[0];
                            return null;
                        }
                    );

                    Method getEntitiesMethod = world.getClass().getMethod("getEntitiesByClass", Class.class, boxClass, predicateClass);
                    Collection<?> nearby = (Collection<?>) getEntitiesMethod.invoke(world, entityClass, expandedBox, filter);

                    if (nearby != null) {
                        for (Object e : nearby) {
                            JsonObject entity = new JsonObject();
                            entity.addProperty("id", ClientReflect.invokeInt(e, "getId"));
                            Object type = ClientReflect.invoke(e, "getType");
                            entity.addProperty("type", type != null ? type.toString() : "unknown");
                            entity.addProperty("x", ClientReflect.invokeDouble(e, "getX"));
                            entity.addProperty("y", ClientReflect.invokeDouble(e, "getY"));
                            entity.addProperty("z", ClientReflect.invokeDouble(e, "getZ"));

                            Class<?> playerEntityClass = Class.forName("net.minecraft.entity.player.PlayerEntity");
                            if (playerEntityClass.isInstance(e)) {
                                entity.addProperty("health", ClientReflect.invokeFloat(e, "getHealth"));
                            } else {
                                entity.addProperty("health", 0);
                            }
                            entities.add(entity);
                        }
                    }
                }
            } catch (Exception e) {
                LOGGER.debug("getEntities failed: {}", e.getMessage());
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

    private static Object getPlayer() {
        return ClientReflect.getPlayer();
    }
}
