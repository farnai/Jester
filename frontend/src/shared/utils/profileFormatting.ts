export const ZODIAC_SYMBOLS_KA: Record<string, { symbol: string; name: string }> = {
  aries: { symbol: '♈', name: 'ვერძი' },
  taurus: { symbol: '♉', name: 'კურო' },
  gemini: { symbol: '♊', name: 'ტყუპები' },
  cancer: { symbol: '♋', name: 'კირჩხიბი' },
  leo: { symbol: '♌', name: 'ლომი' },
  virgo: { symbol: '♍', name: 'ქალწული' },
  libra: { symbol: '♎', name: 'სასწორი' },
  scorpio: { symbol: '♏', name: 'მორიელი' },
  sagittarius: { symbol: '♐', name: 'მშვილდოსანი' },
  capricorn: { symbol: '♑', name: 'თხის რქა' },
  aquarius: { symbol: '♒', name: 'მერწყული' },
  pisces: { symbol: '♓', name: 'თევზები' },
};

export function formatZodiacSign(sign?: string | null): string | null {
  if (!sign) return null;
  const key = sign.trim().toLowerCase();
  const info = ZODIAC_SYMBOLS_KA[key];
  if (info) return `${info.symbol} ${info.name}`;
  return sign;
}

export function formatShortName(fullName?: string | null): string {
  if (!fullName) return 'მომხმარებელი';
  const parts = fullName.trim().split(/\s+/);
  if (parts.length === 1) return parts[0];
  const first = parts[0];
  const last = parts[parts.length - 1];
  if (last.length <= 2 && last.endsWith('.')) {
    return `${first} ${last}`;
  }
  return `${first} ${last.charAt(0).toUpperCase()}.`;
}

