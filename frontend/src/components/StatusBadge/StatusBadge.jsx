import styles from './StatusBadge.module.css';

const STATUS_META = {
  PENDING: { label: 'Pending', tone: 'pending', icon: 'pending' },
  APPROVED: { label: 'Approved', tone: 'approved', icon: 'check' },
  WARNED: { label: 'Warned', tone: 'warned', icon: 'warning' },
  SETTLED: { label: 'Settled', tone: 'settled', icon: 'check_circle' },
  CANCELED: { label: 'Canceled', tone: 'canceled', icon: 'cancel' },
  REJECTED: { label: 'Rejected', tone: 'rejected', icon: 'block' },
};

const WARNED_CONFIRMED_META = {
  label: 'Warned · Confirmed',
  tone: 'warnedConfirmed',
  icon: 'verified',
};

export default function StatusBadge({ status, wasWarned = false }) {
  const upper = String(status || '').toUpperCase();
  const meta =
    wasWarned && upper === 'SETTLED'
      ? WARNED_CONFIRMED_META
      : STATUS_META[upper] || {
          label: status || 'Unknown',
          tone: 'pending',
          icon: 'help',
        };
  return (
    <span className={`${styles.badge} ${styles[meta.tone]}`}>
      <span className="material-symbols-outlined">{meta.icon}</span>
      {meta.label}
    </span>
  );
}
