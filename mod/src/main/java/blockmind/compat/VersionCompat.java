package blockmind.compat;

import com.mojang.authlib.GameProfile;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Constructor;

/**
 * 版本兼容层 — 处理不同 MC 版本间的 API 差异
 *
 * 支持版本：
 * - 1.20.0 ~ 1.20.1: ServerPlayerEntity 3 参数构造函数（无 SyncedClientOptions）
 * - 1.20.2 ~ 1.20.4: ServerPlayerEntity 4 参数构造函数（含 SyncedClientOptions）
 * - 1.20.5 ~ 1.21.x: 同 1.20.2+ 但内部实现可能有变化
 *
 * 使用反射避免编译期硬依赖，运行时自动检测可用 API。
 */
public class VersionCompat {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.compat");

    /** 检测到的 MC 主版本号 */
    private static int mcMajor = -1;
    private static int mcMinor = -1;
    private static int mcPatch = -1;

    /** SyncedClientOptions 类是否可用 */
    private static boolean hasSyncedClientOptions = false;
    private static Class<?> syncedClientOptionsClass = null;

    static {
        detectVersion();
    }

    /**
     * 运行时检测 MC 版本和可用 API
     */
    private static void detectVersion() {
        // 方法1: 从 SharedConstants 获取版本
        try {
            Class<?> sharedConstants = Class.forName("net.minecraft.SharedConstants");
            Object gameVersion = sharedConstants.getMethod("getGameVersion").invoke(null);
            String versionString = (String) gameVersion.getClass().getMethod("getName").invoke(gameVersion);
            parseVersion(versionString);
            LOGGER.info("[BlockMind] Detected MC version: {}.{}.{}", mcMajor, mcMinor, mcPatch);
        } catch (Exception e) {
            LOGGER.warn("[BlockMind] Could not detect MC version from SharedConstants, trying fallback...");
            detectVersionFallback();
        }

        // 检测 SyncedClientOptions 是否存在
        try {
            syncedClientOptionsClass = Class.forName("net.minecraft.network.packet.c2s.common.SyncedClientOptions");
            hasSyncedClientOptions = true;
            LOGGER.info("[BlockMind] SyncedClientOptions available (MC >= 1.20.2)");
        } catch (ClassNotFoundException e) {
            hasSyncedClientOptions = false;
            LOGGER.info("[BlockMind] SyncedClientOptions not available (MC 1.20.0-1.20.1)");
        }
    }

    private static void detectVersionFallback() {
        // 方法2: 从 Fabric Loader 获取
        try {
            Class<?> fabricLoader = Class.forName("net.fabricmc.loader.api.FabricLoader");
            Object loader = fabricLoader.getMethod("getInstance").invoke(null);
            Object mcMod = loader.getMethod("getModContainer", String.class).invoke(loader, "minecraft");
            if (mcMod != null) {
                Object metadata = mcMod.getClass().getMethod("getMetadata").invoke(mcMod);
                Object version = metadata.getClass().getMethod("getVersion").invoke(metadata);
                String versionString = version.toString();
                parseVersion(versionString);
                LOGGER.info("[BlockMind] Detected MC version (fallback): {}.{}.{}", mcMajor, mcMinor, mcPatch);
                return;
            }
        } catch (Exception ignored) {}

        // 方法3: 尝试从系统属性获取
        String mcVersion = System.getProperty("minecraft.version", "");
        if (!mcVersion.isEmpty()) {
            parseVersion(mcVersion);
            LOGGER.info("[BlockMind] Detected MC version (system prop): {}.{}.{}", mcMajor, mcMinor, mcPatch);
            return;
        }

        // 默认假设 1.20.4
        LOGGER.warn("[BlockMind] Could not detect MC version, assuming 1.20.4");
        mcMajor = 1; mcMinor = 20; mcPatch = 4;
    }

