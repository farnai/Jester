# JESTER — FRONTEND ARCHITECTURE SPECIFICATION

**Document Version:** `1.1.0`  
**System Roles:** Lead Product Architect, Senior Frontend Systems Architect, React Native / Expo Architect, Design Systems Architect  
**Backend Reference Version:** `synastry-v1.0.0` (Production Ready, 188/188 passing tests)  
**Parent Blueprint:** [`docs/FRONTEND_CAPABILITY_SPECIFICATION.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/FRONTEND_CAPABILITY_SPECIFICATION.md)  
**Parent Product Spec:** [`docs/PRODUCT_SPECIFICATION.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/PRODUCT_SPECIFICATION.md)  
**Status:** Authoritative Frontend Architectural Blueprint (Cross-Platform / Universal Target Architecture)  

---

## 1. Architectural Principles

The JESTER frontend is designed as a deterministic, privacy-first, human-first client application engineered to run across **iOS, Android, and Desktop/Mobile Web** from a single unified codebase.

1. **Backend as the Single Source of Truth `[FROZEN]`**: The frontend is strictly a presentation, interaction, and state-orchestration layer. It never computes, derives, or approximates astronomical coordinates, aspect geometries, synastry dimensions, or compatibility scores.
2. **Deterministic Rendering `[FROZEN]`**: All compatibility representations (scores, dimensions, signals, topics, conversation starters) are direct, reproducible renderings of backend JSON payloads.
3. **Strict Privacy Invariants `[FROZEN]`**: The client strictly prevents exposure, caching, or accidental logging of private astronomical data (`astro_private`), raw coordinate degrees of other users, or internal mathematical audit traces (`evidence_trace`).
4. **Human-First JESTER Persona `[FROZEN]`**: JESTER is not a raw technical astrology dashboard, nor a generic dating swipe app. Astrological signals serve as the deterministic intelligence layer that fuels sharp, witty, penetrating relationship observations (`Score creates curiosity. Interpretation creates value.`).
5. **Universal Cross-Platform Architecture `[RECOMMENDED]`**: A single unified component and business logic tree targets iOS, Android, and Web using React Native primitives (`View`, `Text`, `Pressable`), NativeWind utility styling, and universal platform abstractions (`platform/`), eliminating dual-codebase divergence.
6. **Decoupled Server and Local UI State `[FROZEN]`**: Server state (profiles, connections, compatibility, chat history, notifications) is managed exclusively by an asynchronous query caching layer (TanStack Query); local transient UI state (active tabs, modal sheets, draft text, interaction animations) is kept strictly isolated.
7. **Graceful Privacy Degradation `[FROZEN]`**: Blocked users or non-discoverable resources return standardized privacy-safe `404 Not Found` responses, which the client renders as standard "Resource Not Found" without leaking existence oracles.
8. **Realtime-Synchronized Caching `[FROZEN]`**: Direct messaging and notifications maintain bidirectional synchronization between local TanStack query caches and Supabase Realtime WebSocket streams, with automatic channel cleanup and message deduplication.
9. **Zero Business Logic Duplication `[FROZEN]`**: Validation rules, connection state machine transitions, and access guards live on the server; the frontend adheres strictly to server-provided error codes and status transitions.
10. **Platform Abstraction Boundary `[RECOMMENDED]`**: Hardware and OS-specific features (SecureStore, Push Notifications, Haptics, Share Sheets, Deep Links) are wrapped behind universal facade interfaces (`platform/`) to preserve 100% shared business logic.

---

## 2. Platform Strategy

