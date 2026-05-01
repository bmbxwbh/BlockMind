package blockmind.compat;

import com.mojang.authlib.GameProfile;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.UUID;
import java.util.function.BiConsumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * MinecraftCompat implementation for MC 26.x using Mojang mappings.
 *
 * Source set: src/v26/java — only compiled when targeting MC 26.x
 *
 * MC 26.x uses Mojang mappings (no Yarn), so class names differ:
 * - ServerPlayer (not ServerPlayerEntity)
 * - Component (not Text)
 * - PlayerChatMessage (not SignedMessage)
 * - ChatType.Bound (not MessageType.Parameters)
 *
 * All MC classes are accessed via reflection to avoid hard compile-time
 * dependencies that would break if mapping names shift.
 */
public class V26Compat implements MinecraftCompat {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.compat.v26");

    // Cached reflection handles
    private static Class<?> serverPlayerClass;
    private static Class<?> serverWorldClass;
    private static Class<?> minecraftServerClass;
    private static Class<?> componentClass;

    static {
        try {
            // MC 26.x Mojang-mapped class names
            serverPlayerClass = forNameSafe("net.minecraft.server.level.ServerPlayer");
            if (serverPlayerClass == null) {
                // intermediary fallback
                serverPlayerClass = forNameSafe("net.minecraft.server.network.ServerPlayerEntity");
            }
            serverWorldClass = forNameSafe("net.minecraft.server.level.ServerLevel");
            if (serverWorldClass == null) {
                serverWorldClass = forNameSafe("net.minecraft.server.world.ServerWorld");
            }
            minecraftServerClass = forNameSafe("net.minecraft.server.MinecraftServer");
            componentClass = forNameSafe("net.minecraft.network.chat.Component");
        } catch (Exception e) {
            LOGGER.error("[BlockMind] Failed to initialize V26Compat reflection", e);
        }
    }

    private static Class<?> forNameSafe(String name) {
        try {
            return Class.forName(name);
        } catch (ClassNotFoundException e) {
            return null;
        }
    }

    @Override
    public Object createPlayer(Object server, Object world, GameProfile profile) {
        try {
            // Try Mojang-mapped SyncedClientOptions (ClientInformation on 26.x)
            Class<?> clientInfoClass = null;
            Object defaultOptions = null;

            // Try different class names for the client options
            String[] clientInfoNames = {
                "net.minecraft.server.level.ClientInformation",        // Mojang 26.x
                "net.minecraft.network.packet.c2s.common.SyncedClientOptions"  // Yarn/fallback
            };
            for (String name : clientInfoNames) {
                try {
                    clientInfoClass = Class.forName(name);
                    defaultOptions = clientInfoClass.getMethod("createDefault").invoke(null);
                    break;
                } catch (ClassNotFoundException ignored) {}
            }

            if (clientInfoClass != null && defaultOptions != null) {
                Constructor<?> ctor = serverPlayerClass.getConstructor(
                        minecraftServerClass, serverWorldClass, GameProfile.class, clientInfoClass);
                return ctor.newInstance(server, world, profile, defaultOptions);
            }

            // Fallback: 3-parameter constructor
            Constructor<?> ctor = serverPlayerClass.getConstructor(
                    minecraftServerClass, serverWorldClass, GameProfile.class);
            return ctor.newInstance(server, world, profile);

        } catch (Exception e) {
            throw new RuntimeException("Failed to create ServerPlayer for MC 26.x", e);
        }
    }

