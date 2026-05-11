import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api/client';
import { formatCurrency, formatDateTime } from '../../utils/format';
import StatusBadge from '../../components/StatusBadge/StatusBadge.jsx';
import styles from './Dashboard.module.css';

const POLL_INTERVAL_MS = 5000;
const DEFAULT_MONTHLY_BUDGET = 10000;

export default function Dashboard() {
  const navigate = useNavigate();
  const [account, setAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('week');

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const [acc, list] = await Promise.all([
          api.myAccount(),
          api.myTransactions(),
        ]);
        if (cancelled) return;
        setAccount(acc);
        setTransactions(list?.transactions || []);
        setError(null);
      } catch (err) {
        if (!cancelled) setError(err.message || 'Failed to load dashboard.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    const id = setInterval(load, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const stats = useMemo(() => {
    if (!account) return { monthly: 0, count: 0 };
    const now = new Date();
    const currentMonth = now.getMonth();
    const currentYear = now.getFullYear();

    let monthly = 0;
    let count = 0;

    for (const tx of transactions) {
      const created = tx.created_at ? new Date(tx.created_at) : null;
      if (!created) continue;
      const status = String(tx.status).toUpperCase();
      const isOutgoing = tx.sender_id === account.id;
      const amount = Number(tx.amount) || 0;
      const isCompleted = status === 'SETTLED' || status === 'APPROVED';

      if (
        isOutgoing &&
        isCompleted &&
        created.getMonth() === currentMonth &&
        created.getFullYear() === currentYear
      ) {
        monthly += amount;
        count += 1;
      }
    }

    return { monthly, count };
  }, [transactions, account]);

  const chart = useMemo(() => {
    if (!account) return { buckets: [], labels: [], activeIdx: -1 };
    const now = new Date();
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];

    let buckets = [];
    let labels = [];
    let activeIdx = -1;
    // bucket(tx) -> index | -1
    let bucketFor = () => -1;

    if (period === 'week') {
      const weekStart = new Date(today);
      const offsetToMonday = (today.getDay() + 6) % 7;
      weekStart.setDate(today.getDate() - offsetToMonday);
      buckets = Array.from({ length: 7 }, () => ({ income: 0, outcome: 0 }));
      labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      activeIdx = (now.getDay() + 6) % 7;
      bucketFor = (created) => {
        const d = new Date(created);
        d.setHours(0, 0, 0, 0);
        const idx = Math.round((d - weekStart) / (1000 * 60 * 60 * 24));
        return idx >= 0 && idx < 7 ? idx : -1;
      };
    } else if (period === 'month') {
      // 4 weekly buckets within the current month
      const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
      const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 1);
      buckets = Array.from({ length: 4 }, () => ({ income: 0, outcome: 0 }));
      labels = ['W1', 'W2', 'W3', 'W4'];
      const dayOfMonth = now.getDate();
      activeIdx = Math.min(3, Math.floor((dayOfMonth - 1) / 7));
      bucketFor = (created) => {
        if (created < monthStart || created >= monthEnd) return -1;
        return Math.min(3, Math.floor((created.getDate() - 1) / 7));
      };
    } else {
      // year: 12 monthly buckets
      const yearStart = new Date(now.getFullYear(), 0, 1);
      const yearEnd = new Date(now.getFullYear() + 1, 0, 1);
      buckets = Array.from({ length: 12 }, () => ({ income: 0, outcome: 0 }));
      labels = months;
      activeIdx = now.getMonth();
      bucketFor = (created) => {
        if (created < yearStart || created >= yearEnd) return -1;
        return created.getMonth();
      };
    }

    for (const tx of transactions) {
      const created = tx.created_at ? new Date(tx.created_at) : null;
      if (!created) continue;
      const status = String(tx.status).toUpperCase();
      if (status !== 'SETTLED' && status !== 'APPROVED') continue;
      const idx = bucketFor(created);
      if (idx < 0) continue;
      const amount = Number(tx.amount) || 0;
      if (tx.sender_id === account.id) buckets[idx].outcome += amount;
      else buckets[idx].income += amount;
    }

    return { buckets, labels, activeIdx };
  }, [transactions, account, period]);

  const recent = useMemo(() => transactions.slice(0, 4), [transactions]);

  const currency = account?.currency || 'EUR';
  const budgetUsedPct = Math.min(
    100,
    Math.round((stats.monthly / DEFAULT_MONTHLY_BUDGET) * 100)
  );

  const chartMax = Math.max(
    1,
    ...chart.buckets.flatMap((d) => [d.income, d.outcome])
  );

  return (
    <div className={styles.page}>
      {error && <div className={styles.error}>{error}</div>}

      <section className={styles.heroGrid}>
        <article className={styles.balanceCard}>
          <div className={styles.balanceTopRow}>
            <span className="material-symbols-outlined">account_balance_wallet</span>
            <span>Total Balance</span>
          </div>
          <h2 className={styles.balanceValue}>
            {loading ? '…' : formatCurrency(account?.balance, currency)}
          </h2>
          <div className={styles.balanceMetaRow}>
            <span className={styles.deltaPill}>
              <span className="material-symbols-outlined">verified_user</span>
              IBAN {account?.iban || '—'}
            </span>
          </div>
          <div className={styles.balanceActions}>
            <button
              type="button"
              className={styles.primaryAction}
              onClick={() => navigate('/send')}
            >
              <span className="material-symbols-outlined filled">send</span>
              Send Money
            </button>
            <button type="button" className={styles.secondaryAction} disabled>
              <span className="material-symbols-outlined">add</span>
              Add Funds
            </button>
          </div>
          <div className={styles.balanceGlow} aria-hidden />
        </article>

        <article className={styles.spendingCard}>
          <h3>Monthly Spending</h3>
          <div className={styles.spendingValue}>
            {formatCurrency(stats.monthly, currency)}
          </div>
          <p>{stats.count} transactions this month</p>
          <div className={styles.budgetRow}>
            <div className={styles.budgetTop}>
              <span>Budget limit</span>
              <strong>{formatCurrency(DEFAULT_MONTHLY_BUDGET, currency)}</strong>
            </div>
            <div className={styles.budgetTrack}>
              <div
                className={styles.budgetFill}
                style={{ width: `${budgetUsedPct}%` }}
              />
            </div>
          </div>
        </article>
      </section>

      <section className={styles.midGrid}>
        <article className={styles.cardWidget}>
          <header>
            <h3>My Cards</h3>
            <button type="button" className={styles.iconBtnSmall} aria-label="Add card">
              <span className="material-symbols-outlined">add</span>
            </button>
          </header>
          <div className={styles.creditCard}>
            <div className={styles.cardChip} />
            <div className={styles.cardLogo}>
              <span />
              <span />
            </div>
            <div className={styles.cardNumber}>
              •••• •••• •••• {(account?.iban || 'XXXX').slice(-4)}
            </div>
            <div className={styles.cardFooter}>
              <div>
                <p>Card Holder</p>
                <strong>{account ? truncateName(account) : '—'}</strong>
              </div>
              <div>
                <p>Expires</p>
                <strong>12/28</strong>
              </div>
            </div>
          </div>
          <div className={styles.cardControls}>
            {[
              { icon: 'ac_unit', label: 'Freeze' },
              { icon: 'visibility', label: 'Details' },
              { icon: 'settings', label: 'Settings' },
            ].map((c) => (
              <button key={c.label} type="button">
                <span className="material-symbols-outlined">{c.icon}</span>
                <span>{c.label}</span>
              </button>
            ))}
          </div>
        </article>

        <article className={styles.statsCard}>
          <header>
            <h3>Money Statistics</h3>
            <div className={styles.segmented}>
              {['week', 'month', 'year'].map((p) => (
                <button
                  key={p}
                  type="button"
                  className={period === p ? styles.segmentedActive : ''}
                  onClick={() => setPeriod(p)}
                >
                  {p[0].toUpperCase() + p.slice(1)}
                </button>
              ))}
            </div>
          </header>
          <div className={styles.legend}>
            <span><i className={styles.dotIncome} /> Income</span>
            <span><i className={styles.dotOutcome} /> Outcome</span>
          </div>
          <div className={styles.chart}>
            {chart.buckets.map((d, idx) => (
              <div key={idx} className={styles.chartDay}>
                <div className={styles.chartBars}>
                  <span
                    className={styles.barIncome}
                    style={{ height: `${(d.income / chartMax) * 100}%` }}
                  />
                  <span
                    className={styles.barOutcome}
                    style={{ height: `${(d.outcome / chartMax) * 100}%` }}
                  />
                </div>
                <span
                  className={
                    idx === chart.activeIdx ? styles.chartLabelActive : styles.chartLabel
                  }
                >
                  {chart.labels[idx]}
                </span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className={styles.activitySection}>
        <div className={styles.activityHeader}>
          <h2>Recent Activity</h2>
          <button
            type="button"
            className={styles.linkAction}
            onClick={() => navigate('/history')}
          >
            View All
            <span className="material-symbols-outlined">arrow_forward</span>
          </button>
        </div>
        <div className={styles.activityCard}>
          {loading ? (
            <div className={styles.empty}>Loading transactions…</div>
          ) : recent.length === 0 ? (
            <div className={styles.empty}>No transactions yet.</div>
          ) : (
            recent.map((tx) => (
              <TransactionRow
                key={tx.id}
                tx={tx}
                accountId={account?.id}
                currency={currency}
              />
            ))
          )}
        </div>
      </section>
    </div>
  );
}

function truncateName(account) {
  return (account.full_name || account.email || 'Account').toString().slice(0, 22);
}

function TransactionRow({ tx, accountId, currency }) {
  const isOutgoing = tx.sender_id === accountId;
  const sign = isOutgoing ? '-' : '+';
  const icon = isOutgoing ? 'storefront' : 'south_west';
  return (
    <div className={styles.txRow}>
      <div className={styles.txLeft}>
        <div
          className={`${styles.txIcon} ${
            isOutgoing ? styles.outgoing : styles.incoming
          }`}
        >
          <span className="material-symbols-outlined">{icon}</span>
        </div>
        <div>
          <div className={styles.txTitle}>
            {tx.description || (isOutgoing ? 'Outgoing transfer' : 'Incoming transfer')}
          </div>
          <div className={styles.txMeta}>
            {isOutgoing ? 'Outgoing' : 'Incoming'} · {formatDateTime(tx.created_at)}
          </div>
        </div>
      </div>
      <div className={styles.txRight}>
        <StatusBadge status={tx.status} wasWarned={tx.requires_password_confirmation} />
        <span className={styles.txAmount}>
          {sign}
          {formatCurrency(tx.amount, tx.currency || currency)}
        </span>
      </div>
    </div>
  );
}
