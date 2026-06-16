import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'pages/dashboard_page.dart';
import 'pages/chat_page.dart';
import 'pages/tasks_page.dart';
import 'pages/memory_page.dart';
import 'pages/settings_page.dart';
import 'services/api_service.dart';

void main() => runApp(const BlockMindApp());

class BlockMindApp extends StatefulWidget {
  const BlockMindApp({super.key});
  @override
  State<BlockMindApp> createState() => _BlockMindAppState();
}

class _BlockMindAppState extends State<BlockMindApp> {
  int _currentIndex = 0;
  late ApiService api;

  @override
  void initState() {
    super.initState();
    api = ApiService();
    _loadConfig();
  }

  Future<void> _loadConfig() async {
    final prefs = await SharedPreferences.getInstance();
    api.baseUrl = prefs.getString('baseUrl') ?? 'http://localhost:19951';
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BlockMind',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0A0A0A),
        cardColor: const Color(0xFF161616),
        dividerColor: const Color(0xFF1F1F1F),
        colorScheme: ColorScheme.dark(
          primary: const Color(0xFF7C5CFC),
          surface: const Color(0xFF161616),
          onSurface: const Color(0xFFEDEDED),
        ),
        textTheme: const TextTheme(
          bodyMedium: TextStyle(color: Color(0xFFEDEDED)),
          bodySmall: TextStyle(color: Color(0xFF888888)),
        ),
      ),
      home: Scaffold(
        body: IndexedStack(
          index: _currentIndex,
          children: [
            DashboardPage(api: api),
            ChatPage(api: api),
            TasksPage(api: api),
            MemoryPage(api: api),
            SettingsPage(api: api, onSaved: _loadConfig),
          ],
        ),
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (i) => setState(() => _currentIndex = i),
          type: BottomNavigationBarType.fixed,
          backgroundColor: const Color(0xFF111111),
          selectedItemColor: const Color(0xFF7C5CFC),
          unselectedItemColor: const Color(0xFF888888),
          items: [
            BottomNavigationBarItem(icon: Icon(Icons.dashboard), label: '仪表盘'),
            BottomNavigationBarItem(icon: Icon(Icons.chat), label: '对话'),
            BottomNavigationBarItem(icon: Icon(Icons.list), label: '任务'),
            BottomNavigationBarItem(icon: Icon(Icons.psychology), label: '记忆'),
            BottomNavigationBarItem(icon: Icon(Icons.settings), label: '设置'),
          ],
        ),
      ),
    );
  }
}
