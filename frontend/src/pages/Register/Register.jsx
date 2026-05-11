import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext.jsx';
import styles from '../Auth/Auth.module.css';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    accept: false,
  });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const update = (key) => (e) =>
    setForm((f) => ({
      ...f,
      [key]: key === 'accept' ? e.target.checked : e.target.value,
    }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!form.accept) {
      setError('You must accept the Terms of Service.');
      return;
    }
    setSubmitting(true);
    try {
      await register({
        full_name: form.full_name,
        email: form.email,
        password: form.password,
      });
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message || 'Unable to create account.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className={`${styles.page} ${styles.pageReverse}`}>
      <aside className={`${styles.brand} ${styles.brandReverse}`}>
        <div className={styles.brandTop}>
          <span className={`material-symbols-outlined filled ${styles.brandIcon}`}>
            security
          </span>
          <h1 className={styles.brandTitle}>SafeFlow AI</h1>
        </div>
        <div className={styles.brandCopy}>
          <h2>Join the institutional standard.</h2>
          <p>
            Create your account to unlock precision control over your corporate
            treasury flows.
          </p>
        </div>
      </aside>

      <div className={styles.formPanel}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h2>Create your account</h2>
            <p>Set up your profile to get started with SafeFlow AI.</p>
          </div>

          {error && <div className={styles.errorBanner}>{error}</div>}

          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.field}>
              <label className={styles.label} htmlFor="full_name">
                Full Name
              </label>
              <div className={styles.inputWrap}>
                <span className={`material-symbols-outlined ${styles.inputIcon}`}>
                  person
                </span>
                <input
                  id="full_name"
                  type="text"
                  required
                  minLength={2}
                  className={styles.input}
                  placeholder="Jane Doe"
                  value={form.full_name}
                  onChange={update('full_name')}
                />
              </div>
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="regEmail">
                Corporate Email
              </label>
              <div className={styles.inputWrap}>
                <span className={`material-symbols-outlined ${styles.inputIcon}`}>
                  business_center
                </span>
                <input
                  id="regEmail"
                  type="email"
                  required
                  autoComplete="email"
                  className={styles.input}
                  placeholder="jane@company.com"
                  value={form.email}
                  onChange={update('email')}
                />
              </div>
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="regPassword">
                Create Password
              </label>
              <div className={styles.inputWrap}>
                <span className={`material-symbols-outlined ${styles.inputIcon}`}>
                  key
                </span>
                <input
                  id="regPassword"
                  type="password"
                  required
                  minLength={8}
                  autoComplete="new-password"
                  className={styles.input}
                  placeholder="Minimum 8 characters"
                  value={form.password}
                  onChange={update('password')}
                />
              </div>
            </div>

            <label className={styles.checkboxRow}>
              <input
                type="checkbox"
                checked={form.accept}
                onChange={update('accept')}
              />
              <span>
                I agree to the <a href="#tos">Terms of Service</a> and{' '}
                <a href="#privacy">Privacy Policy</a>.
              </span>
            </label>

            <button type="submit" className={styles.submit} disabled={submitting}>
              {submitting ? 'Creating account…' : 'Create Account'}
            </button>
          </form>

          <div className={styles.footer}>
            Already have an account? <Link to="/login">Log in</Link>
          </div>
        </div>
      </div>
    </section>
  );
}
