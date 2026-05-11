import styles from './StatusBadge.module.css';

const STATUS_META = {
  PENDING: { label: 'Pending', tone: 'pending', icon: 'pending' },
  APPROVED: { label: 'Approved', tone: 'approved', icon: 'check' },
  WARNED: { label: 'Warned', tone: 'warned', icon: 'warning' },
  SETTLED: { label: 'Settled', tone: 'settled', icon: 'check_circle' },
  CANCELED: { label: 'Canceled', tone: 'canceled', icon: 'cancel' },
  REJECTED: { label: 'Rejected', tone: 'rejected', icon: 'block' },
};

export default function StatusBadge({ status }) {
  const meta = STATUS_META[status] || {
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
