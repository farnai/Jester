import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { JesterLogo } from '../../shared/ui/JesterLogo';
import { HomeIcon } from './HomeElements';
import './home.css';

const navigation = [
  { to: '/', label: 'მთავარი', icon: 'home' },
  { to: '/discover', label: 'აღმოაჩინე', icon: 'compass' },
  { to: '/messages', label: 'საუბრები', icon: 'message' },
  { to: '/me', label: 'ჩემი პროფილი', icon: 'person' },
] as const;

export function HomeNavigation({ unreadCount, signOut }: { unreadCount: number; signOut: () => Promise<void> }) {
  const [leaving, setLeaving] = useState(false);
  const [failed, setFailed] = useState(false);
  return <header className="home-navigation">
    <div className="home-navigation-inner">
      <Link to="/" aria-label="JESTER — მთავარი"><JesterLogo height={26} /></Link>
      <nav className="home-desktop-links" aria-label="მთავარი ნავიგაცია">{navigation.map(item => <NavLink key={item.to} to={item.to} end={item.to === '/'}>{item.label}</NavLink>)}</nav>
      <div className="home-utilities">
        <Link to="/notifications" className="home-icon-button" aria-label={unreadCount ? `შეტყობინებები: ${unreadCount} წაუკითხავი` : 'შეტყობინებები'}><HomeIcon kind="bell" />{unreadCount > 0 && <span className="home-notification-count">{unreadCount}</span>}</Link>
        <details className="home-account-menu"><summary aria-label="ანგარიშის მენიუ"><HomeIcon kind="person" /></summary><div>
          <Link to="/me">ჩემი პროფილი</Link><Link to="/connections">ჩემი კავშირები</Link>
          <button disabled={leaving} onClick={async () => { setLeaving(true); setFailed(false); try { await signOut(); } catch { setFailed(true); } finally { setLeaving(false); } }}>{leaving ? 'გასვლა…' : 'ანგარიშიდან გასვლა'}</button>
          {failed && <p role="alert">გასვლა ვერ მოხერხდა. სცადე ხელახლა.</p>}
        </div></details>
      </div>
    </div>
  </header>;
}

export function HomeMobileNavigation() {
  return <nav className="home-mobile-navigation" aria-label="მთავარი ნავიგაცია">{navigation.map(item => <NavLink key={item.to} to={item.to} end={item.to === '/'}><HomeIcon kind={item.icon} /><span>{item.label}</span></NavLink>)}</nav>;
}
