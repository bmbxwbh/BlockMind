package blockmind.api;

import blockmind.BlockMindMod;
import blockmind.bot.BotManager;
import blockmind.collector.StateCollector;
import blockmind.executor.ActionExecutor;
import blockmind.pathfinding.PathfinderHandler;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

/**
 * BlockMind HTTP API 服务
 * 提供 REST API 供 Python 后端调用
 *
 * 端点列表：
 * - 健康检查: /health
 * - Bot 管理: /api/bot/spawn, /api/bot/despawn, /api/bot/status
 * - 状态查询: /api/status, /api/world, /api/inventory, /api/entities, /api/blocks
 * - 动作执行: /api/move, /api/dig, /api/place, /api/attack, /api/eat, /api/look, /api/chat
 * - 智能导航: /api/navigate/goto, /api/navigate/stop, /api/navigate/status
 */
public class BlockMindHttpServer {

    private final int port;
    private final String apiToken;
    private com.sun.net.httpserver.HttpServer server;

    public BlockMindHttpServer(int port, String apiToken) {
        this.port = port;
        this.apiToken = apiToken;
    }

    public void start() throws IOException {
        staticApiToken = this.apiToken;
        server = com.sun.net.httpserver.HttpServer.create(new InetSocketAddress(port), 0);
        server.setExecutor(Executors.newFixedThreadPool(4));

        // ── 基础 API（无需认证）──
        server.createContext("/health", new HealthHandler());

        // ── 需要认证的 API ──
        server.createContext("/api/status", new StatusHandler());
        server.createContext("/api/world", new WorldHandler());
        server.createContext("/api/inventory", new InventoryHandler());
        server.createContext("/api/entities", new EntitiesHandler());
        server.createContext("/api/blocks", new BlocksHandler());

        // ── Bot 管理 ──
        server.createContext("/api/bot/spawn", new BotSpawnHandler());
        server.createContext("/api/bot/despawn", new BotDespawnHandler());
        server.createContext("/api/bot/status", new BotStatusHandler());

        // ── 动作执行 ──
        server.createContext("/api/move", new MoveHandler());
        server.createContext("/api/dig", new DigHandler());
        server.createContext("/api/place", new PlaceHandler());
        server.createContext("/api/attack", new AttackHandler());
        server.createContext("/api/eat", new EatHandler());
        server.createContext("/api/look", new LookHandler());
        server.createContext("/api/chat", new ChatHandler());

        // ── 智能导航（Baritone 集成）──
        server.createContext("/api/navigate/goto", new NavigateGotoHandler());
        server.createContext("/api/navigate/stop", new NavigateStopHandler());
        server.createContext("/api/navigate/status", new NavigateStatusHandler());

        server.start();
        BlockMindMod.LOGGER.info("[BlockMind] HTTP API listening on port {} ({} 导路引擎, 认证: {})",
                port, PathfinderHandler.isBaritoneAvailable() ? "Baritone" : "基础",
                (apiToken != null && !apiToken.isEmpty()) ? "已启用" : "未配置");
    }

    public void stop() {
        if (server != null) {
            server.stop(0);
        }
    }

    // ─── 辅助方法 ─────────────────────────────────────

    private static String staticApiToken;

    static boolean checkAuth(HttpExchange exchange) throws IOException {
        if (staticApiToken == null || staticApiToken.isEmpty()) return true;
        String auth = exchange.getRequestHeaders().getFirst("Authorization");
        if (auth != null && auth.equals("Bearer " + staticApiToken)) return true;
        sendResponse(exchange, 401, "{\"error\":\"Unauthorized\",\"message\":\"需要有效的 API Token\"}");
        return false;
    }

