package blockmind.env;

import blockmind.bot.BotManager;
import blockmind.executor.ActionExecutor;
import blockmind.collector.StateCollector;
import com.google.gson.JsonObject;

public class ServerAdapter implements GameAdapter {

    private final Object server;

    public ServerAdapter(Object server) {
        this.server = server;
    }

    @Override
    public Object getPlayer() {
        return BotManager.isSpawned() ? BotManager.getBot() : null;
    }

    @Override
    public Object getWorld() {
        try {
            var compat = blockmind.compat.VersionCompat.getCompat();
            return compat.getWorld(server);
        } catch (Exception e) {
            return null;
        }
    }

    @Override
    public Object getServer() { return server; }

    @Override
    public JsonObject getStatus() { return StateCollector.getStatus(); }

    @Override
    public JsonObject getInventory() { return StateCollector.getInventory(); }

    @Override
    public JsonObject getEntities(int radius) { return StateCollector.getEntities(radius); }

    @Override
    public JsonObject getBlocks(int radius) { return StateCollector.getBlocks(radius, "any"); }

    @Override
    public boolean move(double x, double y, double z, boolean sprint) {
        var r = ActionExecutor.move(buildMoveJson(x, y, z, sprint).toString());
        return r.has("success") && r.get("success").getAsBoolean();
    }

    @Override
    public boolean dig(int x, int y, int z) {
        var r = ActionExecutor.dig(buildPosJson(x, y, z).toString());
        return r.has("success") && r.get("success").getAsBoolean();
    }

    @Override
    public boolean place(String item, int x, int y, int z) {
        var r = ActionExecutor.place(buildPlaceJson(item, x, y, z).toString());
        return r.has("success") && r.get("success").getAsBoolean();
    }

    @Override
    public boolean attack(int entityId) {
        var json = new JsonObject();
        json.addProperty("entity_id", entityId);
        var r = ActionExecutor.attack(json.toString());
        return r.has("success") && r.get("success").getAsBoolean();
    }

    @Override
    public boolean eat(String item) {
        var json = new JsonObject();
        json.addProperty("item", item);
        var r = ActionExecutor.eat(json.toString());
        return r.has("success") && r.get("success").getAsBoolean();
    }

    @Override
    public boolean look(double x, double y, double z) {
        var r = ActionExecutor.look(buildPosJson(x, y, z).toString());
        return r.has("success") && r.get("success").getAsBoolean();
    }

    @Override
    public boolean chat(String message) {
        var r = ActionExecutor.chat(buildChatJson(message).toString());
        return r.has("success") && r.get("success").getAsBoolean();
    }

    private static JsonObject buildMoveJson(double x, double y, double z, boolean sprint) {
        var json = new JsonObject();
        json.addProperty("x", x); json.addProperty("y", y); json.addProperty("z", z);
        json.addProperty("sprint", sprint);
        return json;
    }

    private static JsonObject buildPosJson(double x, double y, double z) {
        var json = new JsonObject();
        json.addProperty("x", x); json.addProperty("y", y); json.addProperty("z", z);
        return json;
    }

    private static JsonObject buildPlaceJson(String item, int x, int y, int z) {
        var json = new JsonObject();
        json.addProperty("item", item);
        json.addProperty("x", x); json.addProperty("y", y); json.addProperty("z", z);
        return json;
    }

    private static JsonObject buildChatJson(String msg) {
        var json = new JsonObject();
        json.addProperty("message", msg);
        return json;
    }
}