### 2.1 Strategic Decision: Universal Expo / React Native Stack
To fulfill JESTER's multi-platform mandate (iOS, Android, Desktop Web, Mobile Web) without requiring a future rewrite of the mobile application from scratch, JESTER adopts the **Universal Expo Architecture** as its target platform standard:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        JESTER CLIENT APPLICATION                       │
├────────────────────────────────────────────────────────────────────────┤
│                       SHARED APPLICATION LAYER                         │
│   • Domain Features: ME, YOU, WHY, US, CONNECT, CHAT, NOTIFICATIONS    │
│   • Universal Navigation: Expo Router / Universal Stack & Tabs        │
│   • Universal State: TanStack Query v5 + Auth Context                 │
│   • Universal Design System: UI Primitives + NativeWind v4 Tokens      │
├────────────────────────────────────────────────────────────────────────┤
│                      PLATFORM ABSTRACTION LAYER                        │
│   [platform/storage] [platform/haptics] [platform/notifications]      │
│   [platform/share]   [platform/linking] [platform/clipboard]          │
├──────────────────────────┬─────────────────────────────────────────────┤
│      NATIVE RUNTIME      │                 WEB RUNTIME                 │
│  • React Native (0.76+)  │  • React Native Web (RNW)                   │
│  • iOS (Swift / JSC/Hermes) • Desktop Web (Chrome, Safari, Firefox, Edge)│
│  • Android (Kotlin/Hermes) • Mobile Web (iOS Safari, Android Chrome)    │
│  • Expo SDK 52+ Modules  │  • Static / SSR / Responsive Shell          │
└──────────────────────────┴─────────────────────────────────────────────┘
```

### 2.2 Platform Evaluation & Decision Status
- **Core Framework**: Expo SDK 52+ with React Native 0.76+ `[RECOMMENDED]`
- **Web Bundler / Engine**: Expo Web / Metro with React Native Web `[RECOMMENDED]`
- **Navigation Runtime**: Expo Router v4 (Universal File-Based Routing) `[RECOMMENDED]`
- **Styling Compiler**: NativeWind v4 (Tailwind CSS for React Native & Web) `[RECOMMENDED]`
- **Server State**: TanStack Query v5 `[FROZEN]`
- **Authentication & Realtime**: Supabase JS v2 client `[FROZEN]`
- **Current Scaffold State**: Vite 8.2 + React DOM 19 + React Router v7 + Vanilla CSS `[IMPLEMENTED - RUNNING]`
- **Migration Plan**: Phased, non-disruptive migration from Vite/DOM to Universal Expo `[NOT YET IMPLEMENTED]`

---

## 3. Application Shell

The Application Shell provides the persistent frame, authentication gating, layout boundaries, and global notification subscriptions.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          GLOBAL APP SHELL                              │
│  [Network Monitor] [Auth Interceptor] [Global Realtime Orchestrator]   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌──────────────────────────────────┐        ┌──────────────────────────────────┐
│       UNAUTHENTICATED SHELL      │        │        AUTHENTICATED SHELL       │
│  • Welcome / Brand Narrative     │        │  • Adaptive Top Header (Desktop) │
│  • Login / Register Container    │        │  • Persistent Bottom Bar (Mobile)│
│  • Password Reset / Recovery     │        │  • Realtime Notification Manager │
│  • Deep Link Return Watchdog     │        │  • Adaptive Content Viewport     │
└──────────────────────────────────┘        └──────────────────────────────────┘
```

### 3.1 Unauthenticated Shell `[FROZEN]`
- Gated container for `/auth/login`, `/auth/register`, and session recovery.
- Catches unauthenticated deep links and preserves the intended redirect target (`return_to`).
- Clears all stale local user state, query caches, and active WebSocket subscriptions upon entry.

### 3.2 Authenticated Shell `[FROZEN]`
- **Desktop**: Persistent top header navigation (`HOME`, `DISCOVER`, `MESSAGES`, `ME`), notification indicator with unread count badge, and user identity chip.
- **Mobile**: Persistent bottom tab bar (`HOME`, `DISCOVER`, `MESSAGES`, `ME`) optimized for thumb navigation and 48px+ touch targets.
- **Realtime Listener**: Maintains active WebSocket channel to `public:notifications:user_id=eq.{my_id}`.
- **Onboarding Interceptor**: Evaluates `birth_data` presence; redirects incomplete accounts to `/onboarding/birth-data`.

---

## 4. Information Architecture & Navigation

### 4.1 Product Loop: ME → YOU → US → MORE PEOPLE `[FROZEN]`
JESTER's information hierarchy maps directly to the relationship intelligence loop:

```
JESTER V1
│
├── 1. AUTHENTICATION & ONBOARDING
│   ├── Login (/auth/login)
│   ├── Register (/auth/register)
│   └── Birth Data Onboarding (/onboarding/birth-data)
│
├── 2. ME (Astrological Self-Understanding & Dossier)
│   ├── Personal Astrology & Insights (/me)
│   └── Profile Settings (/me/settings)
│
├── 3. YOU / DISCOVER (People & Curiosity)
│   ├── Discover Feed (/discover)
│   └── Person Profile (/people/{id})
│
├── 4. WHY & US (Relationship Intelligence & Synastry)
│   ├── Comparison Overview (/compare/{id}) [Score, 4 Dimensions, Signals]
│   └── Deep-Dive Explanation (/people/{id}/why) [Dynamics, Topics, Starters]
│
├── 5. CONNECTIONS (Social Graph Management)
│   ├── Active Connections (/connections?tab=active)
│   └── Pending Requests (/connections?tab=pending)
│
├── 6. MESSAGES & CHAT (Direct Realtime Communication)
│   ├── Conversations List (/messages)
│   └── Active Chat Thread (/chat/{conversation_id}) [Realtime, Starters Injection]
│
└── 7. NOTIFICATIONS
    └── Notification Center (/notifications) [Requests, Accepts, Daily Sync]
```

