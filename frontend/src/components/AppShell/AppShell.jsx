import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import styles from './AppShell.module.css';
import { useAuth } from '../../auth/AuthContext.jsx';
import TopAppBar from '../TopAppBar/TopAppBar.jsx';

const PRIMARY_NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
  { to: '/send', label: 'Payments', icon: 'payments' },
  { to: '/history', label: 'History', icon: 'history' },
];

const PAGE_TITLES = {
  '/dashboard': 'Dashboard',
  '/send': 'Send Money',
  '/history': 'History',
};

export default function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();

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

  const title = PAGE_TITLES[pathname] || 'SafeFlow AI';

  return (
    <div className={styles.shell}>
      <nav className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <div className={styles.profile}>
            <div className={styles.avatar}>{initials}</div>
            <div className={styles.profileText}>
              <div className={styles.profileName}>
                {user?.full_name || user?.email || 'Account holder'}
              </div>
              <div className={styles.profileMeta}>Premium Account</div>
            </div>
          </div>

          <button type="button" className={styles.secureBtn}>
            <span className="material-symbols-outlined">shield</span>
            Secure Mode On
          </button>
        </div>

        <div className={styles.navList}>
          {PRIMARY_NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `${styles.navLink} ${isActive ? styles.navLinkActive : ''}`
              }
            >
              <span
                className={`material-symbols-outlined ${styles.navIcon}`}
                aria-hidden
              >
                {item.icon}
              </span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        <div className={styles.navFooter}>
          <button type="button" className={styles.navLink} onClick={handleLogout}>
            <span className="material-symbols-outlined">logout</span>
            <span>Logout</span>
          </button>
        </div>
      </nav>

      <main className={styles.main}>
        <TopAppBar title={title} />
        <div className={styles.content}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
