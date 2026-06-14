package blockmind.env;

import net.fabricmc.loader.api.FabricLoader;

public final class EnvironmentDetector {
    private EnvironmentDetector() {}

    public static boolean isClient() {
        return FabricLoader.getInstance().getEnvironmentType() == net.fabricmc.api.EnvType.CLIENT;
    }

    public static boolean isServer() {
        return FabricLoader.getInstance().getEnvironmentType() == net.fabricmc.api.EnvType.SERVER;
    }
}
