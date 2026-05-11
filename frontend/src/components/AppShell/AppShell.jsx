import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import styles from './AppShell.module.css';
import { useAuth } from '../../auth/AuthContext.jsx';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
  { to: '/send', label: 'Payments', icon: 'payments' },
  { to: '/history', label: 'History', icon: 'history' },
];

export default function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const initials = (user?.full_name || user?.email || 'U')
    .split(/[\s@]/)
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0].toUpperCase())
    .join('');

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className={styles.shell}>
      <nav className={styles.sidebar}>
        <div>
          <div className={styles.brand}>
            <span className={`material-symbols-outlined filled ${styles.brandIcon}`}>
              security
            </span>
            <span className={styles.brandName}>SafeFlow AI</span>
          </div>

          <div className={styles.profile}>
            <div className={styles.avatar}>{initials}</div>
            <div>
              <div className={styles.profileName}>
                {user?.full_name || 'Account holder'}
              </div>
              <div className={styles.profileMeta}>{user?.email}</div>
            </div>
          </div>

          <div className={styles.secureBadge}>
            <span className="material-symbols-outlined">shield</span>
            Secure Mode On
          </div>
        </div>

        <div className={styles.navList}>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `${styles.navLink} ${isActive ? styles.navLinkActive : ''}`
              }
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        <div className={styles.navFooter}>
          <button className={styles.navLink} onClick={handleLogout} type="button">
            <span className="material-symbols-outlined">logout</span>
            <span>Logout</span>
          </button>
        </div>
      </nav>

      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}