    private static void parseVersion(String version) {
        try {
            String[] parts = version.split("\\.");
            mcMajor = Integer.parseInt(parts[0]);
            mcMinor = Integer.parseInt(parts[1]);
            mcPatch = parts.length > 2 ? Integer.parseInt(parts[2].split("-")[0]) : 0;
        } catch (Exception e) {
            LOGGER.warn("[BlockMind] Failed to parse version '{}', assuming 1.20.4", version);
            mcMajor = 1; mcMinor = 20; mcPatch = 4;
        }
    }

    // ── 公共 API ──

    /**
     * 获取 MC 主版本号 (e.g., 1)
     */
    public static int getMcMajor() { return mcMajor; }

    /**
     * 获取 MC 次版本号 (e.g., 20)
     */
    public static int getMcMinor() { return mcMinor; }

    /**
     * 获取 MC 补丁版本号 (e.g., 4)
     */
    public static int getMcPatch() { return mcPatch; }

    /**
     * 获取完整版本字符串
     */
    public static String getVersionString() {
        return mcMajor + "." + mcMinor + "." + mcPatch;
    }

    /**
     * 是否支持 SyncedClientOptions (MC >= 1.20.2)
     */
    public static boolean hasSyncedClientOptions() {
        return hasSyncedClientOptions;
    }

    /**
     * 判断版本是否 >= 指定版本
     */
    public static boolean isAtLeast(int major, int minor, int patch) {
        if (mcMajor != major) return mcMajor > major;
        if (mcMinor != minor) return mcMinor > minor;
        return mcPatch >= patch;
    }

    /**
     * 创建 ServerPlayerEntity — 自动适配不同版本的构造函数
     *
     * - MC 1.20.0-1.20.1: 3 参数 (server, world, profile)
     * - MC 1.20.2+:        4 参数 (server, world, profile, clientOptions)
     *
     * @return 新创建的 ServerPlayerEntity 实例
     */
    public static ServerPlayerEntity createPlayer(MinecraftServer server, ServerWorld world, GameProfile profile) {
        if (hasSyncedClientOptions) {
            return createPlayerWithSyncedOptions(server, world, profile);
        } else {
            return createPlayerLegacy(server, world, profile);
        }
    }

    private static ServerPlayerEntity createPlayerWithSyncedOptions(MinecraftServer server, ServerWorld world, GameProfile profile) {
        try {
            // SyncedClientOptions.createDefault()
            Object defaultOptions = syncedClientOptionsClass.getMethod("createDefault").invoke(null);

            // 查找 4 参数构造函数
            Constructor<?> ctor = ServerPlayerEntity.class.getConstructor(
                    MinecraftServer.class, ServerWorld.class, GameProfile.class, syncedClientOptionsClass);
            return (ServerPlayerEntity) ctor.newInstance(server, world, profile, defaultOptions);
        } catch (Exception e) {
            LOGGER.error("[BlockMind] Failed to create player with SyncedClientOptions, falling back to legacy", e);
            return createPlayerLegacy(server, world, profile);
        }
    }

    private static ServerPlayerEntity createPlayerLegacy(MinecraftServer server, ServerWorld world, GameProfile profile) {
        try {
            // 3 参数构造函数 (MC 1.20.0-1.20.1)
            Constructor<?> ctor = ServerPlayerEntity.class.getConstructor(
                    MinecraftServer.class, ServerWorld.class, GameProfile.class);
            return (ServerPlayerEntity) ctor.newInstance(server, world, profile);
        } catch (Exception e) {
            // 如果 3 参数也不存在，尝试 4 参数作为最终回退
            LOGGER.error("[BlockMind] Failed to create player with legacy constructor", e);
            throw new RuntimeException("Cannot create ServerPlayerEntity for MC " + getVersionString(), e);
        }
    }