### 4.2 Route Architecture Specification `[FROZEN]`

| Route | Platform URL | Purpose & Data Contract | Access Guard | Primary Action |
| :--- | :--- | :--- | :--- | :--- |
| **Login** | `/auth/login` | Supabase credentials auth | Public | Sign in, navigate to app |
| **Register** | `/auth/register` | New account registration | Public | Sign up, navigate to onboarding |
| **Onboarding** | `/onboarding/birth-data` | Collect birth parameters | Auth Required | Submit birth data -> calculate natal |
| **Home** | `/` (Index) | Daily energy, active pulse | Onboarded | Jump into ME or DISCOVER |
| **Discover** | `/discover` | Discoverable people feed | Onboarded | Browse cards, initiate connect |
| **Person** | `/people/:id` | View public profile & safe signs | Onboarded | Send connect request, view why |
| **Why Person** | `/people/:id/why` | Deep synastry dynamics & starters | Onboarded | Copy/send starter to chat |
| **Compare** | `/compare/:id` | Score (10-98), 4 dimensions, signals | Connected | Analyze compatibility |
| **Connections**| `/connections` | Active & pending relationship graph| Onboarded | Accept, decline, remove, block |
| **Messages** | `/messages` | Conversation threads list | Onboarded | Open chat thread |
| **Chat** | `/chat/:id` | Realtime messaging with starters | Connected | Send message, insert starter |
| **Me** | `/me` | Personal placements & insights | Onboarded | Read personal dossier, edit profile |
| **Notifications**| `/notifications`| In-app alert feed | Onboarded | Mark read, navigate to trigger |

---

## 5. Design System Architecture

### 5.1 Design System Philosophy `[FROZEN]`
JESTER is an engine of **insight, wit, and provocative psychological clarity**. It rejects generic, colorful horoscope aesthetics, pastel spiritual clichés, and gamified dating swipe cards. The design language expresses:
- **Depth & Contrast**: High-contrast, sleek surfaces with purposeful elevation.
- **Editorial Precision**: Monospace accents for astrological coordinates/aspect metrics paired with refined sans-serif for sharp JESTER prose.
- **Tactile Weight**: Distinct tactile feedback for state changes, connection locks, and score reveals.

### 5.2 Layered System Hierarchy `[FROZEN]`

