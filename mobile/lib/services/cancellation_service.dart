import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/subscription.dart';
import '../models/graveyard_item.dart';

class CancellationService {
  // TODO: Replace with actual backend URL
  static const String baseUrl = 'http://localhost:3000/api';
  
  final http.Client _client;

  CancellationService({http.Client? client}) 
      : _client = client ?? http.Client();

  /// Fetches list of detected subscriptions from backend
  Future<List<Subscription>> getDetectedSubscriptions() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/subscriptions'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => Subscription.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load subscriptions: ${response.statusCode}');
      }
    } catch (e) {
      // Return mock data for development
      return _getMockSubscriptions();
    }
  }

  /// Starts the AI-powered cancellation workflow for a subscription
  Future<void> startCancellation(String subscriptionId) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/subscriptions/$subscriptionId/cancel'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'subscription_id': subscriptionId}),
      );

      if (response.statusCode != 200 && response.statusCode != 202) {
        throw Exception('Failed to start cancellation: ${response.statusCode}');
      }
    } catch (e) {
      // For development, just log the error
      print('Cancellation error: $e');
    }
  }

  /// Marks a subscription as one the user wants to keep
  Future<void> markAsKeeper(String subscriptionId) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/subscriptions/$subscriptionId/keep'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'subscription_id': subscriptionId}),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to mark as keeper: ${response.statusCode}');
      }
    } catch (e) {
      // For development, just log the error
      print('Mark as keeper error: $e');
    }
  }

  /// Fetches list of successfully cancelled subscriptions
  Future<List<GraveyardItem>> getGraveyard() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/graveyard'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => GraveyardItem.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load graveyard: ${response.statusCode}');
      }
    } catch (e) {
      // Return mock data for development
      return _getMockGraveyard();
    }
  }

  /// Calculates total annual savings from cancelled subscriptions
  Future<double> getTotalSavings() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/graveyard/savings'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return (data['total_annual_savings'] as num).toDouble();
      } else {
        throw Exception('Failed to load savings: ${response.statusCode}');
      }
    } catch (e) {
      // Calculate from graveyard for development
      final graveyard = await getGraveyard();
      return graveyard.fold(0.0, (sum, item) => sum + item.annualSavings);
    }
  }

  // Mock data for development/testing
  List<Subscription> _getMockSubscriptions() {
    return [
      Subscription(
        id: '1',
        name: 'Netflix',
        logoUrl: 'https://logo.clearbit.com/netflix.com',
        monthlyPrice: 15.99,
        lastChargeDate: '2024-01-15',
        usageScore: 0.85,
        status: 'active',
        cancellationUrl: 'https://www.netflix.com/cancelplan',
      ),
      Subscription(
        id: '2',
        name: 'Adobe Creative Cloud',
        logoUrl: 'https://logo.clearbit.com/adobe.com',
        monthlyPrice: 54.99,
        lastChargeDate: '2024-01-10',
        usageScore: 0.15,
        status: 'active',
        cancellationUrl: 'https://account.adobe.com/plans',
      ),
      Subscription(
        id: '3',
        name: 'Spotify Premium',
        logoUrl: 'https://logo.clearbit.com/spotify.com',
        monthlyPrice: 10.99,
        lastChargeDate: '2024-01-20',
        usageScore: 0.95,
        status: 'active',
        cancellationUrl: 'https://www.spotify.com/account/subscription/',
      ),
      Subscription(
        id: '4',
        name: 'Planet Fitness',
        logoUrl: 'https://logo.clearbit.com/planetfitness.com',
        monthlyPrice: 24.99,
        lastChargeDate: '2024-01-05',
        usageScore: 0.05,
        status: 'active',
      ),
      Subscription(
        id: '5',
        name: 'HelloFresh',
        logoUrl: 'https://logo.clearbit.com/hellofresh.com',
        monthlyPrice: 89.99,
        lastChargeDate: '2024-01-12',
        usageScore: 0.30,
        status: 'active',
        cancellationUrl: 'https://www.hellofresh.com/my-deliveries/cancel',
      ),
    ];
  }

  List<GraveyardItem> _getMockGraveyard() {
    return [
      GraveyardItem(
        id: '1',
        serviceName: 'Adobe Creative Cloud',
        monthlySavings: 54.99,
        cancelledAt: DateTime.now().subtract(const Duration(days: 7)),
        proofScreenshotUrl: 'https://via.placeholder.com/400x300?text=Adobe+Cancelled',
      ),
      GraveyardItem(
        id: '2',
        serviceName: 'Planet Fitness',
        monthlySavings: 24.99,
        cancelledAt: DateTime.now().subtract(const Duration(days: 14)),
        proofScreenshotUrl: 'https://via.placeholder.com/400x300?text=Planet+Fitness+Cancelled',
      ),
      GraveyardItem(
        id: '3',
        serviceName: 'HelloFresh',
        monthlySavings: 89.99,
        cancelledAt: DateTime.now().subtract(const Duration(days: 3)),
        proofScreenshotUrl: 'https://via.placeholder.com/400x300?text=HelloFresh+Cancelled',
      ),
    ];
  }
}