    @Override
    public void registerChatListener(BiConsumer<String, String> handler) {
        try {
            // ServerMessageEvents is from Fabric API — same API surface for 26.x
            Class<?> messageEvents = Class.forName("net.fabricmc.fabric.api.message.v1.ServerMessageEvents");
            Object chatMessageEvent = messageEvents.getField("CHAT_MESSAGE").get(null);

            // Find the register method
            Method registerMethod = null;
            for (Method m : chatMessageEvent.getClass().getMethods()) {
                if (m.getName().equals("register") && m.getParameterCount() == 1) {
                    registerMethod = m;
                    break;
                }
            }

            if (registerMethod == null) {
                LOGGER.warn("[BlockMind] Could not find CHAT_MESSAGE.register method");
                return;
            }

            // Create dynamic proxy for the callback interface
            Class<?> functionalInterface = registerMethod.getParameterTypes()[0];
            Object proxy = java.lang.reflect.Proxy.newProxyInstance(
                    functionalInterface.getClassLoader(),
                    new Class<?>[]{functionalInterface},
                    (proxyObj, method, args) -> {
                        try {
                            extractChatMessage(args, handler);
                        } catch (Exception e) {
                            LOGGER.debug("[BlockMind] Chat event parse error: {}", e.getMessage());
                        }
                        return null;
                    }
            );

            registerMethod.invoke(chatMessageEvent, proxy);
            LOGGER.info("[BlockMind] Chat event listener registered (V26Compat, Mojang mappings)");
        } catch (Exception e) {
            LOGGER.error("[BlockMind] Failed to register chat listener in V26Compat: {}", e.getMessage());
        }
    }

    /**
     * Extract chat message from callback args.
     * MC 26.x callback: (PlayerChatMessage, ServerPlayer, ChatType.Bound)
     *   - PlayerChatMessage: use getContent() or getSignedContent() → Component
     *   - ServerPlayer: use getName() → Component
     */
    private void extractChatMessage(Object[] args, BiConsumer<String, String> handler) {
        if (args == null || args.length < 2) return;

        String playerName = "unknown";
        String messageText = "";

        // args[1] = ServerPlayer
        if (args[1] != null) {
            try {
                Object nameComponent = args[1].getClass().getMethod("getName").invoke(args[1]);
                playerName = (String) nameComponent.getClass().getMethod("getString").invoke(nameComponent);
            } catch (Exception ignored) {}
        }

        // args[0] = PlayerChatMessage (Mojang name)
        if (args[0] != null) {
            try {
                // Try getContent() → Component.getString()
                Object content = args[0].getClass().getMethod("getContent").invoke(args[0]);
                messageText = (String) content.getClass().getMethod("getString").invoke(content);
            } catch (Exception e1) {
                try {
                    // Try getSignedContent()
                    Object content = args[0].getClass().getMethod("getSignedContent").invoke(args[0]);
                    if (componentClass != null && componentClass.isInstance(content)) {
                        messageText = (String) content.getClass().getMethod("getString").invoke(content);
                    } else {
                        messageText = content.toString();
                    }
                } catch (Exception e2) {
                    try {
                        messageText = args[0].toString();
                    } catch (Exception ignored) {}
                }
            }
        }

        handler.accept(playerName, messageText);
    }

    @Override
    public String getPlayerName(Object player) {
        try {
            Object nameComponent = player.getClass().getMethod("getName").invoke(player);
            return (String) nameComponent.getClass().getMethod("getString").invoke(nameComponent);
        } catch (Exception e) {
            return player.toString();
        }
    }

    @Override
    public String getMessageText(Object message) {
        try {
            Object content = message.getClass().getMethod("getContent").invoke(message);
            return (String) content.getClass().getMethod("getString").invoke(content);
        } catch (Exception e) {
            return message.toString();
        }
    }

    @Override
    public String getVersionString() {
        try {
            Class<?> sharedConstants = Class.forName("net.minecraft.SharedConstants");
            Object gameVersion = sharedConstants.getMethod("getGameVersion").invoke(null);
            return (String) gameVersion.getClass().getMethod("getName").invoke(gameVersion);
        } catch (Exception e) {
            return "26.x";
        }
    }

    // ── Player property access (via reflection) ──