```
┌─────────────────────────────────────────────────────────────┐
│                    1. DESIGN TOKENS                         │
│  (Colors, Typography, Spacing, Radii, Shadows, Motion)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    2. TAILWIND THEME                        │
│  (NativeWind tailwind.config.js token mappings)             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    3. UI PRIMITIVES                         │
│  (Box, Text, Button, Card, Badge, Input, Avatar, Skeleton)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 4. JESTER PRODUCT COMPONENTS                │
│  (InsightCard, PersonCard, ScoreGauge, StarterChip, etc.)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 5. FEATURE MODULE SCREENS                   │
│  (MeScreen, DiscoverScreen, WhyScreen, ChatScreen, etc.)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Design Token Architecture `[RECOMMENDED]`

Design tokens are structured as immutable TypeScript constants (`ui/tokens/`):

### 6.1 Color Tokens (`tokens/colors.ts`)
```typescript
export const colors = {
  // Brand & Accent
  brand: {
    DEFAULT: "#6366f1", // Indigo 500
    hover: "#4f46e5",   // Indigo 600
    subtle: "#eef2ff",  // Indigo 50
    border: "#c7d2fe",  // Indigo 200
  },
  // Compatibility & Score Highlights
  score: {
    DEFAULT: "#9333ea", // Purple 600
    bg: "#fdf4ff",      // Purple 50
    border: "#f0abfc",  // Purple 300
  },
  // Background Surfaces
  bg: {
    page: "#f8fafc",     // Slate 50
    surface: "#ffffff",  // White
    subtle: "#f1f5f9",   // Slate 100
    muted: "#e2e8f0",    // Slate 200
    inverse: "#0f172a",  // Slate 900
  },
  // Typography Colors
  text: {
    main: "#0f172a",     // Slate 900
    muted: "#64748b",    // Slate 500
    subtle: "#94a3b8",   // Slate 400
    inverse: "#ffffff",  // White
    accent: "#6366f1",   // Indigo 500
  },
  // Astrological Element Palette
  element: {
    fire: "#ea580c",     // Orange 600
    earth: "#16a34a",    // Green 600
    air: "#0284c7",      // Sky 600
    water: "#0891b2",    // Cyan 600
  },
  // Semantic State
  state: {
    success: "#16a34a",
    warning: "#d97706",
    error: "#dc2626",
    info: "#2563eb",
  },
};
```

### 6.2 Typography Tokens (`tokens/typography.ts`)
```typescript
export const typography = {
  fonts: {
    sans: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    mono: "'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace",
    georgian: "'Sylfaen', 'Noto Sans Georgian', sans-serif",
  },
  sizes: {
    xs: { fontSize: 12, lineHeight: 16 },
    sm: { fontSize: 14, lineHeight: 20 },
    base: { fontSize: 16, lineHeight: 24 },
    lg: { fontSize: 18, lineHeight: 28 },
    xl: { fontSize: 20, lineHeight: 28 },
    "2xl": { fontSize: 24, lineHeight: 32 },
    "3xl": { fontSize: 30, lineHeight: 36 },
  },
  weights: {
    normal: "400",
    medium: "500",
    semibold: "600",
    bold: "700",
    heavy: "800",
  },
};
```

### 6.3 Spacing, Radii, and Elevation Tokens
- **Spacing Grid**: 4px baseline (`0: 0, 1: 4px, 2: 8px, 3: 12px, 4: 16px, 5: 20px, 6: 24px, 8: 32px, 10: 40px, 12: 48px, 16: 64px`).
- **Radii**: `sm: 6px, md: 10px, lg: 16px, xl: 24px, full: 9999px`.
- **Elevation / Shadows**:
  - `none`: 0
  - `sm`: `{ shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.05, shadowRadius: 2, elevation: 1 }`
  - `md`: `{ shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.08, shadowRadius: 8, elevation: 3 }`
  - `lg`: `{ shadowColor: '#000', shadowOffset: { width: 0, height: 10 }, shadowOpacity: 0.12, shadowRadius: 16, elevation: 6 }`

---

## 7. NativeWind / Styling Architecture `[RECOMMENDED]`

### 7.1 Styling Engine Specification
JESTER adopts **NativeWind v4** for universal component styling:
1. **Utility-First**: Styles are applied via Tailwind classes compiled at build time into native `StyleSheet` objects on iOS/Android, and into CSS class rules on Web.
2. **Deterministic Pre-compilation**: Zero runtime CSS-in-JS overhead; full support for the new React Native Architecture (Hermes & Fabric).
3. **Responsive Variants**: Full support for Tailwind breakpoints (`sm:`, `md:`, `lg:`) mapping seamlessly across mobile screens and desktop browser viewports.

### 7.2 Boundaries: What NOT to Express with Utility Classes
- **Complex Gesture Physics**: Handled via `react-native-reanimated` worklets and `react-native-gesture-handler`.
- **Astronomical Aspect Visualizations**: Rendered via pure declarative SVG primitives (`react-native-svg`), not HTML/CSS tricks.
- **Dynamic Computed Scores**: Gauge arc geometry and fill calculations are passed as explicit numeric props to SVG wrappers.

---

## 8. Component Architecture

### 8.1 UI Primitives (Universal Presentation Building Blocks)
All primitives live in `ui/primitives/` and expose cross-platform interfaces:

| Primitive | Universal Props | Responsibility |
| :--- | :--- | :--- |
| **`Box`** | `className, style, children` | Universal layout container mapping to `View` (Native) / `div` (Web). |
| **`Text`** | `variant, weight, color, children` | Enforces typography scale and system font fallbacks. |
| **`Button`** | `variant, size, isLoading, icon, onPress` | Accessible touchable button with 44px+ minimum touch target and tactile haptic trigger. |
| **`Card`** | `variant, elevation, className, children` | Contained surface with border and subtle elevation. |
| **`Input`** | `label, error, value, onChangeText, ...` | Cross-platform text entry with focus ring and error label. |
| **`Badge`** | `variant, size, children` | Compact tag for astrological elements, signs, or status flags. |
| **`Avatar`** | `src, fallback, size, isOnline` | User profile avatar with initials fallback. |
| **`Skeleton`**| `width, height, radius` | Shimmer loading placeholder for data fetching states. |
| **`Modal`** | `isOpen, onClose, title, children` | Responsive dialog: bottom-sheet on mobile, centered modal on desktop. |

### 8.2 JESTER Product Components
Located in `ui/components/`:
- **`InsightCard`**: Renders a single JESTER interpretation unit (`title, text, tone_tag, depth, signal_label`).
- **`PersonCard`**: Discovery feed card displaying avatar, display name, sun/moon/rising badges, and connection CTA.
- **`ScoreGauge`**: Circular / arc score visualizer rendering normalized score ($10–98$), confidence, and tier label.
- **`RelationshipSignal`**: Top synastry dynamic with icon, category, and tension/harmony indicator.
- **`TopicChip`**: Interactive pill displaying a discussion topic with mutual interest relevance.
- **`ConversationStarter`**: Shareable opening line with one-tap "Send to Chat" handoff.
- **`ConnectionAction`**: State-machine driven button group (Connect, Pending, Accept/Decline, Compare/Chat).
- **`ChatBubble`**: Direct message bubble with status indicators and starter injection callout.

---

## 9. Feature Module Architecture

Code is strictly organized by business capability inside `src/features/`:

```
src/
├── features/
│   ├── auth/              # Login, Register, Password Reset
│   │   ├── components/    # LoginForm, RegisterForm
│   │   ├── hooks/         # useAuthSession, useAuthActions
│   │   └── types.ts
│   ├── onboarding/        # Birth data wizard
│   │   ├── components/    # BirthDateStep, PrecisionToggle, CitySearchStep
│   │   └── hooks/         # useBirthDataForm, useGeocoding
│   ├── self/              # ME — Personal astrology & dossier
│   │   ├── components/    # PlacementCard, InsightSection, DossierViewer
│   │   └── hooks/         # useMySafeAstro, useNatalObservations
│   ├── discover/          # Discover people & feed
│   │   ├── components/    # DiscoveryCard, FeedList, FilterSheet
│   │   └── hooks/         # useDiscoverFeed, useDiscoveryActions
│   ├── people/            # Public profiles
│   │   ├── components/    # PublicProfileHeader, SafeSignsGrid
│   │   └── hooks/         # usePersonProfile
│   ├── connections/       # Social graph
│   │   ├── components/    # ConnectionList, PendingRequests, ConnectionActionButtons
│   │   └── hooks/         # useConnections, useConnectionTransition
│   ├── compatibility/     # US — Compare & Why
│   │   ├── components/    # ScoreGauge, DimensionsGrid, DynamicsList, StartersSection
│   │   └── hooks/         # useCompatibility, useWhyPerson
│   ├── chat/              # Direct messaging
│   │   ├── components/    # MessageThread, ChatInputBar, StarterInsertionSheet
│   │   └── hooks/         # useChatThread, useSendMessage, useChatRealtime
│   └── notifications/     # In-app alerts
│       ├── components/    # NotificationList, NotificationItem, UnreadBadge
│       └── hooks/         # useNotifications, useNotificationRealtime
```

---

## 10. Platform Abstraction Architecture `[RECOMMENDED]`

Hardware, device, and OS capabilities are abstracted into universal interfaces (`platform/`) to isolate platform discrepancies:

```
src/platform/
├── storage.ts         # Secure persistent key-value storage
├── notifications.ts   # Push token registration & local notification handling
├── haptics.ts         # Tactile vibration feedback
├── share.ts           # Native OS share sheet vs Web Share API
├── clipboard.ts       # Copy-to-clipboard functionality
├── linking.ts         # Deep link resolution & external browser opening
└── keyboard.ts        # Soft-keyboard spacing & avoidance
```

### 10.1 Storage Facade Contract
- **Native (iOS/Android)**: Backed by `expo-secure-store` with hardware encryption (iOS Keychain / Android Keystore).
- **Web**: Backed by secure, partition-isolated browser storage (`localStorage` with fallback to in-memory).

### 10.2 Haptics Facade Contract
- **Native**: Calls `expo-haptics` (`impactAsync(ImpactFeedbackStyle.Light)`, `notificationAsync(NotificationFeedbackType.Success)`).
- **Web**: Calls `navigator.vibrate` if supported, otherwise performs a clean no-op.

---

## 11. State & Data Flow Architecture

### 11.1 Canonical Data Flow `[FROZEN]`
```
UI Component (Tap Action)
       │
       ▼
