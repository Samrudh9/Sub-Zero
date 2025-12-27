class Subscription {
  final String id;
  final String name;
  final String logoUrl;
  final double monthlyPrice;
  final String lastChargeDate;
  final double? usageScore;
  final String status; // 'active', 'cancelled', 'keeper'
  final String? cancellationUrl;

  Subscription({
    required this.id,
    required this.name,
    required this.logoUrl,
    required this.monthlyPrice,
    required this.lastChargeDate,
    this.usageScore,
    required this.status,
    this.cancellationUrl,
  });

  factory Subscription.fromJson(Map<String, dynamic> json) {
    return Subscription(
      id: json['id'] as String,
      name: json['name'] as String,
      logoUrl: json['logo_url'] as String,
      monthlyPrice: (json['monthly_price'] as num).toDouble(),
      lastChargeDate: json['last_charge_date'] as String,
      usageScore: json['usage_score'] != null 
          ? (json['usage_score'] as num).toDouble() 
          : null,
      status: json['status'] as String,
      cancellationUrl: json['cancellation_url'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'logo_url': logoUrl,
      'monthly_price': monthlyPrice,
      'last_charge_date': lastChargeDate,
      'usage_score': usageScore,
      'status': status,
      'cancellation_url': cancellationUrl,
    };
  }

  Subscription copyWith({
    String? id,
    String? name,
    String? logoUrl,
    double? monthlyPrice,
    String? lastChargeDate,
    double? usageScore,
    String? status,
    String? cancellationUrl,
  }) {
    return Subscription(
      id: id ?? this.id,
      name: name ?? this.name,
      logoUrl: logoUrl ?? this.logoUrl,
      monthlyPrice: monthlyPrice ?? this.monthlyPrice,
      lastChargeDate: lastChargeDate ?? this.lastChargeDate,
      usageScore: usageScore ?? this.usageScore,
      status: status ?? this.status,
      cancellationUrl: cancellationUrl ?? this.cancellationUrl,
    );
  }
}
