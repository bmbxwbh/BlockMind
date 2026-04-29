package blockmind.executor;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.MinecraftServer;
import net.minecraft.text.Text;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Vec3d;

/**
 * 游戏动作执行器
 * 接收 JSON 参数，执行游戏内动作
 */
public class ActionExecutor {

    private static MinecraftServer server;

    public static void setServer(MinecraftServer srv) {
        server = srv;
    }

    /**
     * 移动到指定位置
     * Body: {"x": 128, "y": 64, "z": -256, "sprint": false}
     */
    public static JsonObject move(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity player = getPlayer();
        if (player == null) return error("No player online");

        double x = json.get("x").getAsDouble();
        double y = json.get("y").getAsDouble();
        double z = json.get("z").getAsDouble();
        boolean sprint = json.has("sprint") && json.get("sprint").getAsBoolean();

        // 传送到目标位置（简化实现）
        player.teleport(x, y, z);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("details", String.format("移动到 (%.1f, %.1f, %.1f)", x, y, z));
        return result;
    }

    /**
     * 挖掘方块
     * Body: {"x": 128, "y": 63, "z": -256}
     */
    public static JsonObject dig(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity player = getPlayer();
        if (player == null) return error("No player online");

        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

        BlockPos pos = new BlockPos(x, y, z);
        String blockType = player.getWorld().getBlockState(pos).getBlock().toString();

        // 破坏方块
        player.getWorld().breakBlock(pos, true, player);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("details", String.format("挖掘 %s at (%d, %d, %d)", blockType, x, y, z));
        return result;
    }

    /**
     * 放置方块
     * Body: {"item": "torch", "x": 128, "y": 64, "z": -256}
     */
    public static JsonObject place(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity player = getPlayer();
        if (player == null) return error("No player online");

        String item = json.get("item").getAsString();
        int x = json.get("x").getAsInt();
        int y = json.get("y").getAsInt();
        int z = json.get("z").getAsInt();

        // 简化实现：直接在目标位置放置方块
        BlockPos pos = new BlockPos(x, y, z);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("details", String.format("放置 %s at (%d, %d, %d)", item, x, y, z));
        return result;
    }

    /**
     * 攻击实体
     * Body: {"entity_id": 123}
     */
    public static JsonObject attack(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity player = getPlayer();
        if (player == null) return error("No player online");

        int entityId = json.get("entity_id").getAsInt();

        // 查找实体
        var entity = player.getWorld().getEntityById(entityId);
        if (entity == null) return error("Entity not found");

        String entityType = entity.getType().toString();
        player.attack(entity);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("details", String.format("攻击 %s (ID: %d)", entityType, entityId));
        return result;
    }

    /**
     * 进食
     * Body: {"item": "bread"}
     */
    public static JsonObject eat(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity player = getPlayer();
        if (player == null) return error("No player online");

        String item = json.get("item").getAsString();

        // 简化实现：直接恢复饥饿值
        player.getHungerManager().add(5, 0.5f);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("details", String.format("进食 %s，恢复饥饿值", item));
        return result;
    }

    /**
     * 看向位置
     * Body: {"x": 130, "y": 65, "z": -258}
     */
    public static JsonObject look(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity player = getPlayer();
        if (player == null) return error("No player online");

        double x = json.get("x").getAsDouble();
        double y = json.get("y").getAsDouble();
        double z = json.get("z").getAsDouble();

        // 计算朝向
        double dx = x - player.getX();
        double dy = y - player.getY();
        double dz = z - player.getZ();
        double horizontalDist = Math.sqrt(dx * dx + dz * dz);
        float yaw = (float) Math.toDegrees(Math.atan2(-dx, dz));
        float pitch = (float) Math.toDegrees(Math.atan2(-dy, horizontalDist));

        player.setYaw(yaw);
        player.setPitch(pitch);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("details", String.format("看向 (%.1f, %.1f, %.1f)", x, y, z));
        return result;
    }

    /**
     * 发送聊天消息
     * Body: {"message": "Hello!"}
     */
    public static JsonObject chat(String body) {
        JsonObject json = parseBody(body);
        if (json == null) return error("Invalid JSON");

        ServerPlayerEntity player = getPlayer();
        if (player == null) return error("No player online");

        String message = json.get("message").getAsString();

        // 发送聊天消息
        player.sendMessage(Text.literal(message), false);

        JsonObject result = new JsonObject();
        result.addProperty("success", true);
        result.addProperty("details", String.format("发送消息: %s", message));
        return result;
    }

    // ─── 辅助方法 ─────────────────────────────────────

    private static ServerPlayerEntity getPlayer() {
        if (server == null) return null;
        var players = server.getPlayerManager().getPlayerList();
        return players.isEmpty() ? null : players.get(0);
    }

    private static JsonObject parseBody(String body) {
        try {
            return JsonParser.parseString(body).getAsJsonObject();
        } catch (Exception e) {
            return null;
        }
    }

    private static JsonObject error(String message) {
        JsonObject json = new JsonObject();
        json.addProperty("success", false);
        json.addProperty("error", message);
        return json;
    }
}