Feature Custom Hook
       │
       ▼
TanStack Query / Mutation (`useQuery` / `useMutation`)
       │
       ▼
API Service Client (`services/api/`)
       │
       ▼ [Bearer JWT via Supabase Session]
FastAPI Endpoint (`https://api.jester.app/v1/...`)
       │
       ▼ [Structured JSON Response]
Query Cache Invalidation / Optimistic Update
       │
       ▼
UI Component Re-renders Deterministically
```

### 11.2 Invalidation & Caching Strategy `[FROZEN]`

| Cache Key | Data Entity | Stale Time | Invalidation Triggers |
| :--- | :--- | :--- | :--- |
| `["profile", "me"]` | Current User Profile | 10 mins | Profile update mutation |
| `["astrology", "me"]` | Safe Natal Astrology | 60 mins | Recalculate mutation / Birth data update |
| `["astrology", targetId]` | Target Safe Astrology | 30 mins | Target profile refresh |
| `["connections"]` | Social Connections Graph | 30 secs | Any `/transition` mutation or Realtime event |
| `["compatibility", targetId]`| Synastry Comparison | 120 mins | Invalidate if either birth data version bumps |
| `["messages", convId]` | Chat Message History | Instant | Realtime `INSERT` event or send mutation |
| `["notifications"]` | User Alerts Feed | 15 secs | Mark read mutation or Realtime event |

---

## 12. Supabase & Realtime Architecture `[FROZEN]`

1. **Authentication Interceptor**:
   - Every outbound API request retrieves the active JWT via `supabase.auth.getSession()`.
   - On HTTP 401: Clears tokens, terminates query caches, and redirects to `/auth/login`.
2. **Channel Lifecycle Management**:
   - `public:notifications:user_id=eq.{id}`: Opened once upon authenticated shell entry; stays open until sign out.
   - `public:messages:conversation_id=eq.{id}`: Opened when navigating into `/chat/:id`; immediately unsubscribed on unmount.
3. **Deduplication & Optimistic Messages**:
   - Optimistic outgoing messages are assigned a client UUID `client_id`.
   - When the backend broadcast arrives, the client replaces the optimistic entry without visual flicker or double-bubble duplication.

---

## 13. Responsive & Adaptive Architecture `[RECOMMENDED]`

Responsive layouts adapt presentation while keeping business logic and state 100% identical:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        VIEWPORT ADAPTATION                             │
├───────────────────┬────────────────────────────┬───────────────────────┤
│ MOBILE (< 768px)  │ TABLET (768px - 1023px)    │ DESKTOP (≥ 1024px)    │
├───────────────────┼────────────────────────────┼───────────────────────┤
│ • Bottom Tab Bar  │ • Collapsible Rail Nav     │ • Persistent Top Nav  │
│ • Stacked Screens │ • Master-Detail Panels     │ • Multi-Column Canvas │
│ • Bottom Sheets   │ • Split Chat Thread        │ • Modal Side-Drawers  │
│ • 100% Full Width │ • Max-width 720px Content  │ • Max-width 1024px    │
└───────────────────┴────────────────────────────┴───────────────────────┘
```

