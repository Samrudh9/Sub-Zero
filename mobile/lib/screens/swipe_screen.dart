import 'package:flutter/material. dart';
import 'package: flutter_card_swiper/flutter_card_swiper.dart';
import '../models/subscription. dart';
import '../services/cancellation_service.dart';

class SwipeScreen extends StatefulWidget {
  const SwipeScreen({super.key});

  @override
  State<SwipeScreen> createState() => _SwipeScreenState();
}

class _SwipeScreenState extends State<SwipeScreen> {
  final CardSwiperController controller = CardSwiperController();
  final CancellationService _cancellationService = CancellationService();
  
  List<Subscription> subscriptions = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSubscriptions();
  }

  Future<void> _loadSubscriptions() async {
    // Loaded from Plaid via backend
    final subs = await _cancellationService.getDetectedSubscriptions();
    setState(() {
      subscriptions = subs;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E21),
      appBar: AppBar(
        title: const Text('Sub-Zero', style: TextStyle(color: Colors.cyan)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons. history, color: Colors.grey),
            onPressed: () => Navigator.pushNamed(context, '/graveyard'),
          )
        ],
      ),
      body: Column(
        children: [
          // Savings tracker
          Container(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Potential Savings:  \$${_calculateTotalSavings()}/year',
              style: const TextStyle(
                color: Colors.greenAccent,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          
          // Swipe cards
          Expanded(
            child: CardSwiper(
              controller: controller,
              cardsCount: subscriptions.length,
              onSwipe: _onSwipe,
              numberOfCardsDisplayed: 3,
              backCardOffset: const Offset(40, 40),
              padding: const EdgeInsets.all(24),
              cardBuilder: (context, index, _, __) => 
                  _buildSubscriptionCard(subscriptions[index]),
            ),
          ),
          
          // Action buttons
          Padding(
            padding: const EdgeInsets.all(24),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // KILL button
                FloatingActionButton(
                  heroTag: 'kill',
                  backgroundColor: Colors.red,
                  onPressed: () => controller.swipe(CardSwiperDirection.left),
                  child: const Icon(Icons.close, size: 32),
                ),
                // KEEP button
                FloatingActionButton(
                  heroTag: 'keep',
                  backgroundColor: Colors.green,
                  onPressed: () => controller.swipe(CardSwiperDirection.right),
                  child: const Icon(Icons.check, size: 32),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSubscriptionCard(Subscription sub) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Colors.grey[900]!, Colors.grey[850]!],
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.cyan.withOpacity(0.2),
            blurRadius: 20,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Service logo
            CircleAvatar(
              radius: 40,
              backgroundImage: NetworkImage(sub.logoUrl),
            ),
            const SizedBox(height: 16),
            
            // Service name
            Text(
              sub. name,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight. bold,
              ),
            ),
            const SizedBox(height: 8),
            
            // Monthly cost
            Text(
              '\$${sub.monthlyPrice. toStringAsFixed(2)}/month',
              style: const TextStyle(
                color: Colors.cyan,
                fontSize: 24,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '\$${(sub.monthlyPrice * 12).toStringAsFixed(2)}/year',
              style: TextStyle(
                color: Colors. grey[500],
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 16),
            
            // Last charge date
            Text(
              'Last charged: ${sub.lastChargeDate}',
              style: TextStyle(color: Colors.grey[400]),
            ),
            
            // Usage indicator (if available)
            if (sub. usageScore != null) ...[
              const SizedBox(height: 16),
              _buildUsageIndicator(sub. usageScore! ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildUsageIndicator(double score) {
    final color = score > 0. 7 ? Colors.green : score > 0.3 ? Colors.orange : Colors.red;
    final label = score > 0.7 ? 'High Usage' : score > 0.3 ? 'Medium Usage' : 'Rarely Used';
    
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(Icons.analytics, color: color, size: 16),
        const SizedBox(width: 4),
        Text(label, style: TextStyle(color:  color)),
      ],
    );
  }

  Future<bool> _onSwipe(
    int previousIndex,
    int?  currentIndex,
    CardSwiperDirection direction,
  ) async {
    final subscription = subscriptions[previousIndex];
    
    if (direction == CardSwiperDirection. left) {
      // KILL - Trigger cancellation workflow
      await _showCancellationDialog(subscription);
    } else {
      // KEEP - Mark as keeper
      await _cancellationService.markAsKeeper(subscription. id);
    }
    
    return true;
  }

  Future<void> _showCancellationDialog(Subscription sub) async {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[900],
        title: Text('Cancel ${sub.name}?', style: const TextStyle(color: Colors. white)),
        content: Text(
          'Sub-Zero will log in and cancel this for you. '
          'You may need to provide a verification code.',
          style: TextStyle(color: Colors.grey[400]),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Never mind'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () async {
              Navigator.pop(context);
              await _cancellationService.startCancellation(sub.id);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('🎯 Hitman deployed for ${sub.name}'),
                  backgroundColor: Colors.cyan[800],
                ),
              );
            },
            child: const Text('Kill It'),
          ),
        ],
      ),
    );
  }

  double _calculateTotalSavings() {
    return subscriptions.fold(0, (sum, sub) => sum + (sub.monthlyPrice * 12));
  }
}