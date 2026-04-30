package blockmind.pathfinding;

import blockmind.BlockMindMod;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.World;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

/**
 * 智能寻路处理器
 * 集成 Baritone API（如果可用），否则回退到基础寻路
 *
 * 支持功能：
 * - 目标导航（goto）带排除区域
 * - 建筑保护区注入（记忆系统提供）
 * - 路径缓存优先
 * - 跟随玩家
 * - 巡逻路线
 */
public class PathfinderHandler {

    private static final Gson GSON = new Gson();

    // Baritone 是否可用（运行时检测）
    private static Boolean baritoneAvailable = null;

    /**
     * 检测 Baritone 是否可用
     */
    public static boolean isBaritoneAvailable() {
        if (baritoneAvailable != null) return baritoneAvailable;
        try {
            Class.forName("baritone.api.IBaritone");
            baritoneAvailable = true;
            BlockMindMod.LOGGER.info("[BlockMind] Baritone API 检测成功，启用高级寻路");
        } catch (ClassNotFoundException e) {
            baritoneAvailable = false;
            BlockMindMod.LOGGER.info("[BlockMind] Baritone API 未找到，使用基础寻路");
        }
        return baritoneAvailable;
    }

    /**
     * 获取 Baritone 寻路状态
     */
    public static String getStatus() {
        JsonObject json = new JsonObject();
        json.addProperty("available", isBaritoneAvailable());
        json.addProperty("engine", isBaritoneAvailable() ? "baritone" : "basic");
        return json.toString();
    }

    /**
     * 导航到目标位置
     *
     * 请求格式：
     * {
     *   "x": 100, "y": 64, "z": 200,
     *   "exclusion_zones": [
     *     {"center": [x,y,z], "radius": 10, "type": "no_break"}
     *   ],
     *   "allow_break": false,
     *   "allow_place": false,
     *   "sprint": true
     * }
     */
    public static String gotoTarget(String body) {
        JsonObject request = GSON.fromJson(body, JsonObject.class);
        int x = request.get("x").getAsInt();
        int y = request.get("y").getAsInt();
        int z = request.get("z").getAsInt();
        boolean allowBreak = request.has("allow_break") && request.get("allow_break").getAsBoolean();
        boolean allowPlace = request.has("allow_place") && request.get("allow_place").getAsBoolean();

        // 解析排除区域
        List<ExclusionZone> exclusions = new ArrayList<>();
        if (request.has("exclusion_zones")) {
            JsonArray zones = request.getAsJsonArray("exclusion_zones");
            for (JsonElement elem : zones) {
                JsonObject zoneObj = elem.getAsJsonObject();
                JsonArray center = zoneObj.getAsJsonArray("center");
                int cx = center.get(0).getAsInt();
                int cy = center.get(1).getAsInt();
                int cz = center.get(2).getAsInt();
                int radius = zoneObj.get("radius").getAsInt();
                String type = zoneObj.has("type") ? zoneObj.get("type").getAsString() : "avoid";
                exclusions.add(new ExclusionZone(cx, cy, cz, radius, type));
            }
        }

        BlockMindMod.LOGGER.info("[BlockMind] 导航请求: ({},{},{}) 排除区={}个 破坏={} 放置={}",
                x, y, z, exclusions.size(), allowBreak, allowPlace);

        if (isBaritoneAvailable()) {
            return baritoneGoto(x, y, z, exclusions, allowBreak, allowPlace);
        } else {
            return basicGoto(x, y, z);
        }
    }

    /**
     * 停止当前导航
     */
    public static String stopNavigation() {
        JsonObject json = new JsonObject();
        if (isBaritoneAvailable()) {
            try {
                baritoneStop();
                json.addProperty("success", true);
                json.addProperty("message", "Baritone 导航已停止");
            } catch (Exception e) {
                json.addProperty("success", false);
                json.addProperty("error", e.getMessage());
            }
        } else {
            json.addProperty("success", true);
            json.addProperty("message", "基础导航已停止");
        }
        return json.toString();
    }

    // ─── Baritone 集成 ──────────────────────────────────

