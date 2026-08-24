import { useState, useCallback } from 'react'

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
}

export default function App() {
  const [file, setFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [length, setLength] = useState('medium')
  const [provider, setProvider] = useState('gemini')
  const [status, setStatus] = useState('idle') // idle | loading | done | error
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

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

  const reset = () => {
    setFile(null)
    setResult(null)
    setError('')
    setStatus('idle')
  }

  return (
    <div className="page">
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
              {file ? (
                <>
                  <p className="filename">{file.name}</p>
                  <p className="hint">Click to choose a different file</p>
                </>
              ) : (
                <>
                  <p className="drop-title">Drop a PDF or image here</p>
                  <p className="hint">or click to browse — max 10MB</p>
                </>
              )}
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
            <h2>Summary</h2>
            <p className="summary-text">{result.parsed.summary}</p>
            {result.parsed.points.length > 0 && (
              <>
                <h3>Key points</h3>
                <ul>
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
