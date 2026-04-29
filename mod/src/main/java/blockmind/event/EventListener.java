package blockmind.event;

import com.google.gson.JsonObject;
import net.fabricmc.fabric.api.message.v1.ServerMessageEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.server.network.ServerPlayerEntity;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/**
 * 游戏事件监听器
 * 监听 MC 游戏事件并推送到 WebSocket
 */
public class EventListener {

    private static final List<Consumer<JsonObject>> listeners = new ArrayList<>();

    /**
     * 注册事件监听
     */
    public void register() {
        // 聊天消息监听
        ServerMessageEvents.CHAT_MESSAGE.register((message, sender, params) -> {
            JsonObject event = new JsonObject();
            event.addProperty("type", "chat");
            JsonObject data = new JsonObject();
            data.addProperty("player", sender.getName().getString());
            data.addProperty("message", message.getContent().getString());
            event.add("data", data);
            broadcastEvent(event);
        });

        // 每 tick 检查（用于检测伤害、状态变化等）
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            // 检查玩家状态变化
            for (ServerPlayerEntity player : server.getPlayerManager().getPlayerList()) {
                checkPlayerStatus(player);
            }
        });
    }

    private static float lastHealth = 20.0f;
    private static int lastHunger = 20;

    /**
     * 检查玩家状态变化
     */
    private void checkPlayerStatus(ServerPlayerEntity player) {
        float currentHealth = player.getHealth();
        int currentHunger = player.getHungerManager().getFoodLevel();

        // 检测伤害
        if (currentHealth < lastHealth) {
            JsonObject event = new JsonObject();
            event.addProperty("type", "damage");
            JsonObject data = new JsonObject();
            data.addProperty("amount", lastHealth - currentHealth);
            data.addProperty("health", currentHealth);
            event.add("data", data);
            broadcastEvent(event);
        }

        // 检测死亡
        if (currentHealth <= 0) {
            JsonObject event = new JsonObject();
            event.addProperty("type", "death");
            JsonObject data = new JsonObject();
            data.addProperty("reason", "unknown");
            event.add("data", data);
            broadcastEvent(event);
        }

        lastHealth = currentHealth;
        lastHunger = currentHunger;
    }

    /**
     * 广播事件到所有监听器
     */
    public static void broadcastEvent(JsonObject event) {
        for (Consumer<JsonObject> listener : listeners) {
            try {
                listener.accept(event);
            } catch (Exception e) {
                // 忽略监听器异常
            }
        }
    }

    /**
     * 添加事件监听器
     */
    public static void addListener(Consumer<JsonObject> listener) {
        listeners.add(listener);
    }

    /**
     * 移除事件监听器
     */
    public static void removeListener(Consumer<JsonObject> listener) {
        listeners.remove(listener);
    }
}
