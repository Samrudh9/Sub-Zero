class GraveyardItem {
  final String id;
  final String serviceName;
  final double monthlySavings;
  final DateTime cancelledAt;
  final String? proofScreenshotUrl;
  final String? proofVideoUrl;

  GraveyardItem({
    required this.id,
    required this.serviceName,
    required this.monthlySavings,
    required this.cancelledAt,
    this.proofScreenshotUrl,
    this.proofVideoUrl,
  });

  factory GraveyardItem.fromJson(Map<String, dynamic> json) {
    return GraveyardItem(
      id: json['id'] as String,
      serviceName: json['service_name'] as String,
      monthlySavings: (json['monthly_savings'] as num).toDouble(),
      cancelledAt: DateTime.parse(json['cancelled_at'] as String),
      proofScreenshotUrl: json['proof_screenshot_url'] as String?,
      proofVideoUrl: json['proof_video_url'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'service_name': serviceName,
      'monthly_savings': monthlySavings,
      'cancelled_at': cancelledAt.toIso8601String(),
      'proof_screenshot_url': proofScreenshotUrl,
      'proof_video_url': proofVideoUrl,
    };
  }

  double get annualSavings => monthlySavings * 12;
}
