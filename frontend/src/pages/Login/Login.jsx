import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext.jsx';
import styles from '../Auth/Auth.module.css';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(form);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message || 'Unable to sign in.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className={styles.page}>
      <aside className={styles.brand}>
        <div className={styles.brandTop}>
          <span className={`material-symbols-outlined filled ${styles.brandIcon}`}>
            security
          </span>
          <h1 className={styles.brandTitle}>SafeFlow AI</h1>
        </div>
        <div className={styles.brandCopy}>
          <h2>Secure, seamless financial management.</h2>
          <p>
            Experience next-generation institutional controls and automated
            reconciliation in one minimal interface.
          </p>
        </div>
      </aside>

      <div className={styles.formPanel}>
        <div className={styles.card}>
          <div className={styles.mobileBrand}>
            <span className={`material-symbols-outlined filled ${styles.brandIcon}`}>
              security
            </span>
            <span className={styles.brandTitle}>SafeFlow AI</span>
          </div>
          <div className={styles.cardHeader}>
            <h2>Welcome back</h2>
            <p>Enter your credentials to access your dashboard.</p>
          </div>

          {error && <div className={styles.errorBanner}>{error}</div>}

          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.field}>
              <label className={styles.label} htmlFor="email">
                Email Address
              </label>
              <div className={styles.inputWrap}>
                <span className={`material-symbols-outlined ${styles.inputIcon}`}>
                  mail
                </span>
                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  className={styles.input}
                  placeholder="name@company.com"
                  value={form.email}
                  onChange={update('email')}
                />
              </div>
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="password">
                Password
              </label>
              <div className={styles.inputWrap}>
                <span className={`material-symbols-outlined ${styles.inputIcon}`}>
                  lock
                </span>
                <input
                  id="password"
                  type="password"
                  required
                  autoComplete="current-password"
                  className={styles.input}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={update('password')}
                />
              </div>
            </div>

            <button type="submit" className={styles.submit} disabled={submitting}>
              {submitting ? 'Signing in…' : 'Sign In'}
              <span className="material-symbols-outlined">arrow_forward</span>
            </button>
          </form>

          <div className={styles.footer}>
            Don&apos;t have an account? <Link to="/register">Request Access</Link>
          </div>
        </div>
      </div>
    </section>
  );
}
