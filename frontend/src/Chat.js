import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

function Chat({ profile, onUpdateProfile }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: `Hi! I'm your Financial Advisor. Based on your goal to **${profile.goal}** with a **${profile.risk} risk tolerance** over **${profile.horizon}**, I'm ready to help. What would you like to know?`,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          history: messages,
          goal: profile.goal,
          risk: profile.risk,
          horizon: profile.horizon,
          income: profile.income,
        }),
      });

      const data = await res.json();
      setMessages([...updatedMessages, { role: "assistant", content: data.response }]);
    } catch (err) {
      setMessages([...updatedMessages, { role: "assistant", content: "Something went wrong. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={styles.container}>
      {/* Navbar */}
      <div style={styles.navbar}>
        <div style={styles.navLogo}>
          <div style={styles.logoBox}>FA</div>
          <span style={styles.navTitle}>Financial Advisor</span>
        </div>
        <div style={styles.navIcons}>
          <button style={styles.iconButton} title="Update Profile" onClick={onUpdateProfile}>
            👤
          </button>
          <button style={styles.iconButton} title="Settings">
            ⚙️
          </button>
        </div>
      </div>

      {/* Messages */}
      <div style={styles.messages}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.bubbleWrapper,
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            {msg.role === "assistant" && <div style={styles.avatar}>FA</div>}
            <div
              style={{
                ...styles.bubble,
                backgroundColor: msg.role === "user" ? "#6366f1" : "#ffffff",
                color: msg.role === "user" ? "#fff" : "#111827",
                boxShadow: msg.role === "assistant" ? "0 2px 12px rgba(0,0,0,0.06)" : "none",
              }}
            >
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ ...styles.bubbleWrapper, justifyContent: "flex-start" }}>
            <div style={styles.avatar}>FA</div>
            <div style={{ ...styles.bubble, backgroundColor: "#ffffff", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" }}>
              <div style={styles.dots}>
                <span style={styles.dot} />
                <span style={{ ...styles.dot, animationDelay: "0.2s" }} />
                <span style={{ ...styles.dot, animationDelay: "0.4s" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={styles.inputRow}>
        <textarea
          style={styles.input}
          placeholder="Ask me anything about your finances..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
        />
        <button style={styles.button} onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>

      {/* Dot animation keyframes */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  );
}

const styles = {
  container: {
    height: "100vh",
    backgroundColor: "#f0f4ff",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    fontFamily: "'Inter', sans-serif",
  },
  navbar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "14px 24px",
    backgroundColor: "#ffffff",
    borderBottom: "1px solid #e5e7eb",
    boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
  },
  navLogo: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  logoBox: {
    width: "36px",
    height: "36px",
    borderRadius: "10px",
    backgroundColor: "#6366f1",
    color: "#fff",
    fontSize: "0.8rem",
    fontWeight: "800",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  navTitle: {
    fontSize: "1rem",
    fontWeight: "700",
    color: "#1e1b4b",
  },
  navIcons: {
    display: "flex",
    gap: "8px",
  },
  iconButton: {
    background: "none",
    border: "none",
    fontSize: "1.2rem",
    cursor: "pointer",
    padding: "6px",
    borderRadius: "8px",
  },
  messages: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    padding: "24px",
    gap: "16px",
    overflowY: "auto",
  },
  bubbleWrapper: {
    display: "flex",
    flexDirection: "row",
    gap: "10px",
    alignItems: "flex-start",
  },
  avatar: {
    width: "32px",
    height: "32px",
    borderRadius: "10px",
    backgroundColor: "#6366f1",
    color: "#fff",
    fontSize: "0.65rem",
    fontWeight: "800",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  bubble: {
    maxWidth: "70%",
    padding: "12px 16px",
    borderRadius: "16px",
    fontSize: "0.95rem",
    lineHeight: "1.6",
  },
  dots: {
    display: "flex",
    gap: "4px",
    alignItems: "center",
    height: "20px",
  },
  dot: {
    width: "7px",
    height: "7px",
    borderRadius: "50%",
    backgroundColor: "#6366f1",
    display: "inline-block",
    animation: "bounce 1.2s infinite ease-in-out",
  },
  inputRow: {
    display: "flex",
    padding: "16px 24px",
    gap: "12px",
    borderTop: "1px solid #e5e7eb",
    backgroundColor: "#ffffff",
  },
  input: {
    flex: 1,
    padding: "12px 16px",
    borderRadius: "12px",
    border: "1.5px solid #e5e7eb",
    backgroundColor: "#f9fafb",
    color: "#111827",
    fontSize: "0.95rem",
    resize: "none",
    outline: "none",
    fontFamily: "'Inter', sans-serif",
  },
  button: {
    padding: "12px 24px",
    borderRadius: "12px",
    border: "none",
    backgroundColor: "#6366f1",
    color: "#fff",
    fontSize: "0.95rem",
    cursor: "pointer",
    fontWeight: "700",
    fontFamily: "'Inter', sans-serif",
  },
};

export default Chat;