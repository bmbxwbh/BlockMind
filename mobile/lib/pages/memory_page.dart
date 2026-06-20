import 'package:flutter/material.dart';
import '../services/api_service.dart';

class MemoryPage extends StatefulWidget {
  final ApiService api;
  const MemoryPage({super.key, required this.api});
  @override
  State<MemoryPage> createState() => _MemoryPageState();
}

class _MemoryPageState extends State<MemoryPage> {
  int zones = 0, paths = 0, strategies = 0, players = 0;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    final d = await widget.api.getMemory();
    if (d != null && mounted) setState(() {
      zones = d['zones'] ?? 0;
      paths = d['cached_paths'] ?? 0;
      strategies = d['strategies'] ?? 0;
      players = d['players'] ?? 0;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: ListView(children: [
        Row(children: [
          const Expanded(child: Text('记忆系统', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white))),
          IconButton(onPressed: _load, icon: const Icon(Icons.refresh, color: Color(0xFF888888))),
        ]),
        const SizedBox(height: 16),
        Wrap(spacing: 10, runSpacing: 10, children: [
          _card('区域', zones),
          _card('路径', paths),
          _card('策略', strategies),
          _card('玩家', players),
        ]),
      ]),
    );
  }

  Widget _card(String label, int count) {
    return Container(
      width: 160,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: const Color(0xFF161616), borderRadius: BorderRadius.circular(14)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label, style: const TextStyle(fontSize: 12, color: Color(0xFF666666))),
        const SizedBox(height: 4),
        Text('$count', style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFFEDEDED))),
      ]),
    );
  }
}