    private Object invokeMethod(Object obj, String methodName) {
        try {
            return obj.getClass().getMethod(methodName).invoke(obj);
        } catch (Exception e) {
            throw new RuntimeException("Failed to invoke " + methodName + " on " + obj.getClass().getName(), e);
        }
    }

    @Override
    public float getHealth(Object player) {
        return (float) invokeMethod(player, "getHealth");
    }

    @Override
    public double getX(Object player) {
        // Mojang: getX() or position().x
        try {
            return (double) invokeMethod(player, "getX");
        } catch (Exception e) {
            try {
                Object pos = invokeMethod(player, "position");
                return (double) pos.getClass().getMethod("x").invoke(pos);
            } catch (Exception e2) {
                throw new RuntimeException("Cannot get X", e2);
            }
        }
    }

    @Override
    public double getY(Object player) {
        try {
            return (double) invokeMethod(player, "getY");
        } catch (Exception e) {
            try {
                Object pos = invokeMethod(player, "position");
                return (double) pos.getClass().getMethod("y").invoke(pos);
            } catch (Exception e2) {
                throw new RuntimeException("Cannot get Y", e2);
            }
        }
    }

    @Override
    public double getZ(Object player) {
        try {
            return (double) invokeMethod(player, "getZ");
        } catch (Exception e) {
            try {
                Object pos = invokeMethod(player, "position");
                return (double) pos.getClass().getMethod("z").invoke(pos);
            } catch (Exception e2) {
                throw new RuntimeException("Cannot get Z", e2);
            }
        }
    }

    @Override
    public float getYaw(Object player) {
        return (float) invokeMethod(player, "getYaw");
    }

    @Override
    public float getPitch(Object player) {
        return (float) invokeMethod(player, "getPitch");
    }

    @Override
    public boolean isAlive(Object player) {
        return (boolean) invokeMethod(player, "isAlive");
    }

    @Override
    public void discard(Object player) {
        invokeMethod(player, "discard");
    }

    @Override
    public void setPos(Object player, double x, double y, double z) {
        try {
            player.getClass().getMethod("setPos", double.class, double.class, double.class)
                    .invoke(player, x, y, z);
        } catch (Exception e) {
            throw new RuntimeException("Cannot setPos", e);
        }
    }

    @Override
    public void refreshPositionAndAngles(Object player, double x, double y, double z, float yaw, float pitch) {
        try {
            // Mojang: absMoveTo or refreshPositionAndAngles
            player.getClass().getMethod("absMoveTo",
                    double.class, double.class, double.class, float.class, float.class)
                    .invoke(player, x, y, z, yaw, pitch);
        } catch (Exception e) {
            try {
                // Fallback: try Yarn name
                player.getClass().getMethod("refreshPositionAndAngles",
                        double.class, double.class, double.class, float.class, float.class)
                        .invoke(player, x, y, z, yaw, pitch);
            } catch (Exception e2) {
                throw new RuntimeException("Cannot refreshPositionAndAngles", e2);
            }
        }
    }

    @Override
    public void setRotation(Object player, float yaw, float pitch) {
        try {
            player.getClass().getMethod("setYRot", float.class).invoke(player, yaw);
            player.getClass().getMethod("setXRot", float.class).invoke(player, pitch);
        } catch (Exception e) {
            try {
                // Fallback: Yarn names
                player.getClass().getMethod("setYaw", float.class).invoke(player, yaw);
                player.getClass().getMethod("setPitch", float.class).invoke(player, pitch);
            } catch (Exception e2) {
                throw new RuntimeException("Cannot setRotation", e2);
            }
        }
    }

    @Override
    public int getFoodLevel(Object player) {
        try {
            // Mojang: getFoodData() or foodData()
            Object foodData = invokeMethodOrField(player, "getFoodData", "foodData");
            return (int) foodData.getClass().getMethod("getFoodLevel").invoke(foodData);
        } catch (Exception e) {
            try {
                // Yarn fallback: getHungerManager()
                Object hunger = invokeMethod(player, "getHungerManager");
                return (int) hunger.getClass().getMethod("getFoodLevel").invoke(hunger);
            } catch (Exception e2) {
                throw new RuntimeException("Cannot getFoodLevel", e2);
            }
        }
    }