---

## 14. Accessibility Architecture `[RECOMMENDED]`

1. **Minimum Touch Targets**: 44×44px on mobile touchscreens; 36×36px with keyboard focus rings on web.
2. **Dynamic Text Scaling**: All typography scales with iOS Dynamic Type and Android font scale settings.
3. **Screen Reader Semantics**:
   - Every interactive primitive specifies `accessibilityRole` (`button`, `link`, `header`, `alert`).
   - Astrological glyphs and badges include descriptive `accessibilityLabel` (e.g., `accessibilityLabel="მზე ვერძში / Sun in Aries"`).
4. **Contrast Compliance**: Text contrast meets WCAG AA standards (minimum 4.5:1 for normal text, 3:1 for large display headers).
5. **Reduced Motion**: All animations respect `prefers-reduced-motion` / system accessibility motion preferences.

---

## 15. Performance Architecture `[RECOMMENDED]`

1. **List Recycling**: Use `@shopify/flash-list` for the Discover feed, Connections list, and Chat message threads to eliminate memory leaks and frame drops.
2. **Asset Optimization**: Local image assets are served in WebP format with `expo-image` aggressive memory and disk caching.
3. **Memoized Computations**: Heavy view formatting and complex astrological badge layouts are guarded with `React.memo` and `useMemo`.
4. **Fast Initial Load**: Code-splitting per route on Web; lazy loading for non-critical bottom sheets and settings screens.

---

## 16. Testing Architecture `[RECOMMENDED]`

