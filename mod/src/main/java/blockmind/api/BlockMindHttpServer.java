package blockmind.api;

import blockmind.BlockMindMod;
import blockmind.collector.StateCollector;
import blockmind.executor.ActionExecutor;
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
 */
public class BlockMindHttpServer {

    private final int port;
    private com.sun.net.httpserver.HttpServer server;

    public BlockMindHttpServer(int port) {
        this.port = port;
    }

    public void start() throws IOException {
        server = com.sun.net.httpserver.HttpServer.create(new InetSocketAddress(port), 0);
        server.setExecutor(Executors.newFixedThreadPool(4));

        // 注册路由
        server.createContext("/health", new HealthHandler());
        server.createContext("/api/status", new StatusHandler());
        server.createContext("/api/world", new WorldHandler());
        server.createContext("/api/inventory", new InventoryHandler());
        server.createContext("/api/entities", new EntitiesHandler());
        server.createContext("/api/blocks", new BlocksHandler());
        server.createContext("/api/move", new MoveHandler());
        server.createContext("/api/dig", new DigHandler());
        server.createContext("/api/place", new PlaceHandler());
        server.createContext("/api/attack", new AttackHandler());
        server.createContext("/api/eat", new EatHandler());
        server.createContext("/api/look", new LookHandler());
        server.createContext("/api/chat", new ChatHandler());

        server.start();
        BlockMindMod.LOGGER.info("[BlockMind] HTTP API listening on port {}", port);
    }

    public void stop() {
        if (server != null) {
            server.stop(0);
        }
    }

    // ─── 辅助方法 ─────────────────────────────────────

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
            sendResponse(exchange, 200, "{\"status\":\"ok\",\"mod\":\"blockmind\"}");
        }
    }

    static class StatusHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            sendResponse(exchange, 200, StateCollector.getStatus().toString());
        }
    }

    static class WorldHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            sendResponse(exchange, 200, StateCollector.getWorld().toString());
        }
    }

    static class InventoryHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
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