    static void sendResponse(HttpExchange exchange, int statusCode, String json) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        byte[] response = json.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(statusCode, response.length);
        OutputStream os = exchange.getResponseBody();
        os.write(response);
        os.close();
    }

    static String readBody(HttpExchange exchange) throws IOException {
        return new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
    }

    // ─── 状态查询 Handlers ────────────────────────────

    static class HealthHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            sendResponse(exchange, 200,
                    "{\"status\":\"ok\",\"mod\":\"blockmind\",\"pathfinder\":\""
                    + (PathfinderHandler.isBaritoneAvailable() ? "baritone" : "basic") + "\"}");
        }
    }

    static class StatusHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkAuth(exchange)) return;
            sendResponse(exchange, 200, StateCollector.getStatus().toString());
        }
    }

    static class WorldHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkAuth(exchange)) return;
            sendResponse(exchange, 200, StateCollector.getWorld().toString());
        }
    }

    static class InventoryHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkAuth(exchange)) return;
            sendResponse(exchange, 200, StateCollector.getInventory().toString());
        }
    }

    static class EntitiesHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            int radius = parseQueryParam(exchange, "radius", 32);
            sendResponse(exchange, 200, StateCollector.getEntities(radius).toString());
        }
    }

    static class BlocksHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            int radius = parseQueryParam(exchange, "radius", 16);
            String type = parseQueryStr(exchange, "type");
            sendResponse(exchange, 200, StateCollector.getBlocks(radius, type).toString());
        }
    }

    // ─── Bot 管理 Handlers ────────────────────────────

    static class BotSpawnHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            String body = readBody(exchange);
            String name = null;
            try {
                var json = com.google.gson.JsonParser.parseString(body).getAsJsonObject();
                if (json.has("name")) name = json.get("name").getAsString();
            } catch (Exception ignored) {}
            sendResponse(exchange, 200, BotManager.spawn(name).toString());
        }
    }

    static class BotDespawnHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            sendResponse(exchange, 200, BotManager.despawn().toString());
        }
    }

    static class BotStatusHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkAuth(exchange)) return;
            sendResponse(exchange, 200, BotManager.getStatus().toString());
        }
    }

    // ─── 动作执行 Handlers ────────────────────────────

    static class MoveHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            sendResponse(exchange, 200, ActionExecutor.move(readBody(exchange)).toString());
        }
    }

    static class DigHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            sendResponse(exchange, 200, ActionExecutor.dig(readBody(exchange)).toString());
        }
    }

    static class PlaceHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            sendResponse(exchange, 200, ActionExecutor.place(readBody(exchange)).toString());
        }
    }

    static class AttackHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            sendResponse(exchange, 200, ActionExecutor.attack(readBody(exchange)).toString());
        }
    }

    static class EatHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            sendResponse(exchange, 200, ActionExecutor.eat(readBody(exchange)).toString());
        }
    }

    static class LookHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            sendResponse(exchange, 200, ActionExecutor.look(readBody(exchange)).toString());
        }
    }

    static class ChatHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            sendResponse(exchange, 200, ActionExecutor.chat(readBody(exchange)).toString());
        }
    }

    // ─── 智能导航 Handlers ───────────────────────────

    /**
     * 导航到目标位置（带排除区域）
     * POST /api/navigate/goto
     */
    static class NavigateGotoHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            String result = PathfinderHandler.gotoTarget(readBody(exchange));
            sendResponse(exchange, 200, result);
        }
    }

    /**
     * 停止当前导航
     * POST /api/navigate/stop
     */
    static class NavigateStopHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkMethod(exchange, "POST")) return;
            String result = PathfinderHandler.stopNavigation();
            sendResponse(exchange, 200, result);
        }
    }

    /**
     * 获取寻路引擎状态
     * GET /api/navigate/status
     */
    static class NavigateStatusHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!checkAuth(exchange)) return;
            sendResponse(exchange, 200, PathfinderHandler.getStatus());
        }
    }

    // ─── 工具方法 ─────────────────────────────────────

    static boolean checkMethod(HttpExchange exchange, String method) throws IOException {
        if (!method.equals(exchange.getRequestMethod())) {
            sendResponse(exchange, 405, "{\"error\":\"Method not allowed\"}");
            return false;
        }
        return true;
    }

    static int parseQueryParam(HttpExchange exchange, String key, int defaultVal) {
        String query = exchange.getRequestURI().getQuery();
        if (query != null && query.contains(key + "=")) {
            try {
                return Integer.parseInt(query.split(key + "=")[1].split("&")[0]);
            } catch (NumberFormatException ignored) {}
        }
        return defaultVal;
    }

    static String parseQueryStr(HttpExchange exchange, String key) {
        String query = exchange.getRequestURI().getQuery();
        if (query != null && query.contains(key + "=")) {
            return query.split(key + "=")[1].split("&")[0];
        }
        return null;
    }
}
