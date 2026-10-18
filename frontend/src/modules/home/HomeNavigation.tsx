import { useState, useRef, useEffect } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { JesterLogo } from '../../shared/ui/JesterLogo';
import { HomeIcon, HomeAvatar } from './HomeElements';
import './home.css';

const navigation = [
  { to: '/', label: 'მთავარი', icon: 'home' },
  { to: '/discover', label: 'აღმოაჩინე', icon: 'compass' },
  { to: '/connections', label: 'კავშირები', icon: 'people' },
  { to: '/messages', label: 'საუბრები', icon: 'message' },
  { to: '/me', label: 'პროფილი', icon: 'person' },
] as const;

interface HomeNavigationProps {
  unreadCount?: number;
  signOut: () => Promise<void>;
  profileName?: string | null;
  avatarUrl?: string | null;
  userEmail?: string | null;
}

export function HomeNavigation({
  unreadCount = 0,
  signOut,
  profileName,
  avatarUrl,
  userEmail,
}: HomeNavigationProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [leaving, setLeaving] = useState(false);
  const [failed, setFailed] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuOpen]);

  const displayName = profileName || 'მომხმარებელი';

  return (
    <header className="home-navigation">
      <div className="home-navigation-inner">
        <Link to="/" className="home-brand-link" aria-label="JESTER — მთავარი">
          <JesterLogo variant="horizontal" height={26} />
        </Link>

        <nav className="home-desktop-links" aria-label="მთავარი ნავიგაცია">
          {navigation.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => `home-nav-link${isActive ? ' active' : ''}`}
            >
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="home-utilities" ref={menuRef}>
          <Link
            to="/notifications"
            className="home-icon-button"
            aria-label={unreadCount > 0 ? `შეტყობინებები: ${unreadCount} წაუკითხავი` : 'შეტყობინებები'}
            title="შეტყობინებები"
          >
            <HomeIcon kind="bell" />
            {unreadCount > 0 && (
              <span className="home-notification-count" aria-hidden="true">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </Link>

          <div className="home-account-wrapper">
            <button
              type="button"
              className={`home-account-trigger${menuOpen ? ' is-active' : ''}`}
              aria-label="ანგარიშის მენიუ"
              aria-expanded={menuOpen}
              aria-haspopup="true"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              <HomeAvatar name={displayName} src={avatarUrl} />
            </button>

            {menuOpen && (
              <div className="home-account-popover" role="menu">
                <div className="home-account-header">
                  <strong className="home-account-name">{displayName}</strong>
                  {userEmail && <span className="home-account-email">{userEmail}</span>}
                </div>

                <div className="home-account-links">
                  <Link
                    to="/me"
                    role="menuitem"
                    onClick={() => setMenuOpen(false)}
                  >
                    <HomeIcon kind="person" />
                    <span>ჩემი პროფილი</span>
                  </Link>
                  <Link
                    to="/connections"
                    role="menuitem"
                    onClick={() => setMenuOpen(false)}
                  >
                    <HomeIcon kind="people" />
                    <span>ჩემი კავშირები</span>
                  </Link>
                  <Link
                    to="/notifications"
                    role="menuitem"
                    onClick={() => setMenuOpen(false)}
                  >
                    <HomeIcon kind="bell" />
                    <span>შეტყობინებები</span>
                    {unreadCount > 0 && <span className="home-menu-badge">{unreadCount}</span>}
                  </Link>
                </div>

                {import.meta.env.DEV && (
                  <div className="home-account-dev-section">
                    <span className="home-account-dev-label">დეველოპერი</span>
                    <Link to="/visual-lab" role="menuitem" onClick={() => setMenuOpen(false)}>
                      🎨 Visual Lab
                    </Link>
                    <Link to="/smoke-test" role="menuitem" onClick={() => setMenuOpen(false)}>
                      🧪 Smoke Test
                    </Link>
                    <Link to="/__debug/backend-audit" role="menuitem" onClick={() => setMenuOpen(false)}>
                      🔬 Backend Audit
                    </Link>
                  </div>
                )}

                <div className="home-account-footer">
                  <button
                    type="button"
                    className="home-signout-btn"
                    role="menuitem"
                    disabled={leaving}
                    onClick={async () => {
                      setLeaving(true);
                      setFailed(false);
                      try {
                        await signOut();
                      } catch {
                        setFailed(true);
                        setLeaving(false);
                      }
                    }}
                  >
                    <HomeIcon kind="exit" />
                    <span>{leaving ? 'გასვლა…' : 'ანგარიშიდან გასვლა'}</span>
                  </button>
                  {failed && <p role="alert" className="home-menu-error">გასვლა ვერ მოხერხდა. სცადე ხელახლა.</p>}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

export function HomeMobileNavigation() {
  return (
    <nav className="home-mobile-navigation" aria-label="მთავარი ნავიგაცია">
      {navigation.map(item => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === '/'}
          className={({ isActive }) => `home-mobile-tab${isActive ? ' active' : ''}`}
        >
          <HomeIcon kind={item.icon} />
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