    /**
     * 注册聊天事件监听 — 适配不同版本的 callback 签名
     *
     * 在 MC 1.21+ 中，ServerMessageEvents.CHAT_MESSAGE 的 callback 参数有变化。
     * 此方法通过反射注册，避免编译期硬依赖。
     *
     * @param handler 聊天消息处理器，参数为 (playerName, messageText)
     */
    public static void registerChatListener(java.util.function.BiConsumer<String, String> handler) {
        try {
            Class<?> messageEvents = Class.forName("net.fabricmc.fabric.api.message.v1.ServerMessageEvents");
            Object chatMessage = messageEvents.getField("CHAT_MESSAGE").get(null);

            // 获取 register 方法
            Class<?> listenerType = chatMessage.getClass();
            // 使用 Fabric Event API 的 register 方法
            java.lang.reflect.Method registerMethod = null;
            for (java.lang.reflect.Method m : chatMessage.getClass().getMethods()) {
                if (m.getName().equals("register") && m.getParameterCount() == 1) {
                    registerMethod = m;
                    break;
                }
            }

            if (registerMethod == null) {
                LOGGER.warn("[BlockMind] Could not find CHAT_MESSAGE.register method, chat events disabled");
                return;
            }

            // 创建动态代理处理不同的 callback 签名
            Class<?> functionalInterface = registerMethod.getParameterTypes()[0];
            Object proxy = java.lang.reflect.Proxy.newProxyInstance(
                    functionalInterface.getClassLoader(),
                    new Class<?>[]{functionalInterface},
                    (proxyObj, method, args) -> {
                        try {
                            // 尝试从 callback 参数中提取消息
                            extractChatMessage(args, handler);
                        } catch (Exception e) {
                            LOGGER.debug("[BlockMind] Chat event parse error: {}", e.getMessage());
                        }
                        return null;
                    }
            );

            registerMethod.invoke(chatMessage, proxy);
            LOGGER.info("[BlockMind] Chat event listener registered (compat mode)");
        } catch (Exception e) {
            LOGGER.warn("[BlockMind] Failed to register chat listener via reflection: {}", e.getMessage());
            // 回退: 直接尝试编译时 API
            registerChatListenerDirect(handler);
        }
    }

    /**
     * 直接注册聊天监听 (编译时回退)
     */
    private static void registerChatListenerDirect(java.util.function.BiConsumer<String, String> handler) {
        try {
            net.fabricmc.fabric.api.message.v1.ServerMessageEvents.CHAT_MESSAGE.register(
                (message, sender, params) -> {
                    String playerName = sender.getName().getString();
                    String text = message.getContent().getString();
                    handler.accept(playerName, text);
                }
            );
            LOGGER.info("[BlockMind] Chat event listener registered (direct mode)");
        } catch (Exception e) {
            LOGGER.error("[BlockMind] Failed to register chat listener: {}", e.getMessage());
        }
    }

    /**
     * 从 CHAT_MESSAGE callback 参数中提取玩家名和消息文本
     * 兼容不同版本的参数结构
     */
    private static void extractChatMessage(Object[] args, java.util.function.BiConsumer<String, String> handler) {
        if (args == null || args.length < 2) return;

        // args[0] = SignedMessage, args[1] = ServerPlayerEntity, args[2] = MessageType.Parameters
        String playerName = "unknown";
        String messageText = "";

        // 提取玩家名
        if (args[1] != null) {
            try {
                Object nameObj = args[1].getClass().getMethod("getName").invoke(args[1]);
                playerName = nameObj.getClass().getMethod("getString").invoke(nameObj).toString();
            } catch (Exception ignored) {}
        }

        // 提取消息文本
        if (args[0] != null) {
            try {
                // 尝试 getContent().getString() (1.20.x)
                Object content = args[0].getClass().getMethod("getContent").invoke(args[0]);
                messageText = content.getClass().getMethod("getString").invoke(content).toString();
            } catch (Exception e1) {
                try {
                    // 1.21+ 可能使用 getSignedContent() 或其他方法
                    Object content = args[0].getClass().getMethod("getSignedContent").invoke(args[0]);
                    messageText = content.toString();
                } catch (Exception e2) {
                    try {
                        // 最终回退: toString()
                        messageText = args[0].toString();
                    } catch (Exception ignored) {}
                }
            }
        }

        handler.accept(playerName, messageText);
    }
}
