# BlockMind Desktop

> Native desktop application for BlockMind Minecraft AI Companion

## Tech Stack

- **UI**: Avalonia UI 11.x (cross-platform native rendering)
- **Backend**: C# / .NET 8
- **Design**: Linear dark theme
- **AI**: Python subprocess (reuses existing AI engine)

## Build

```bash
cd desktop/src/BlockMind.Desktop
dotnet build
dotnet run
```

## Package

```bash
dotnet publish -c Release -r win-x64 --self-contained
dotnet publish -c Release -r osx-arm64 --self-contained
dotnet publish -c Release -r linux-x64 --self-contained
```

## Architecture

```
BlockMind.exe
├── Avalonia UI (XAML + C#)
├── Services (AppService, ModClient, AiClient, PythonBridge)
├── ViewModels (MVVM pattern)
└── Python subprocess (AI engine)
```

## Pages

| Page | Status |
|------|--------|
| Dashboard | Complete |
| Chat | Complete |
| Model Config | Complete |
| Memory | Complete |
| Skills | Complete |
| Settings | Complete |
| Map | Placeholder |
| Marketplace | Placeholder |
| Safety | Placeholder |
| Tasks | Placeholder |
| Logs | Placeholder |
