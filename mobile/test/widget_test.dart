import 'package:flutter_test/flutter_test.dart';
import 'package:blockmind_mobile/main.dart';

void main() {
  testWidgets('App starts', (WidgetTester tester) async {
    await tester.pumpWidget(const BlockMindApp());
    expect(find.text('仪表盘'), findsOneWidget);
  });
}