```
┌────────────────────────────────────────────────────────────────────────┐
│                        TESTING PYRAMID LAYERS                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. UNIT TESTS (Vitest / Jest)                                          │
│    • Domain formatters, date/timezone parsers, DTO normalizers         │
├────────────────────────────────────────────────────────────────────────┤
│ 2. COMPONENT TESTS (React Native Testing Library + Jest Native)        │
│    • Primitives (Button, Input, Card, Badge)                          │
│    • JESTER UI components (ScoreGauge, InsightCard, ConnectionAction) │
├────────────────────────────────────────────────────────────────────────┤
│ 3. INTEGRATION TESTS (Mock Service Worker / MSW)                       │
│    • Query hooks, mutation transitions, auth state changes            │
├────────────────────────────────────────────────────────────────────────┤
│ 4. E2E TESTS (Playwright for Web / Maestro for Mobile)                 │
│    • Registration -> Birth Data -> ME Dossier                         │
│    • Discover -> Connect -> Accept -> Compare -> Why -> Chat           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 17. Security & Privacy Invariants `[FROZEN]`

- **Zero Astronomical Leaks**: Under no circumstances will raw degrees, exact house cusps, or `evidence_trace` data be rendered or logged in the client.
- **Safe DTO Binding**: The client binds strictly to `SafeDerivedAstrologyResponse`, `ProfileResponse`, and `CompatibilityResponse`.
- **Existence Oracle Prevention**: Navigating to private, deleted, or blocked profiles renders a uniform `404 Not Found` view.

---

## 18. Content Rendering Architecture `[FROZEN]`

The frontend renders content generated by the deterministic JESTER Content Engine:
1. **Insight Units**: Renders Micro (100–250 chars) and Medium (400–750 chars) assets without altering semantic meaning.
2. **Tone Presentation**: Displays tone tags (`Cocky`, `Snarky`, `Dramatic`, `Conversational`, `Unfiltered`, `Mocking`, `Playful`, `Unexpected`) as subtle personality indicators.
3. **Structured Synthesis**: As the backend introduces multi-placement synthesis (Sun×Moon, Cognitive Drive), the UI renders composite insight cards rather than hardcoded individual paragraphs.

---

## 19. Current Implementation Gap Report

| Architecture Area | Current State (Vite Web Scaffold) | Target Architecture (Universal Expo) | Gap Severity | Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **Framework** | Vite 8.2 + React 19 DOM | Expo SDK 52+ / React Native 0.76+ | High | Transition to Expo Universal project |
| **Platform Scope** | Web Only (Desktop & Mobile Browser) | iOS, Android, Desktop Web, Mobile Web | High | Universal primitives & bundling |
| **Navigation** | `react-router-dom` v7 | `expo-router` v4 (Universal file routing) | Medium | Map route definitions to app folder |
| **Styling** | Vanilla CSS (1,273 lines `index.css`) | NativeWind v4 (Tailwind tokens) | Medium | Migrate CSS variables to design tokens |
| **UI Primitives** | Custom DOM elements (`div`, `button`) | Universal RN primitives (`View`, `Pressable`)| Medium | Re-implement primitives with RN/NW |
| **State Layer** | TanStack Query v5 + React Context | TanStack Query v5 + React Context | **ZERO (MATCH)**| 100% reusable directly |
| **API Client** | Fetch + Bearer JWT (`client.ts`) | Fetch / Axios + Bearer JWT | **ZERO (MATCH)**| 100% reusable directly |
| **Auth Flow** | Supabase JS client v2 | Supabase JS client + SecureStore | Low | Add `expo-secure-store` adapter |
| **Realtime** | Supabase WSS notifications | Supabase WSS notifications + Chat | Low | Add background channel handlers |
| **Hardware APIs** | Browser `alert()`, `confirm()` | Platform facades (`haptics`, `share`) | Medium | Replace browser alerts with UI sheets |

---

## 20. Platform Decision Matrix

| Evaluation Dimension | Option A: Keep Vite Web Only | Option B: Universal Expo (RN + RNW) | Option C: Monorepo (Vite Web + Expo Native) |
| :--- | :---: | :---: | :---: |
| **iOS / Android Readiness** | 1 / 5 (Must rewrite from scratch) | **5 / 5 (First-class native)** | 5 / 5 (First-class native) |
| **Desktop Web Readiness** | 5 / 5 (Native DOM) | **4 / 5 (High with RNW)** | 5 / 5 (Native DOM) |
| **Code Reuse** | 0% for mobile | **85–95% UI, 100% logic** | 40% (Logic only, UI duplicated) |
| **Developer Velocity** | Fast for web, zero for mobile | **Very High (One unified stack)**| Slow (Dual component trees) |
| **Design Consistency** | Diverges when mobile starts | **Single source of design truth**| High divergence risk |
| **Haptics / Push / Deep Links**| Zero native support | **Full native support via Expo** | Full native support |
| **Maintenance Burden** | Moderate now, double later | **Low (Single universal codebase)**| High (Two apps to maintain) |
| **Long-Term Architectural Health**| Poor (Tech debt accumulation) | **Excellent (Future-proof)** | Good but resource-heavy |
| **TOTAL SCORE (out of 40)** | 18 / 40 | **36 / 40 (WINNER)** | 29 / 40 |

**Architectural Recommendation:** **Option B: Universal Expo (React Native + React Native Web with NativeWind v4)** is the definitive architecture for JESTER v1.1.

---

## 21. Phased Migration Plan

To ensure continuous development stability without breaking current verification workflows:

### Phase A: Universal Foundation & Design Tokens `[NEXT IMPLEMENTATION PHASE]`
- Initialize the target Expo Universal structure alongside existing code.
- Extract all design tokens from `frontend/src/index.css` into typed TypeScript constants in `ui/tokens/`.
- Configure `tailwind.config.js` and NativeWind v4.

### Phase B: UI Primitives & Platform Facades
- Implement universal primitives (`Box`, `Text`, `Button`, `Card`, `Badge`, `Input`, `Avatar`, `Skeleton`).
- Implement platform abstraction facades (`platform/storage.ts`, `platform/haptics.ts`, `platform/share.ts`).

### Phase C: State & API Client Shared Core
- Migrate `core/api/`, `core/auth/`, and `core/realtime/` directly into universal `services/` and `features/auth/`.
- Wire `expo-secure-store` to Supabase client storage adapter.

### Phase D: Feature Screen Migration (ME & Onboarding)
- Port Birth Data Onboarding wizard using universal primitives.
- Port ME screen (Placements, Insight Cards, Dossier viewer).

### Phase E: Feature Screen Migration (YOU, WHY, US)
- Port Discover feed with FlashList virtualization.
- Port Person Profile and Why Person deep-dive views.
- Port Compare screen (ScoreGauge, Dimensions, Signals).

### Phase F: Feature Screen Migration (Connect, Chat, Notifications)
- Port Connections management screen.
- Port Realtime Chat screen with starter insertion sheet.
- Port Notifications center.

### Phase G: Universal Navigation & Route Freeze
- Mount Expo Router universal file-tree.
- Verify identical responsive layout execution on Desktop Web, iOS Simulator, and Android Emulator.

### Phase H: Native Build Packaging & Store Readiness
- Configure `app.json` / `app.config.ts` for iOS & Android bundle IDs, splash screens, and icons.
- Configure Expo EAS Build pipelines.
- Decommission legacy Vite single-platform scaffold.

---

## 22. Implementation Readiness & Decision Summary

### Status Legend:
- `[FROZEN]`: Canonical product or technical invariant. Cannot be changed without Architecture Board approval.
- `[RECOMMENDED]`: Approved target architectural path.
- `[PENDING PRODUCT / UX DECISION]`: Requires user/product owner confirmation before coding.
- `[NOT YET IMPLEMENTED]`: Documented target state awaiting scheduled migration phase.

---

```
════════════════════════════════════════════════════════════════
             JESTER FRONTEND ARCHITECTURE DECISION
