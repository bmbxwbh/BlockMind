import 'package:flutter/material.dart';
import '../services/api_service.dart';

class TasksPage extends StatefulWidget {
  final ApiService api;
  const TasksPage({super.key, required this.api});
  @override
  State<TasksPage> createState() => _TasksPageState();
}

class _TasksPageState extends State<TasksPage> {
  int pending = 0, running = 0, completed = 0;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    final d = await widget.api.getTasks();
    if (d != null && mounted) setState(() {
      pending = d['pending'] ?? 0;
      running = d['running'] ?? 0;
      completed = d['completed'] ?? 0;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: ListView(children: [
        Row(children: [
          const Expanded(child: Text('任务队列', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white))),
          IconButton(onPressed: _load, icon: const Icon(Icons.refresh, color: Color(0xFF888888))),
        ]),
        const SizedBox(height: 16),
        Wrap(spacing: 10, runSpacing: 10, children: [
          _card('待执行', pending, const Color(0xFFFFAA00)),
          _card('运行中', running, const Color(0xFF3B82F6)),
          _card('已完成', completed, const Color(0xFF00D68F)),
        ]),
      ]),
    );
  }

  Widget _card(String label, int count, Color accent) {
    return Container(
      width: 160,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: const Color(0xFF161616), borderRadius: BorderRadius.circular(14)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label, style: const TextStyle(fontSize: 12, color: Color(0xFF666666))),
        const SizedBox(height: 4),
        Text('$count', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: accent)),
      ]),
    );
  }
}
