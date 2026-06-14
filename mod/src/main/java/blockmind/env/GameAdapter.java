package blockmind.env;

import com.google.gson.JsonObject;

public interface GameAdapter {
    Object getPlayer();
    Object getWorld();
    Object getServer();

    JsonObject getStatus();
    JsonObject getInventory();
    JsonObject getEntities(int radius);
    JsonObject getBlocks(int radius);

    boolean move(double x, double y, double z, boolean sprint);
    boolean dig(int x, int y, int z);
    boolean place(String item, int x, int y, int z);
    boolean attack(int entityId);
    boolean eat(String item);
    boolean look(double x, double y, double z);
    boolean chat(String message);
}
