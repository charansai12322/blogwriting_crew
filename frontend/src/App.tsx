import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Sparkles,
  Copy,
  Check,
  Download,
  RotateCcw,
  AlertCircle,
  Loader2,
  FileText,
  Users,
  Feather,
  CheckCircle2,
  Server
} from 'lucide-react';
import { generateBlog, checkBackendHealth, API_BASE_URL } from './api';
import type { BlogGenerateResponse, HealthStatus } from './types';
import './App.css';

const CURRENT_YEAR = new Date().getFullYear();

const SAMPLE_TOPICS = [
  "How AI agents are transforming software development",
  "The future of renewable energy and solid-state batteries",
  "Why clean code architecture matters for high-scale web apps",
];

export const App: React.FC = () => {
  const [topic, setTopic] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [elapsedSeconds, setElapsedSeconds] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BlogGenerateResponse | null>(null);
  const [copied, setCopied] = useState<boolean>(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  const timerRef = useRef<number | null>(null);

  // Check health on mount
  useEffect(() => {
    let isMounted = true;
    checkBackendHealth()
      .then((data) => {
        if (isMounted) {
          setHealth(data);
          setBackendOnline(true);
        }
      })
      .catch(() => {
        if (isMounted) {
          setBackendOnline(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // Timer for execution feedback
  useEffect(() => {
    if (loading) {
      timerRef.current = window.setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [loading]);

  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = topic.trim();
    if (!trimmed) {
      setError("Please enter a blog topic before generating.");
      return;
    }
    if (trimmed.length < 3) {
      setError("Topic should be at least 3 characters long.");
      return;
    }

    setLoading(true);
    setElapsedSeconds(0);
    setError(null);
    setCopied(false);

    try {
      const response = await generateBlog(trimmed);
      setResult(response);
    } catch (err: any) {
      setError(err?.message || "Failed to generate blog post. Please verify backend server and API key.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!result?.blog) return;
    try {
      await navigator.clipboard.writeText(result.blog);
      setCopied(true);
      setTimeout(() => setCopied(false), 2200);
    } catch {
      setError("Failed to copy content to clipboard.");
    }
  };

  const handleDownload = () => {
    if (!result?.blog) return;
    const blob = new Blob([result.blog], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    // Create clean filename slug from topic
    const slug = (result.topic || 'blog-post')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '')
      .slice(0, 45);

    link.href = url;
    link.setAttribute('download', `${slug}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleReset = () => {
    setTopic('');
    setResult(null);
    setError(null);
    setCopied(false);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="brand-badge">
          <Sparkles size={14} /> Multi-Agent AI Workflow
        </div>
        <h1 className="brand-title">Blog Writing Crew</h1>
        <p className="brand-subtitle">
          Collaborative AI editorial team that transforms any topic into a complete, publish-ready blog article.
        </p>

        {/* Pipeline Agents Badge Row */}
        <div className="crew-pipeline">
          <span className="pipeline-step strategist">
            <Users size={13} /> 1. Content Strategist
          </span>
          <span className="pipeline-arrow">→</span>
          <span className="pipeline-step writer">
            <Feather size={13} /> 2. Blog Writer
          </span>
          <span className="pipeline-arrow">→</span>
          <span className="pipeline-step editor">
            <CheckCircle2 size={13} /> 3. Editorial Polish
          </span>
        </div>
      </header>

      {/* Main Topic Input Card */}
      <main className="interactive-card">
        <form className="prompt-form" onSubmit={handleGenerate}>
          <div className="input-label-row">
            <label htmlFor="topic-input" className="input-label">
              Enter your blog topic or premise
            </label>
            <span className="char-counter">{topic.length}/500</span>
          </div>

          <textarea
            id="topic-input"
            className="topic-textarea"
            placeholder="e.g. How AI agents are transforming software development..."
            value={topic}
            maxLength={500}
            disabled={loading}
            onChange={(e) => {
              setTopic(e.target.value);
              if (error) setError(null);
            }}
            rows={3}
          />

          {/* Quick Topic Suggestions */}
          <div className="suggestions-wrapper">
            <span className="suggestions-label">Try an example:</span>
            {SAMPLE_TOPICS.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                className="suggestion-chip"
                disabled={loading}
                onClick={() => {
                  setTopic(sample);
                  if (error) setError(null);
                }}
              >
                {sample}
              </button>
            ))}
          </div>

          {/* Form Actions & Backend Status */}
          <div className="form-actions">
            <div className="backend-badge" title={`Connected API: ${API_BASE_URL}`}>
              <Server size={13} />
              <span>Backend:</span>
              <span className={`status-dot ${backendOnline === false ? 'offline' : ''}`} />
              <span>
                {backendOnline === true
                  ? `Online (${health?.model || 'Ready'})`
                  : backendOnline === false
                  ? 'Offline (Check API)'
                  : 'Connecting...'}
              </span>
            </div>

            <div className="button-group">
              {(result || topic) && (
                <button
                  type="button"
                  className="btn-secondary"
                  disabled={loading}
                  onClick={handleReset}
                >
                  <RotateCcw size={15} /> New Topic
                </button>
              )}

              <button
                type="submit"
                className="btn-primary"
                disabled={loading || !topic.trim()}
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="spin" /> Generating Crew Post...
                  </>
                ) : (
                  <>
                    <Sparkles size={16} /> Generate Blog
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </main>

      {/* Error Banner */}
      {error && (
        <div className="error-banner" role="alert">
          <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div className="error-title">Generation Error</div>
            <div>{error}</div>
          </div>
        </div>
      )}

      {/* Loading State Experience */}
      {loading && (
        <section className="loading-box">
          <div className="loading-pulse-ring" />
          <div className="loading-heading">Crew is working on your blog...</div>
          <p className="loading-subtext">
            The Content Strategist is creating the outline, the Writer is drafting complete sections, and the Editor is polishing grammar and flow.
          </p>
          <div className="loading-timer">
            Elapsed time: {elapsedSeconds}s
          </div>
        </section>
      )}

      {/* Result Container */}
      {!loading && result && (
        <section className="result-container">
          <div className="result-toolbar">
            <div className="result-meta-tags">
              <span className="meta-pill">
                Words: <strong>{result.metadata.stats.word_count}</strong>
              </span>
              <span className="meta-pill">
                Characters: <strong>{result.metadata.stats.char_count}</strong>
              </span>
              <span className="meta-pill">
                Model: <strong>{result.metadata.model}</strong>
              </span>
            </div>

            <div className="result-actions">
              <button
                type="button"
                className={`btn-action ${copied ? 'copied' : ''}`}
                onClick={handleCopy}
              >
                {copied ? <Check size={14} /> : <Copy size={14} />}
                {copied ? 'Copied to Clipboard' : 'Copy Blog'}
              </button>

              <button
                type="button"
                className="btn-action"
                onClick={handleDownload}
              >
                <Download size={14} /> Download .md
              </button>
            </div>
          </div>

          {/* Rendered Article */}
          <article className="markdown-article">
            <ReactMarkdown>{result.blog}</ReactMarkdown>
          </article>
        </section>
      )}

      {/* Empty State when no result yet and not loading */}
      {!loading && !result && !error && (
        <section className="empty-state">
          <FileText size={38} className="empty-icon" />
          <div className="empty-title">Ready for your topic</div>
          <p className="empty-desc">
            Type a topic above or pick a suggested starter to kick off the three-agent CrewAI writing process.
          </p>
        </section>
      )}

      {/* Footer */}
      <footer className="app-footer">
        Blog Writing Crew &copy; {CURRENT_YEAR} &bull; CrewAI Multi-Agent Architecture
      </footer>
    </div>
  );
};

export default App;
