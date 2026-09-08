import React, { useState } from "react";
import { View, ScrollView } from "react-native";
import {
  Box,
  Text,
  Button,
  IconButton,
  Card,
  Input,
  Avatar,
  Badge,
  Divider,
  Skeleton,
} from "./primitives";
import { colors, spacing } from "./tokens";
import { haptics, clipboard, storage } from "../platform";

export const VisualLab: React.FC = () => {
  const [inputValue, setInputValue] = useState("");
  const [buttonLoading, setButtonLoading] = useState(false);
  const [storageStatus, setStorageStatus] = useState("Untested");
  const [copyStatus, setCopyStatus] = useState("Click to copy token");

  const handleTestStorage = async () => {
    await storage.setItem("jester_lab_test", "verified_token_ok");
    const val = await storage.getItem("jester_lab_test");
    setStorageStatus(val ? "Verified (Storage OK)" : "Failed");
    haptics.success();
  };

  const handleCopy = async () => {
    await clipboard.setString("JESTER-UNIVERSAL-TOKEN-2026");
    setCopyStatus("Copied to clipboard!");
    haptics.light();
    setTimeout(() => setCopyStatus("Click to copy token"), 2500);
  };

  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: colors.background }}
      contentContainerStyle={{ padding: 24, maxWidth: 900, alignSelf: "center", width: "100%" }}
    >
      {/* Header Banner */}
      <Box surface="subtle" rounded="lg" padding={20} style={{ marginBottom: 24, borderWidth: 1, borderColor: colors.border }}>
        <Badge variant="highlight" size="sm" style={{ marginBottom: 8 }}>
          PHASE 4.1 FOUNDATION
        </Badge>
        <Text variant="2xl" weight="heavy" color="primary">
          JESTER Universal Design System Lab
        </Text>
        <Text variant="sm" color="secondary" style={{ marginTop: 4 }}>
          Route: <Text variant="sm" weight="semibold" color="accent">/visual-lab</Text> • Runtime: React Native Web / Universal Primitives • Zero DOM dependencies in primitives
        </Text>
      </Box>

      {/* 1. Typography Hierarchy */}
      <Card elevation="sm" style={{ marginBottom: 24 }}>
        <Text variant="lg" weight="bold" color="primary" style={{ marginBottom: 16 }}>
          1. Typography Matrix & Hierarchy
        </Text>
        <Text variant="3xl" weight="heavy" color="primary" style={{ marginBottom: 6 }}>
          Display 3xl Heavy (30px)
        </Text>
        <Text variant="2xl" weight="bold" color="primary" style={{ marginBottom: 6 }}>
          Heading 2xl Bold (24px)
        </Text>
        <Text variant="xl" weight="semibold" color="accent" style={{ marginBottom: 6 }}>
          Title xl Semibold (20px) — Accent Color
        </Text>
        <Text variant="lg" weight="medium" color="secondary" style={{ marginBottom: 6 }}>
          Subheading lg Medium (18px) — Secondary Slate
        </Text>
        <Text variant="base" weight="normal" color="primary" style={{ marginBottom: 6 }}>
          Body Base Normal (16px) — JESTER deterministic relationship intelligence and sharp psychological clarity.
        </Text>
        <Text variant="sm" weight="normal" color="muted" style={{ marginBottom: 6 }}>
          Caption sm Normal (14px) — Muted metadata label
        </Text>
        <Text variant="xs" weight="semibold" color="highlight">
          MICRO xs SEMIBOLD (12px) — HIGH-PRIORITY INSIGHT TAG
        </Text>
      </Card>

      {/* 2. Universal Button States & Touch Targets */}
      <Card elevation="sm" style={{ marginBottom: 24 }}>
        <Text variant="lg" weight="bold" color="primary" style={{ marginBottom: 16 }}>
          2. Button States (44px+ Accessible Touch Targets)
        </Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12, marginBottom: 16 }}>
          <Button
            variant="primary"
            onPress={() => {
              haptics.light();
            }}
          >
            Primary Action
          </Button>

          <Button
            variant="highlight"
            onPress={() => {
              haptics.success();
            }}
          >
            Highlight Action
          </Button>

          <Button
            variant="secondary"
            onPress={() => {
              haptics.light();
            }}
          >
            Secondary
          </Button>

          <Button
            variant="outline"
            onPress={() => {
              haptics.light();
            }}
          >
            Outline
          </Button>

          <Button
            variant="danger"
            onPress={() => {
              haptics.error();
            }}
          >
            Danger
          </Button>

          <Button
            variant="primary"
            isLoading={buttonLoading}
            onPress={() => {
              setButtonLoading(true);
              setTimeout(() => setButtonLoading(false), 2000);
            }}
          >
            {buttonLoading ? "Loading..." : "Simulate Loading"}
          </Button>

          <Button variant="primary" disabled>
            Disabled Button
          </Button>
        </View>

        <Divider spacing={12} />

        <Text variant="sm" weight="semibold" color="secondary" style={{ marginBottom: 8 }}>
          IconButtons (Circular 44px)
        </Text>
        <View style={{ flexDirection: "row", gap: 12 }}>
          <IconButton
            accessibilityLabel="Search"
            icon={<Text color="inverse">🔍</Text>}
            variant="default"
            onPress={() => haptics.light()}
          />
          <IconButton
            accessibilityLabel="Notifications"
            icon={<Text>🔔</Text>}
            variant="subtle"
            onPress={() => haptics.light()}
          />
          <IconButton
            accessibilityLabel="Settings"
            icon={<Text>⚙️</Text>}
            variant="outline"
            onPress={() => haptics.light()}
          />
          <IconButton
            accessibilityLabel="Remove"
            icon={<Text>🗑️</Text>}
            variant="danger"
            onPress={() => haptics.error()}
          />
        </View>
      </Card>

      {/* 3. Surface & Card Elevations */}
      <Card elevation="sm" style={{ marginBottom: 24 }}>
        <Text variant="lg" weight="bold" color="primary" style={{ marginBottom: 16 }}>
          3. Surfaces & Elevation Hierarchy
        </Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 16 }}>
          <Card elevation="none" variant="subtle" style={{ flex: 1, minWidth: 200 }}>
            <Text variant="sm" weight="bold" color="primary">Flat Subtle Surface</Text>
            <Text variant="xs" color="secondary" style={{ marginTop: 4 }}>elevation="none"</Text>
          </Card>

          <Card elevation="sm" variant="surface" style={{ flex: 1, minWidth: 200 }}>
            <Text variant="sm" weight="bold" color="primary">Surface Card (SM)</Text>
            <Text variant="xs" color="secondary" style={{ marginTop: 4 }}>elevation="sm"</Text>
          </Card>

          <Card elevation="md" variant="highlight" style={{ flex: 1, minWidth: 200 }}>
            <Text variant="sm" weight="bold" color="highlight">Highlight Card (MD)</Text>
            <Text variant="xs" color="secondary" style={{ marginTop: 4 }}>elevation="md"</Text>
          </Card>

          <Card elevation="lg" variant="bordered" style={{ flex: 1, minWidth: 200 }}>
            <Text variant="sm" weight="bold" color="primary">Bordered Card (LG)</Text>
            <Text variant="xs" color="secondary" style={{ marginTop: 4 }}>elevation="lg"</Text>
          </Card>
        </View>
      </Card>

      {/* 4. Form Controls & Input */}
      <Card elevation="sm" style={{ marginBottom: 24 }}>
        <Text variant="lg" weight="bold" color="primary" style={{ marginBottom: 16 }}>
          4. Cross-Platform Input Controls
        </Text>
        <Input
          label="Display Name / სახელი"
          placeholder="e.g. ელენე"
          value={inputValue}
          onChangeText={setInputValue}
          helperText="Universal TextInput component with focus handling."
        />
        <Input
          label="Error State Demonstration"
          placeholder="Invalid input"
          value="invalid_coordinates"
          error="სისტემური შეცდომა: მონაცემები არავალიდურია"
        />
      </Card>

      {/* 5. Astrological Badges & Chips */}
      <Card elevation="sm" style={{ marginBottom: 24 }}>
        <Text variant="lg" weight="bold" color="primary" style={{ marginBottom: 16 }}>
          5. Badges & Astrological Category Chips
        </Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 12 }}>
          <Badge variant="brand">♈ მზე ვერძში / Sun Aries</Badge>
          <Badge variant="highlight">♏ მთვარე მორიელში / Moon Scorpio</Badge>
          <Badge variant="neutral">♌ ასცედენტი ლომში / Rising Leo</Badge>
          <Badge variant="success">🔥 ცეცხლი / Fire Dominant</Badge>
          <Badge variant="warning">⚡ კარდინალური / Cardinal</Badge>
          <Badge variant="danger">⚔️ მარსი თევზებში / Mars Pisces</Badge>
        </View>
      </Card>

      {/* 6. Avatars & Status Badges */}
      <Card elevation="sm" style={{ marginBottom: 24 }}>
        <Text variant="lg" weight="bold" color="primary" style={{ marginBottom: 16 }}>
          6. Avatars with Online Status Indicators
        </Text>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 16 }}>
          <Avatar size="sm" name="A B" isOnline={true} />
          <Avatar size="md" name="Davit Beridze" isOnline={false} />
          <Avatar size="lg" name="Nino K" isOnline={true} />
          <Avatar size="xl" name="Jester King" isOnline={true} />
        </View>
      </Card>

      {/* 7. Skeleton Shimmer Loading States */}
      <Card elevation="sm" style={{ marginBottom: 24 }}>
        <Text variant="lg" weight="bold" color="primary" style={{ marginBottom: 16 }}>
          7. Shimmer Skeleton Loading States
        </Text>
        <View style={{ gap: 10 }}>
          <Skeleton width="40%" height={24} rounded="sm" />
          <Skeleton width="100%" height={16} rounded="sm" />
          <Skeleton width="90%" height={16} rounded="sm" />
          <Skeleton width="75%" height={16} rounded="sm" />
        </View>
      </Card>

      {/* 8. Spacing Grid Reference */}
      <Card elevation="sm" style={{ marginBottom: 24 }}>
        <Text variant="lg" weight="bold" color="primary" style={{ marginBottom: 16 }}>
          8. 4px / 8px Baseline Spacing Scale
        </Text>
        <View style={{ gap: 8 }}>
          {[1, 2, 3, 4, 6, 8, 12].map((step) => {
            const px = spacing[step as keyof typeof spacing];
            return (
              <View key={step} style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
                <Text variant="xs" weight="semibold" color="secondary" style={{ width: 80 }}>
                  Step {step} ({px}px):
                </Text>
                <View
                  style={{
                    height: 14,
                    width: px * 4,
                    backgroundColor: colors.accent,
                    borderRadius: 2,
                  }}
                />
              </View>
            );
          })}
        </View>
      </Card>

      {/* 9. Universal Platform Facades Test */}
      <Card elevation="sm" style={{ marginBottom: 24 }}>
        <Text variant="lg" weight="bold" color="primary" style={{ marginBottom: 16 }}>
          9. Platform Abstraction Facades (Web / Native Universal)
        </Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12 }}>
          <Button variant="secondary" size="sm" onPress={handleTestStorage}>
            Test Storage: {storageStatus}
          </Button>

          <Button variant="outline" size="sm" onPress={handleCopy}>
            {copyStatus}
          </Button>

          <Button
            variant="highlight"
            size="sm"
            onPress={() => {
              haptics.success();
            }}
          >
            Trigger Haptic Pulse
          </Button>
        </View>
      </Card>

      {/* 10. NativeWind Integration & Class Path Verification */}
      <Card elevation="sm" style={{ marginBottom: 24 }}>
        <Text variant="lg" weight="bold" color="primary" style={{ marginBottom: 8 }}>
          10. NativeWind Integration & Class Path Verification
        </Text>
        <Text variant="sm" color="secondary" style={{ marginBottom: 16 }}>
          Exercises NativeWind utility class resolution mapped directly to JESTER design tokens.
        </Text>
        <View className="bg-accent-subtle p-4 rounded-lg border border-accent-border mb-3">
          <Text className="text-accent font-bold text-base">
            NativeWind Class Path: bg-accent-subtle + text-accent
          </Text>
          <Text className="text-textSecondary text-sm mt-1">
            Compiled through Tailwind token mapping: #6366f1 accent on #eef2ff surface.
          </Text>
        </View>
        <View className="bg-highlight-subtle p-4 rounded-lg border border-highlight-border">
          <Text className="text-highlight font-bold text-base">
            NativeWind Class Path: bg-highlight-subtle + text-highlight
          </Text>
          <Text className="text-textSecondary text-sm mt-1">
            Compiled through Tailwind token mapping: #9333ea highlight on #fdf4ff surface.
          </Text>
        </View>
      </Card>
    </ScrollView>
  );
};
