import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class SettingsPage extends StatefulWidget {
  final ApiService api;
  final VoidCallback onSaved;
  const SettingsPage({super.key, required this.api, required this.onSaved});
  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  final _urlCtrl = TextEditingController();
  final _passCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _urlCtrl.text = widget.api.baseUrl;
  }

  Future<void> _save() async {
    final prefs = await SharedPreferences.getInstance();
    widget.api.baseUrl = _urlCtrl.text.trim();
    await prefs.setString('baseUrl', widget.api.baseUrl);
    final pass = _passCtrl.text.trim();
    if (pass.isNotEmpty) await widget.api.login(pass);
    widget.onSaved();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('已保存'), backgroundColor: Color(0xFF00D68F)));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: ListView(children: [
        const Text('设置', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 16),
        _section('连接', [
          _field('后端地址', _urlCtrl, 'http://localhost:19951'),
          const SizedBox(height: 12),
          _field('密码', _passCtrl, 'WebUI 密码', obscure: true),
        ]),
        const SizedBox(height: 16),
        _section('关于', [
          const Text('BlockMind Mobile v1.0.0', style: TextStyle(color: Color(0xFF888888))),
          const SizedBox(height: 4),
          const Text('Minecraft AI Companion 手机客户端', style: TextStyle(color: Color(0xFF555555), fontSize: 12)),
          const SizedBox(height: 4),
          const Text('仅用于查看和控制，不包含后端功能', style: TextStyle(color: Color(0xFF555555), fontSize: 12)),
        ]),
        const SizedBox(height: 24),
        ElevatedButton(
          onPressed: _save,
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF7C5CFC),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            padding: const EdgeInsets.symmetric(vertical: 14),
          ),
          child: const Text('保存设置', style: TextStyle(fontSize: 15)),
        ),
      ]),
    );
  }

  Widget _section(String title, List<Widget> children) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: const Color(0xFF161616), borderRadius: BorderRadius.circular(14)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Colors.white)),
        const SizedBox(height: 12),
        ...children,
      ]),
    );
  }

  Widget _field(String label, TextEditingController ctrl, String hint, {bool obscure = false}) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: const TextStyle(fontSize: 12, color: Color(0xFF888888))),
      const SizedBox(height: 4),
      TextField(
        controller: ctrl,
        obscureText: obscure,
        style: const TextStyle(color: Color(0xFFEDEDED)),
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: const TextStyle(color: Color(0xFF555555)),
          filled: true,
          fillColor: const Color(0xFF1E1E1E),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFF2A2A2A))),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFF2A2A2A))),
          contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        ),
      ),
    ]);
  }
}