════════════════════════════════════════════════════════════════
Framework:       Universal Expo (SDK 52+) / React Native (0.76+)
Runtime:         Hermes Engine (iOS & Android) + React Native Web
Web:             Universal React Native Web (RNW)
Mobile:          iOS Native & Android Native (Single Codebase)
Navigation:      Expo Router v4 (Universal File-Based Routing)
Styling:         NativeWind v4 (Tailwind Utility Engine)
Design System:   Structured Design Tokens (TS) -> UI Primitives
Server State:    TanStack Query v5 (Shared Cache & Keys)
API Client:      Typed Fetch / Axios + Bearer JWT + FastAPI
Auth & Realtime: Supabase JS Client v2 + SecureStore
Hardware APIs:   Universal Facades (platform/*)
Animation:       React Native Reanimated v3 + Gesture Handler v2
Testing:         Vitest (Unit) + RNTL (Components) + Playwright/Maestro (E2E)

Primary Architectural Choice:
UNIVERSAL EXPO (REACT NATIVE + REACT NATIVE WEB + NATIVEWIND)

Migration Required:
YES (Phased migration from current Vite scaffold to Universal Expo)

Immediate Next Implementation Phase:
PHASE 4.1 — UNIVERSAL FOUNDATION, DESIGN TOKENS & UI PRIMITIVES
════════════════════════════════════════════════════════════════
```