    @Override
    public float getSaturationLevel(Object player) {
        try {
            Object foodData = invokeMethodOrField(player, "getFoodData", "foodData");
            return (float) foodData.getClass().getMethod("getSaturationLevel").invoke(foodData);
        } catch (Exception e) {
            try {
                Object hunger = invokeMethod(player, "getHungerManager");
                return (float) hunger.getClass().getMethod("getSaturationLevel").invoke(hunger);
            } catch (Exception e2) {
                throw new RuntimeException("Cannot getSaturationLevel", e2);
            }
        }
    }

    @Override
    public int getTotalExperience(Object player) {
        try {
            // Mojang: experienceLevel field or getTotalExperience()
            return (int) invokeMethod(player, "getTotalExperience");
        } catch (Exception e) {
            try {
                return (int) player.getClass().getField("totalExperience").get(player);
            } catch (Exception e2) {
                throw new RuntimeException("Cannot getTotalExperience", e2);
            }
        }
    }

    @Override
    public int getExperienceLevel(Object player) {
        try {
            return (int) player.getClass().getField("experienceLevel").get(player);
        } catch (Exception e) {
            try {
                return (int) invokeMethod(player, "getExperienceLevel");
            } catch (Exception e2) {
                throw new RuntimeException("Cannot getExperienceLevel", e2);
            }
        }
    }

    @Override
    public UUID getUuid(Object player) {
        return (UUID) invokeMethod(player, "getUUID");
    }

    @Override
    public String getDimension(Object player) {
        try {
            // Mojang: level().dimension().location().toString()
            Object level = invokeMethodOrField(player, "level", "serverLevel");
            Object dimension = invokeMethod(level, "dimension");
            Object location = invokeMethod(dimension, "location");
            return location.toString();
        } catch (Exception e) {
            try {
                // Yarn fallback
                Object world = invokeMethod(player, "getWorld");
                Object regKey = invokeMethod(world, "getRegistryKey");
                Object value = invokeMethod(regKey, "getValue");
                return value.toString();
            } catch (Exception e2) {
                return "unknown";
            }
        }
    }

    @Override
    public int[] getBlockPos(Object player) {
        try {
            Object pos = invokeMethod(player, "blockPosition");
            int x = (int) pos.getClass().getMethod("getX").invoke(pos);
            int y = (int) pos.getClass().getMethod("getY").invoke(pos);
            int z = (int) pos.getClass().getMethod("getZ").invoke(pos);
            return new int[]{x, y, z};
        } catch (Exception e) {
            throw new RuntimeException("Cannot getBlockPos", e);
        }
    }

    @Override
    public long getWorldTimeOfDay(Object player) {
        try {
            Object level = invokeMethodOrField(player, "level", "serverLevel");
            return (long) invokeMethod(level, "dayTime");
        } catch (Exception e) {
            try {
                Object world = invokeMethod(player, "getWorld");
                return (long) invokeMethod(world, "getTimeOfDay");
            } catch (Exception e2) {
                return 0;
            }
        }
    }

    @Override
    public boolean isBotPlayer(Object player) {
        return false;
    }

    // ── Reflection helpers ──

    /**
     * Try invoking a method, or reading a field if the method doesn't exist.
     */
    private Object invokeMethodOrField(Object obj, String methodName, String fieldName) {
        try {
            return invokeMethod(obj, methodName);
        } catch (Exception e) {
            try {
                return obj.getClass().getField(fieldName).get(obj);
            } catch (Exception e2) {
                throw new RuntimeException("Cannot access " + methodName + "/" + fieldName, e2);
            }
        }
    }
}
