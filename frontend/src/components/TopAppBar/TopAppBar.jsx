import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api/client';
import { useAuth } from '../../auth/AuthContext.jsx';
import { formatCurrency, formatDateTime } from '../../utils/format';
import styles from './TopAppBar.module.css';

const ALERT_STATUSES = new Set(['PENDING', 'WARNED', 'REJECTED']);
const READ_NOTIFICATIONS_KEY = 'safeflow.notifications.read';

export default function TopAppBar({ title }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const menuRef = useRef(null);
  const [openMenu, setOpenMenu] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const notificationReadKey = `${READ_NOTIFICATIONS_KEY}.${
    user?.id || user?.email || 'default'
  }`;
  const [readNotificationIds, setReadNotificationIds] = useState(() =>
    readStoredNotificationIds(notificationReadKey)
  );

  const initials = (user?.full_name || user?.email || 'U')
    .split(/[\s@]/)
    .filter(Boolean)
    .slice(0, 2)
    .map((s) => s[0].toUpperCase())
    .join('');

  const displayName = user?.full_name || 'Account holder';
  const alertNotifications = useMemo(
    () =>
      transactions.filter((tx) => {
        const status = String(tx.status || '').toUpperCase();
        return ALERT_STATUSES.has(status) || tx.requires_password_confirmation;
      }),
    [transactions]
  );
  const notificationItems = useMemo(
    () => alertNotifications.slice(0, 5),
    [alertNotifications]
  );
  const readNotificationIdSet = useMemo(
    () => new Set(readNotificationIds),
    [readNotificationIds]
  );
  const unreadNotificationCount = useMemo(
    () =>
      alertNotifications.filter(
        (tx) => !readNotificationIdSet.has(notificationId(tx))
      ).length,
    [alertNotifications, readNotificationIdSet]
  );

  useEffect(() => {
    setReadNotificationIds(readStoredNotificationIds(notificationReadKey));
  }, [notificationReadKey]);

  useEffect(() => {
    let cancelled = false;
    async function loadNotifications() {
      try {
        const data = await api.myTransactions();
        if (!cancelled) setTransactions(data?.transactions || []);
      } catch {
        if (!cancelled) setTransactions([]);
      }
    }

    loadNotifications();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!openMenu) return undefined;

    const handlePointerDown = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setOpenMenu(null);
      }
    };
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') setOpenMenu(null);
    };

    document.addEventListener('pointerdown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [openMenu]);

  const toggleMenu = (menu) => {
    setOpenMenu((current) => (current === menu ? null : menu));
  };

  const goTo = (path) => {
    setOpenMenu(null);
    navigate(path);
  };

  const clearNotifications = () => {
    const next = Array.from(
      new Set([
        ...readNotificationIds,
        ...alertNotifications.map(notificationId).filter(Boolean),
      ])
    );
    setReadNotificationIds(next);
    localStorage.setItem(notificationReadKey, JSON.stringify(next));
  };

  const handleLogout = async () => {
    setOpenMenu(null);
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <header className={styles.bar}>
      <div className={styles.left}>
        <h1 className={styles.title}>{title}</h1>
      </div>
      <div className={styles.right} ref={menuRef}>
        <button
          type="button"
          className={styles.iconBtn}
          aria-label="Notifications"
          aria-haspopup="menu"
          aria-expanded={openMenu === 'notifications'}
          aria-controls="topbar-notifications"
          onClick={() => toggleMenu('notifications')}
        >
          <span className="material-symbols-outlined">notifications</span>
          {unreadNotificationCount > 0 && (
            <span className={styles.badge}>
              {unreadNotificationCount > 9 ? '9+' : unreadNotificationCount}
            </span>
          )}
        </button>
        <button
          type="button"
          className={styles.iconBtn}
          aria-label="Help"
          aria-haspopup="menu"
          aria-expanded={openMenu === 'help'}
          aria-controls="topbar-help"
          onClick={() => toggleMenu('help')}
        >
          <span className="material-symbols-outlined">help</span>
        </button>
        <button
          type="button"
          className={styles.avatar}
          title={user?.email}
          aria-label="Account menu"
          aria-haspopup="menu"
          aria-expanded={openMenu === 'profile'}
          aria-controls="topbar-profile"
          onClick={() => toggleMenu('profile')}
        >
          {initials}
        </button>

        {openMenu === 'notifications' && (
          <div
            id="topbar-notifications"
            className={styles.menu}
            role="menu"
            aria-label="Notifications"
          >
            <div className={styles.menuHeader}>
              <strong>Notifications</strong>
              <div className={styles.menuHeaderActions}>
                <button
                  type="button"
                  onClick={clearNotifications}
                  disabled={unreadNotificationCount === 0}
                >
                  Clear
                </button>
                <button type="button" onClick={() => goTo('/history')}>
                  View all
                </button>
              </div>
            </div>
            <div className={styles.menuList}>
              {notificationItems.length === 0 ? (
                <div className={styles.emptyState}>
                  <span className="material-symbols-outlined">verified_user</span>
                  <div>
                    <strong>No urgent alerts</strong>
                    <span>Your recent account activity is clear.</span>
                  </div>
                </div>
              ) : (
                notificationItems.map((tx) => {
                  const isRead = readNotificationIdSet.has(notificationId(tx));
                  return (
                    <button
                      type="button"
                      role="menuitem"
                      key={notificationId(tx)}
                      className={`${styles.notificationRow} ${
                        isRead ? styles.notificationRowRead : ''
                      }`}
                      onClick={() => goTo('/history')}
                    >
                      <span className={styles.notificationIcon}>
                        <span className="material-symbols-outlined">
                          {notificationIcon(tx)}
                        </span>
                      </span>
                      <span className={styles.notificationCopy}>
                        <strong>
                          {notificationTitle(tx)}
                          {!isRead && (
                            <span
                              className={styles.unreadDot}
                              aria-label="Unread"
                            />
                          )}
                        </strong>
                        <span>
                          {tx.description || tx.receiver_name || tx.sender_name || 'Transfer'} ·{' '}
                          {formatCurrency(tx.amount, tx.currency)}
                        </span>
                        <small>{formatDateTime(tx.created_at)}</small>
                      </span>
                    </button>
                  );
                })
              )}
            </div>
          </div>
        )}

        {openMenu === 'help' && (
          <div
            id="topbar-help"
            className={styles.menu}
            role="menu"
            aria-label="Help"
          >
            <div className={styles.menuHeader}>
              <strong>Help</strong>
            </div>
            <div className={styles.menuList}>
              <button type="button" role="menuitem" onClick={() => goTo('/send')}>
                <span className="material-symbols-outlined">payments</span>
                New transfer
              </button>
              <button type="button" role="menuitem" onClick={() => goTo('/history')}>
                <span className="material-symbols-outlined">history</span>
                Transaction history
              </button>
              <a
                role="menuitem"
                href="mailto:support@safeflow.ai"
                onClick={() => setOpenMenu(null)}
              >
                <span className="material-symbols-outlined">support_agent</span>
                Contact support
              </a>
            </div>
          </div>
        )}

        {openMenu === 'profile' && (
          <div
            id="topbar-profile"
            className={styles.menu}
            role="menu"
            aria-label="Account"
          >
            <div className={styles.profileSummary}>
              <span className={styles.avatarLarge}>{initials}</span>
              <div>
                <strong>{displayName}</strong>
                {user?.email && <span>{user.email}</span>}
              </div>
            </div>
            <div className={styles.menuList}>
              <button type="button" role="menuitem" onClick={() => goTo('/dashboard')}>
                <span className="material-symbols-outlined">dashboard</span>
                Dashboard
              </button>
              <button type="button" role="menuitem" onClick={() => goTo('/history')}>
                <span className="material-symbols-outlined">receipt_long</span>
                Activity
              </button>
              <button
                type="button"
                role="menuitem"
                className={styles.dangerItem}
                onClick={handleLogout}
              >
                <span className="material-symbols-outlined">logout</span>
                Logout
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

function readStoredNotificationIds(key) {
  try {
    const raw = localStorage.getItem(key);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.map(String) : [];
  } catch {
    return [];
  }
}

function notificationId(tx) {
  const status = String(tx?.status || 'alert').toUpperCase();
  const confirmationState = tx?.requires_password_confirmation
    ? 'confirmed'
    : 'standard';
  if (tx?.id) return `${tx.id}:${status}:${confirmationState}`;
  return `${tx?.status || 'alert'}-${tx?.created_at || ''}-${tx?.amount || ''}`;
}

function notificationIcon(tx) {
  const status = String(tx.status || '').toUpperCase();
  if (status === 'REJECTED') return 'block';
  if (status === 'WARNED' || tx.requires_password_confirmation) return 'warning';
  if (status === 'PENDING') return 'pending';
  return 'notifications';
}

function notificationTitle(tx) {
  const status = String(tx.status || '').toUpperCase();
  if (status === 'REJECTED') return 'Transfer blocked';
  if (status === 'WARNED') return 'Transfer needs review';
  if (tx.requires_password_confirmation) return 'Confirmed after warning';
  if (status === 'PENDING') return 'Transfer pending';
  return 'Account activity';
}
