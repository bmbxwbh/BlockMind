import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ChatPage extends StatefulWidget {
  final ApiService api;
  const ChatPage({super.key, required this.api});
  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final _ctrl = TextEditingController();
  final _scroll = ScrollController();
  final List<_Msg> _msgs = [_Msg('Bot', '你好！我是 BlockMind，有什么可以帮你的？', false)];
  bool _busy = false;

  Future<void> _send() async {
    final text = _ctrl.text.trim();
    if (text.isEmpty || _busy) return;
    _ctrl.clear();
    setState(() { _msgs.add(_Msg('你', text, true)); _busy = true; });
    _scrollToBottom();

    final r = await widget.api.chatWithAI(text);
    final reply = r?['response']?.toString() ?? 'AI 暂时无法回复';
    setState(() { _msgs.add(_Msg('Bot', reply, false)); _busy = false; });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scroll.hasClients) _scroll.animateTo(_scroll.position.maxScrollExtent, duration: const Duration(milliseconds: 200), curve: Curves.easeOut);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Expanded(child: ListView.builder(
        controller: _scroll,
        padding: const EdgeInsets.all(16),
        itemCount: _msgs.length,
        itemBuilder: (_, i) {
          final m = _msgs[i];
          return Align(
            alignment: m.isUser ? Alignment.centerRight : Alignment.centerLeft,
            child: Container(
              margin: const EdgeInsets.symmetric(vertical: 4),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
              decoration: BoxDecoration(color: const Color(0xFF161616), borderRadius: BorderRadius.circular(14)),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(m.sender, style: const TextStyle(fontSize: 11, color: Color(0xFF7C5CFC), fontWeight: FontWeight.w600)),
                const SizedBox(height: 4),
                Text(m.text, style: const TextStyle(fontSize: 14, color: Color(0xFFEDEDED))),
              ]),
            ),
          );
        },
      )),
      Container(
        padding: const EdgeInsets.all(12),
        color: const Color(0xFF111111),
        child: Row(children: [
          Expanded(child: TextField(
            controller: _ctrl,
            style: const TextStyle(color: Color(0xFFEDEDED)),
            decoration: InputDecoration(
              hintText: '输入消息...',
              hintStyle: const TextStyle(color: Color(0xFF555555)),
              filled: true,
              fillColor: const Color(0xFF161616),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            ),
            onSubmitted: (_) => _send(),
          )),
          const SizedBox(width: 8),
          IconButton(
            onPressed: _busy ? null : _send,
            icon: Icon(Icons.send, color: _busy ? const Color(0xFF555555) : const Color(0xFF7C5CFC)),
          ),
        ]),
      ),
    ]);
  }
}

class _Msg {
  final String sender, text;
  final bool isUser;
  _Msg(this.sender, this.text, this.isUser);
}
