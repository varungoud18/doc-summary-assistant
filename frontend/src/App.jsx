import { useState, useCallback, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// We only use Gemini now


const LENGTHS = [
  { id: 'short', label: 'Short' },
  { id: 'medium', label: 'Medium' },
  { id: 'long', label: 'Long' },
]

function parseSummary(raw) {
  const keyIdx = raw.indexOf('Key Points:')
  if (keyIdx === -1) return { summary: raw.trim(), points: [] }
  const summary = raw.slice(0, keyIdx).replace('Summary:', '').trim()
  const pointsBlock = raw.slice(keyIdx + 'Key Points:'.length)
  const points = pointsBlock
    .split('\n')
    .map((l) => l.replace(/^[-•]\s*/, '').trim())
    .filter(Boolean)
  return { summary, points }
}export default function App() {
  const [file, setFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [length, setLength] = useState('medium')
  const [provider, setProvider] = useState('gemini')
  const [status, setStatus] = useState('idle') // idle | loading | done | error
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark'
  })

  useEffect(() => {
    document.body.className = theme
  }, [theme])

  const toggleTheme = () => {
    setTheme((prev) => {
      const next = prev === 'dark' ? 'light' : 'dark'
      localStorage.setItem('theme', next)
      return next
    })
  }

  const handleFile = (f) => {
    if (!f) return
    setFile(f)
    setStatus('idle')
    setResult(null)
    setError('')
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragActive(false)
    const f = e.dataTransfer.files?.[0]
    handleFile(f)
  }, [])

  const onSubmit = async () => {
    if (!file) return
    setStatus('loading')
    setError('')

    const form = new FormData()
    form.append('file', file)
    form.append('length', length)
    form.append('provider', provider)

    try {
      const res = await fetch(`${API_BASE}/summarize`, {
        method: 'POST',
        body: form,
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Something went wrong summarizing this document.')
      }
      setResult({ ...data, parsed: parseSummary(data.summary) })
      setStatus('done')
    } catch (err) {
      setError(err.message)
      setStatus('error')
    }
  }

  const handleCopy = () => {
    if (!result?.parsed?.summary) return
    navigator.clipboard.writeText(result.parsed.summary)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const reset = () => {
    setFile(null)
    setResult(null)
    setError('')
    setStatus('idle')
  }

  return (
    <div className="page">
      <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
        {theme === 'dark' ? (
          <svg className="theme-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m0 13.5V21M4.93 4.93l1.59 1.59m10.96 10.96 1.59 1.59m-1.59-10.96-1.59 1.59M6.52 17.48l-1.59 1.59M3 12h2.25m13.5 0H21M12 7.5a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9Z" />
          </svg>
        ) : (
          <svg className="theme-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z" />
          </svg>
        )}
      </button>

      <header className="header">
        <div>
          <h1>Document Summary Assistant</h1>
          <p>Upload a PDF or scanned image. Pick a length. Get a summary.</p>
        </div>
      </header>

      <main className="panel">
        {!result && (
          <>
            <div
              className={`dropzone ${dragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}
              onDragOver={(e) => {
                e.preventDefault()
                setDragActive(true)
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={onDrop}
              onClick={() => document.getElementById('file-input').click()}
            >
              <input
                id="file-input"
                type="file"
                accept=".pdf,image/png,image/jpeg,image/webp"
                hidden
                onChange={(e) => handleFile(e.target.files?.[0])}
              />
              <div className="dropzone-content">
                {file ? (
                  <>
                    <div className="doc-icon-wrapper">
                      <svg className="doc-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                      </svg>
                    </div>
                    <p className="filename">{file.name}</p>
                    <p className="hint">Click to choose a different file</p>
                  </>
                ) : (
                  <>
                    <div className="upload-icon-wrapper">
                      <svg className="upload-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
                      </svg>
                    </div>
                    <p className="drop-title">Drop a PDF or image here</p>
                    <p className="hint">or click to browse — max 10MB</p>
                  </>
                )}
              </div>
            </div>

            <div className="controls">
              <fieldset>
                <legend>Length</legend>
                <div className="pill-group">
                  {LENGTHS.map((l) => (
                    <button
                      key={l.id}
                      type="button"
                      className={`pill ${length === l.id ? 'selected' : ''}`}
                      onClick={() => setLength(l.id)}
                    >
                      {l.label}
                    </button>
                  ))}
                </div>
              </fieldset>
            </div>

            {error && <p className="error">{error}</p>}

            <button
              className="submit"
              disabled={!file || status === 'loading'}
              onClick={onSubmit}
            >
              {status === 'loading' ? 'Summarizing…' : 'Generate summary'}
            </button>
          </>
        )}

        {result && (
          <div className="result">
            <div className="result-meta">
              <span className="badge">{result.provider_used}</span>
              {result.fallback && (
                <span className="badge warn">fell back — original model failed</span>
              )}
            </div>
            
            <div className="result-header">
              <h2>Summary</h2>
              <button className="copy-btn" onClick={handleCopy} title="Copy summary">
                {copied ? (
                  <span className="copied-text">Copied!</span>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="copy-icon">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H5.25m11.9-3.664A2.251 2.251 0 0 0 15 2.25h-1.5a2.251 2.251 0 0 0-2.15 1.586m5.8 0c.065.21.1.433.1.664v.75h-6V4.5c0-.231.035-.454.1-.664M6.75 7.5H4.875c-.621 0-1.125.504-1.125 1.125v12c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V16.5a9 9 0 0 0-9-9Z" />
                  </svg>
                )}
              </button>
            </div>
            
            <p className="summary-text">{result.parsed.summary}</p>
            
            {result.parsed.points.length > 0 && (
              <>
                <h3>Key points</h3>
                <ul className="points-list">
                  {result.parsed.points.map((pt, i) => (
                    <li key={i}>{pt}</li>
                  ))}
                </ul>
              </>
            )}
            
            <button className="submit secondary" onClick={reset}>
              Summarize another document
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
