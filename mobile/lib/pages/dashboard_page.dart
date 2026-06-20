import 'package:flutter/material.dart';
import '../services/api_service.dart';

class DashboardPage extends StatefulWidget {
  final ApiService api;
  const DashboardPage({super.key, required this.api});
  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  double health = 0, hunger = 0;
  String position = '--', dimension = '--';
  bool connected = false;

  @override
  void initState() {
    super.initState();
    _poll();
  }

  Future<void> _poll() async {
    while (mounted) {
      final d = await widget.api.getDashboard();
      if (d != null && mounted) {
        setState(() {
          connected = true;
          health = (d['health'] ?? 0).toDouble();
          hunger = (d['hunger'] ?? 0).toDouble();
          position = d['position']?.toString() ?? '--';
          dimension = d['dimension']?.toString() ?? '--';
        });
      } else if (mounted) {
        setState(() => connected = false);
      }
      await Future.delayed(const Duration(seconds: 3));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: ListView(children: [
        const Text('仪表盘', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 16),
        _statusRow(),
        const SizedBox(height: 16),
        if (!connected) _connectionHint(),
        _quickActions(),
      ]),
    );
  }

  Widget _statusRow() {
    return Wrap(spacing: 10, runSpacing: 10, children: [
      _card('生命值', '${health.toInt()}/20', const Color(0xFF00D68F)),
      _card('饥饿值', '${hunger.toInt()}/20', const Color(0xFFFFAA00)),
      _card('位置', position, const Color(0xFF7C5CFC)),
      _card('维度', dimension, const Color(0xFF3B82F6)),
    ]);
  }

  Widget _card(String label, String value, Color accent) {
    return Container(
      width: 160,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: const Color(0xFF161616), borderRadius: BorderRadius.circular(14)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label, style: const TextStyle(fontSize: 12, color: Color(0xFF666666))),
        const SizedBox(height: 4),
        Text(value, style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: accent)),
      ]),
    );
  }

  Widget _connectionHint() {
    return Container(
      padding: const EdgeInsets.all(20),
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(color: const Color(0xFF161616), borderRadius: BorderRadius.circular(14)),
      child: const Column(children: [
        Text('未连接到后端', style: TextStyle(fontSize: 15, color: Color(0xFF888888))),
        SizedBox(height: 4),
        Text('请先启动 BlockMind 后端，然后在设置中配置地址', style: TextStyle(fontSize: 12, color: Color(0xFF555555))),
      ]),
    );
  }

  Widget _quickActions() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: const Color(0xFF161616), borderRadius: BorderRadius.circular(14)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('快捷操作', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Colors.white)),
        const SizedBox(height: 12),
        Wrap(spacing: 8, runSpacing: 8, children: [
          _actionBtn('回家', '回家'),
          _actionBtn('挖矿', '挖矿'),
          _actionBtn('砍树', '砍树'),
          _actionBtn('吃东西', '吃东西'),
          _actionBtn('巡逻', '巡逻'),
          _actionBtn('停止', '停止', color: const Color(0xFFFF3B3B)),
        ]),
      ]),
    );
  }

  Widget _actionBtn(String label, String cmd, {Color color = const Color(0xFFEDEDED)}) {
    return ElevatedButton(
      onPressed: () => widget.api.sendCommand(cmd),
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF1E1E1E),
        foregroundColor: color,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10), side: const BorderSide(color: Color(0xFF2A2A2A))),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      ),
      child: Text(label),
    );
  }
}
