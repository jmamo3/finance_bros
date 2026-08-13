import { useState } from "react";

function Onboarding({ onComplete }) {
  const [form, setForm] = useState({
    goal: "",
    risk: "medium",
    horizon: "",
    income: "",
  });

  const handleSubmit = () => {
    if (!form.goal || !form.horizon || !form.income) {
      alert("Please fill out all fields.");
      return;
    }
    onComplete(form);
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.logo}>FA</div>
        <h1 style={styles.title}>Financial Advisor</h1>
        <p style={styles.subtitle}>Personalized financial guidance, powered by AI</p>

        <div style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>What's your main financial goal?</label>
            <input
              style={styles.input}
              placeholder="e.g. save for retirement, pay off debt, invest"
              value={form.goal}
              onChange={(e) => setForm({ ...form, goal: e.target.value })}
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Risk tolerance</label>
            <select
              style={styles.input}
              value={form.risk}
              onChange={(e) => setForm({ ...form, risk: e.target.value })}
            >
              <option value="low">Low — I prefer stability</option>
              <option value="medium">Medium — Balanced approach</option>
              <option value="high">High — I can handle volatility</option>
            </select>
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Time horizon</label>
            <input
              style={styles.input}
              placeholder="e.g. 3-5 years, long term"
              value={form.horizon}
              onChange={(e) => setForm({ ...form, horizon: e.target.value })}
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Approximate annual income</label>
            <input
              style={styles.input}
              placeholder="e.g. $50,000"
              value={form.income}
              onChange={(e) => setForm({ ...form, income: e.target.value })}
            />
          </div>

          <button style={styles.button} onClick={handleSubmit}>
            Get Started →
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    backgroundColor: "#f0f4ff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "40px 20px",
    fontFamily: "'Inter', sans-serif",
  },
  card: {
    backgroundColor: "#ffffff",
    borderRadius: "20px",
    padding: "48px 40px",
    width: "100%",
    maxWidth: "480px",
    boxShadow: "0 8px 40px rgba(99, 102, 241, 0.12)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  logo: {
    width: "56px",
    height: "56px",
    borderRadius: "16px",
    backgroundColor: "#6366f1",
    color: "#fff",
    fontSize: "1.2rem",
    fontWeight: "800",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "16px",
    letterSpacing: "1px",
  },
  title: {
    color: "#1e1b4b",
    fontSize: "1.8rem",
    fontWeight: "700",
    margin: "0 0 8px 0",
    textAlign: "center",
  },
  subtitle: {
    color: "#6b7280",
    fontSize: "0.95rem",
    marginBottom: "36px",
    textAlign: "center",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    width: "100%",
    gap: "20px",
  },
  field: {
    display: "flex",
    flexDirection: "column",
    gap: "6px",
  },
  label: {
    color: "#374151",
    fontSize: "0.875rem",
    fontWeight: "600",
  },
  input: {
    padding: "12px 14px",
    borderRadius: "10px",
    border: "1.5px solid #e5e7eb",
    backgroundColor: "#f9fafb",
    color: "#111827",
    fontSize: "0.95rem",
    outline: "none",
    transition: "border-color 0.2s",
    fontFamily: "'Inter', sans-serif",
  },
  button: {
    marginTop: "8px",
    padding: "14px",
    borderRadius: "10px",
    border: "none",
    backgroundColor: "#6366f1",
    color: "#fff",
    fontSize: "1rem",
    cursor: "pointer",
    fontWeight: "700",
    fontFamily: "'Inter', sans-serif",
    letterSpacing: "0.3px",
  },
};

export default Onboarding;