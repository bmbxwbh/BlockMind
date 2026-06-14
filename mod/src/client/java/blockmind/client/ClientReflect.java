package blockmind.client;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Method;

/**
 * 客户端反射工具 — 所有 net.minecraft.client.* 调用通过此工具
 * 避免编译时依赖客户端 Minecraft JAR
 */
public final class ClientReflect {

    private static final Logger LOGGER = LoggerFactory.getLogger("blockmind.client.reflect");

    // 缓存的类和方法
    private static Class<?> minecraftClientClass;
    private static Method getInstanceMethod;
    private static Method get playerField;

    private ClientReflect() {}

    static {
        try {
            minecraftClientClass = Class.forName("net.minecraft.client.MinecraftClient");
            getInstanceMethod = minecraftClientClass.getMethod("getInstance");
        } catch (Exception e) {
            LOGGER.warn("[BlockMind-Client] MinecraftClient not available: {}", e.getMessage());
        }
    }

    /** 获取 MinecraftClient 实例 */
    public static Object getClient() {
        try {
            return getInstanceMethod.invoke(null);
        } catch (Exception e) {
            return null;
        }
    }

    /** 获取本地玩家 ClientPlayerEntity */
    public static Object getPlayer() {
        try {
            Object client = getClient();
            if (client == null) return null;
            var playerField = minecraftClientClass.getField("player");
            return playerField.get(client);
        } catch (Exception e) {
            return null;
        }
    }

    /** 调用方法（安全） */
    public static Object invoke(Object obj, String methodName, Class<?>[] paramTypes, Object... args) {
        try {
            Method m = obj.getClass().getMethod(methodName, paramTypes);
            return m.invoke(obj, args);
        } catch (Exception e) {
            LOGGER.debug("invoke {} failed: {}", methodName, e.getMessage());
            return null;
        }
    }

    /** 调用无参方法 */
    public static Object invoke(Object obj, String methodName) {
        try {
            Method m = obj.getClass().getMethod(methodName);
            return m.invoke(obj);
        } catch (Exception e) {
            LOGGER.debug("invoke {} failed: {}", methodName, e.getMessage());
            return null;
        }
    }

    /** 获取字段值 */
    public static Object getField(Object obj, String fieldName) {
        try {
            return obj.getClass().getField(fieldName).get(obj);
        } catch (Exception e) {
            return null;
        }
    }

    /** 设置字段值 */
    public static void setField(Object obj, String fieldName, Object value) {
        try {
            obj.getClass().getField(fieldName).set(obj, value);
        } catch (Exception e) {
            LOGGER.debug("setField {} failed: {}", fieldName, e.getMessage());
        }
    }

    /** 调用 double 返回值方法 */
    public static double invokeDouble(Object obj, String methodName) {
        Object result = invoke(obj, methodName);
        return result instanceof Number ? ((Number) result).doubleValue() : 0;
    }

    /** 调用 float 返回值方法 */
    public static float invokeFloat(Object obj, String methodName) {
        Object result = invoke(obj, methodName);
        return result instanceof Number ? ((Number) result).floatValue() : 0;
    }

    /** 调用 int 返回值方法 */
    public static int invokeInt(Object obj, String methodName) {
        Object result = invoke(obj, methodName);
        return result instanceof Number ? ((Number) result).intValue() : 0;
    }

    /** 调用 boolean 返回值方法 */
    public static boolean invokeBool(Object obj, String methodName) {
        Object result = invoke(obj, methodName);
        return Boolean.TRUE.equals(result);
    }
}
