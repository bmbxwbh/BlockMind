package blockmind.compat;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 版本兼容层 — 处理不同 MC 版本间的 API 差异
 *
 * 支持版本：
 * - 1.20.x: Yarn mappings (V120Compat)
 * - 1.21.x: Yarn mappings (V121Compat)
 * - 26.x:   Mojang mappings (V26Compat)
 *
 * 所有版本特定代码通过 MinecraftCompat 接口隔离，
 * 编译时只包含目标版本的实现（由 build.gradle source set 控制）。
 */
public class VersionCompat {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.compat");

    /** 检测到的 MC 主版本号 */
    private static int mcMajor = -1;
    private static int mcMinor = -1;
    private static int mcPatch = -1;

    /** 缓存的 MinecraftCompat 实例 */
    private static MinecraftCompat compatInstance;

    static {
        detectVersion();
    }

    /**
     * 运行时检测 MC 版本
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
    }

    private static void detectVersionFallback() {
        // 方法2: 从 Fabric Loader 获取
        try {
            Class<?> fabricLoader = Class.forName("net.fabricmc.loader.api.FabricLoader");
            Object loader = fabricLoader.getMethod("getInstance").invoke(null);
            Object mcMod = loader.getClass().getMethod("getModContainer", String.class).invoke(loader, "minecraft");
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

    /** 获取 MC 主版本号 (e.g., 1 or 26) */
    public static int getMcMajor() { return mcMajor; }

    /** 获取 MC 次版本号 (e.g., 20) */
    public static int getMcMinor() { return mcMinor; }

    /** 获取 MC 补丁版本号 (e.g., 4) */
    public static int getMcPatch() { return mcPatch; }

    /** 获取完整版本字符串 */
    public static String getVersionString() {
        return mcMajor + "." + mcMinor + "." + mcPatch;
    }

    /** 判断版本是否 >= 指定版本 */
    public static boolean isAtLeast(int major, int minor, int patch) {
        if (mcMajor != major) return mcMajor > major;
        if (mcMinor != minor) return mcMinor > minor;
        return mcPatch >= patch;
    }

    /**
     * 获取版本特定的 MinecraftCompat 实例。
     *
     * 根据检测到的 MC 版本加载对应的实现类：
     * - MC 26.x   → V26Compat  (Mojang mappings)
     * - MC 1.21.x → V121Compat (Yarn mappings)
     * - MC 1.20.x → V120Compat (Yarn mappings)
     *
     * 实现类由 build.gradle source set 机制确保只编译对应版本的代码。
     * 如果版本特定实现不可用（如 main 源码直接编译），回退到反射模式。
     */
    public static MinecraftCompat getCompat() {
        if (compatInstance != null) return compatInstance;
        compatInstance = createCompat();
        return compatInstance;
    }

    private static MinecraftCompat createCompat() {
        // 按版本优先级尝试加载实现
        String[] candidates;
        if (mcMajor >= 26) {
            candidates = new String[]{"blockmind.compat.V26Compat"};
        } else if (mcMinor >= 21) {
            candidates = new String[]{"blockmind.compat.V121Compat"};
        } else {
            candidates = new String[]{"blockmind.compat.V120Compat"};
        }

        for (String className : candidates) {
            try {
                Class<?> clazz = Class.forName(className);
                MinecraftCompat instance = (MinecraftCompat) clazz.getDeclaredConstructor().newInstance();
                LOGGER.info("[BlockMind] Loaded compat implementation: {}", className);
                return instance;
            } catch (ClassNotFoundException e) {
                LOGGER.debug("[BlockMind] Compat class not found: {} (expected for cross-version build)", className);
            } catch (Exception e) {
                LOGGER.warn("[BlockMind] Failed to instantiate {}: {}", className, e.getMessage());
            }
        }

        // 如果所有候选都失败，抛出异常
        throw new RuntimeException(
            "[BlockMind] No compatible MinecraftCompat implementation found for MC " + getVersionString()
            + ". Ensure the correct version-specific source set is compiled.");
    }
}
