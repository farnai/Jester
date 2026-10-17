import type { ConnectionResponse, DiscoveryPerson } from '../../core/api/types';

export function connectionFor(connections: ConnectionResponse[], viewer: string, target: string) {
  return connections.find(c => (c.user_a_id === viewer && c.user_b_id === target) || (c.user_b_id === viewer && c.user_a_id === target));
}

export function visibleHomePeople(people: DiscoveryPerson[], connections: ConnectionResponse[], viewer: string) {
  // Preserve the backend's order, never substitute a local compatibility ranking.
  return people.filter(person => person.id !== viewer && connectionFor(connections, viewer, person.id)?.status !== 'blocked');
}

export function personObservation(person: DiscoveryPerson) {
  // The API can resolve an Aries hook without candidate data. That is not a personal insight.
  return ['sun', 'ascendant'].includes(person.presence_sign_source ?? '')
    ? person.hook_observation?.text?.trim() || null : null;
}

export function guidanceItems(value?: string[] | string) {
  return (Array.isArray(value) ? value : value ? [value] : []).map(item => item.trim()).filter(Boolean);
}

const months = ['იანვარი', 'თებერვალი', 'მარტი', 'აპრილი', 'მაისი', 'ივნისი', 'ივლისი', 'აგვისტო', 'სექტემბერი', 'ოქტომბერი', 'ნოემბერი', 'დეკემბერი'];
export function georgianDate(iso?: string) {
  if (!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return '';
  const [, month, day] = iso.split('-').map(Number);
  return months[month - 1] && day >= 1 && day <= 31 ? `${day} ${months[month - 1]}` : '';
}

export function calendarKey(now: Date, timezone?: string) {
  try {
    const parts = new Intl.DateTimeFormat('en-US', { timeZone: timezone || undefined, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(now);
    return ['year', 'month', 'day'].map(type => parts.find(p => p.type === type)?.value).join('-');
  } catch { return now.toISOString().slice(0, 10); }
}
