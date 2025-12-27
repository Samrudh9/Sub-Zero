# Sub-Zero Mobile App

The Flutter mobile application for Sub-Zero - AI-Powered Subscription Assassin.

## 🎯 Features

- **Tinder-Style Swipe Interface**: Swipe left to kill subscriptions, right to keep them
- **The Graveyard**: View your cancelled subscriptions and track total savings
- **Dark Theme**: Sub-Zero branded dark theme with cyan accents
- **Mock Data Support**: Works with mock data for development when backend is unavailable

## 🏗️ Project Structure

```
mobile/
├── lib/
│   ├── main.dart                      # App entry point
│   ├── models/
│   │   ├── subscription.dart          # Subscription data model
│   │   └── graveyard_item.dart        # Cancelled subscription model
│   ├── services/
│   │   └── cancellation_service.dart  # API service with mock data
│   └── screens/
│       ├── swipe_screen.dart          # Main swipe interface
│       └── graveyard_screen.dart      # Cancelled subscriptions view
└── pubspec.yaml                       # Dependencies
```

## 🚀 Getting Started

### Prerequisites

- Flutter SDK 3.0.0 or higher
- Dart SDK 3.0.0 or higher

### Installation

1. Install dependencies:
```bash
cd mobile
flutter pub get
```

2. Run the app:
```bash
flutter run
```

For specific platforms:
```bash
flutter run -d chrome      # Web
flutter run -d android     # Android
flutter run -d ios         # iOS
```

## 📱 Screens

### Swipe Screen (`/swipe`)
- Main interface for reviewing subscriptions
- Displays subscription cards with:
  - Service logo and name
  - Monthly and annual cost
  - Last charge date
  - Usage score indicator
- Swipe left to cancel, right to keep
- Shows potential annual savings at the top

### Graveyard Screen (`/graveyard`)
- Accessible via history icon in app bar
- Displays all cancelled subscriptions
- Shows total annual savings prominently
- Each item displays:
  - Service name with celebration icon
  - Monthly and annual savings
  - Cancellation date
  - Proof screenshot thumbnail
- Tap any item to view full cancellation proof

## 🎨 Design System

### Colors
- Background: `#0A0E21` (Dark blue)
- Surface: `#1D1E33` (Slightly lighter blue)
- Primary: `Colors.cyan`
- Secondary: `Colors.cyanAccent`
- Success: `Colors.greenAccent`
- Danger: `Colors.red`

### Typography
- Headers: Bold, white text with cyan accents
- Body: White/white70 for primary/secondary text
- Accent text: Cyan for branding, green for savings

## 🔌 Backend Integration

The `CancellationService` class provides API integration:

```dart
class CancellationService {
  Future<List<Subscription>> getDetectedSubscriptions();
  Future<void> startCancellation(String subscriptionId);
  Future<void> markAsKeeper(String subscriptionId);
  Future<List<GraveyardItem>> getGraveyard();
  Future<double> getTotalSavings();
}
```

**Current Status**: Mock data is used when the backend is unavailable. Update `baseUrl` in `cancellation_service.dart` to point to your backend API.

### API Endpoints Expected

```
GET  /api/subscriptions              # List detected subscriptions
POST /api/subscriptions/:id/cancel   # Start cancellation workflow
POST /api/subscriptions/:id/keep     # Mark as keeper
GET  /api/graveyard                  # List cancelled subscriptions
GET  /api/graveyard/savings          # Get total savings
```

## 🧪 Development

### Mock Data

The app includes mock subscription data for development:
- Netflix ($15.99/mo)
- Adobe Creative Cloud ($54.99/mo)
- Spotify Premium ($10.99/mo)
- Planet Fitness ($24.99/mo)
- HelloFresh ($89.99/mo)

Mock graveyard items are also included to test the UI.

### Adding New Features

1. Models go in `lib/models/`
2. API services go in `lib/services/`
3. UI screens go in `lib/screens/`
4. Update routes in `lib/main.dart`

## 📦 Dependencies

- `flutter_card_swiper: ^6.0.0` - Tinder-style swipe cards
- `http: ^1.1.0` - HTTP client for API calls
- `provider: ^6.1.0` - State management (for future use)
- `shared_preferences: ^2.2.0` - Local storage (for future use)
- `intl: ^0.18.0` - Date formatting

## 🐛 Known Issues

- Backend integration is not yet complete
- Authentication/authorization not implemented
- Real-time updates for cancellation status pending
- Push notifications not implemented

## 🔜 Roadmap

- [ ] Connect to real backend API
- [ ] Add user authentication
- [ ] Implement real-time cancellation status updates
- [ ] Add push notifications for cancellation completion
- [ ] Implement undo functionality
- [ ] Add filters and search for subscriptions
- [ ] Add subscription categorization
- [ ] Implement data persistence with shared_preferences

## 📄 License

MIT License - see root LICENSE file for details.