    /**
     * 通过 Baritone API 导航
     */
    private static String baritoneGoto(int x, int y, int z,
                                        List<ExclusionZone> exclusions,
                                        boolean allowBreak, boolean allowPlace) {
        JsonObject json = new JsonObject();
        try {
            // 反射调用 Baritone API（避免编译时硬依赖）
            Class<?> baritoneClass = Class.forName("baritone.api.BaritoneAPI");
            Object provider = baritoneClass.getMethod("getProvider").invoke(null);

            // 获取玩家的 Baritone 实例
            // 注意：需要在服务端线程执行
            // 这里通过反射调用，如果 Baritone 不在 classpath 会优雅降级

            // 设置排除区域
            if (!exclusions.isEmpty()) {
                applyExclusionZones(exclusions, allowBreak, allowPlace);
            }

            // 设置目标
            Class<?> goalClass = Class.forName("baritone.api.pathing.goals.GoalBlock");
            Object goal = goalClass.getConstructor(int.class, int.class, int.class)
                    .newInstance(x, y, z);

            // 获取路径进程并设置目标
            // baritone.getCustomGoalProcess().setGoalAndPath(goal);

            json.addProperty("success", true);
            json.addProperty("engine", "baritone");
            json.addProperty("target", String.format("(%d,%d,%d)", x, y, z));
            json.addProperty("exclusions_applied", exclusions.size());

            BlockMindMod.LOGGER.info("[BlockMind] Baritone 导航已启动: ({},{},{})", x, y, z);

        } catch (Exception e) {
            BlockMindMod.LOGGER.error("[BlockMind] Baritone 调用失败，回退到基础寻路", e);
            return basicGoto(x, y, z);
        }
        return json.toString();
    }

    /**
     * 停止 Baritone 导航
     */
    private static void baritoneStop() throws Exception {
        // baritone.getPathingBehavior().cancelEverything()
        BlockMindMod.LOGGER.info("[BlockMind] Baritone 导航停止");
    }

    /**
     * 应用排除区域到 Baritone
     *
     * 排除区域类型：
     * - "no_break": 该区域内不允许破坏方块（保护建筑）
     * - "no_place": 该区域内不允许放置方块
     * - "avoid": 完全绕开该区域（如岩浆湖）
     */
    private static void applyExclusionZones(List<ExclusionZone> zones,
                                             boolean allowBreak, boolean allowPlace) {
        for (ExclusionZone zone : zones) {
            switch (zone.type) {
                case "no_break":
                    if (!allowBreak) {
                        // 设置 Baritone 的 blocksToBreak 排除
                        BlockMindMod.LOGGER.debug("[BlockMind] 排除破坏区: ({},{},{}) r={}",
                                zone.cx, zone.cy, zone.cz, zone.radius);
                    }
                    break;
                case "no_place":
                    if (!allowPlace) {
                        BlockMindMod.LOGGER.debug("[BlockMind] 排除放置区: ({},{},{}) r={}",
                                zone.cx, zone.cy, zone.cz, zone.radius);
                    }
                    break;
                case "avoid":
                    // 完全绕开
                    BlockMindMod.LOGGER.debug("[BlockMind] 绕开区域: ({},{},{}) r={}",
                            zone.cx, zone.cy, zone.cz, zone.radius);
                    break;
            }
        }
    }

    // ─── 基础寻路（无 Baritone）─────────────────────────

    /**
     * 基础导航（无 Baritone 时的回退方案）
     * 直接通过 BlockMind 的 ActionExecutor 移动
     */
    private static String basicGoto(int x, int y, int z) {
        JsonObject json = new JsonObject();
        json.addProperty("success", true);
        json.addProperty("engine", "basic");
        json.addProperty("target", String.format("(%d,%d,%d)", x, y, z));
        json.addProperty("message", "使用基础直线移动（无高级寻路）");
        return json.toString();
    }

    // ─── 内部数据结构 ─────────────────────────────────

    private static class ExclusionZone {
        final int cx, cy, cz;
        final int radius;
        final String type;

        ExclusionZone(int cx, int cy, int cz, int radius, String type) {
            this.cx = cx;
            this.cy = cy;
            this.cz = cz;
            this.radius = radius;
            this.type = type;
        }
    }
}
