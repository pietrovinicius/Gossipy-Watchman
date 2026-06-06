import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { UploadCloud, FileVideo, CheckCircle, AlertCircle, X } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../services/api'

const ALLOWED = ['.mp4', '.avi']

function getExt(name) {
  return name.slice(name.lastIndexOf('.')).toLowerCase()
}

export default function Upload() {
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [extError, setExtError] = useState('')
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [dragging, setDragging] = useState(false)

  function selectFile(f) {
    setResult(null)
    setError('')
    setExtError('')
    setProgress(0)
    if (!ALLOWED.includes(getExt(f.name))) {
      setExtError(`Formato não suportado: "${getExt(f.name)}". Use .mp4 ou .avi.`)
      setFile(null)
      return
    }
    setFile(f)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) selectFile(dropped)
  }

  async function handleUpload() {
    if (!file) return
    setUploading(true)
    setError('')
    setProgress(0)

    const form = new FormData()
    form.append('file', file)

    try {
      const res = await api.post('/videos/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) setProgress(Math.round((e.loaded / e.total) * 100))
        },
      })
      setResult(res.data)
      setFile(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  function reset() {
    setFile(null)
    setResult(null)
    setError('')
    setExtError('')
    setProgress(0)
  }

  const sizeMB = file ? (file.size / 1024 / 1024).toFixed(1) : null

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-text-base">Upload de Vídeo</h1>

        {result ? (
          /* Success state */
          <div className="card border-success/30 bg-success/5 text-center space-y-4">
            <CheckCircle className="w-12 h-12 text-success mx-auto" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-text-base">Vídeo enviado com sucesso!</h2>
            <div className="text-sm text-text-muted space-y-1">
              <p>ID: <span className="font-mono text-text-base">#{result.id}</span></p>
              <p>Status: <span className="text-warning font-medium">{result.status}</span></p>
            </div>
            <div className="flex gap-3 justify-center">
              <button onClick={() => navigate('/dashboard')} className="btn-primary">
                Acompanhar no Dashboard
              </button>
              <button onClick={reset} className="px-4 py-2 rounded-lg border border-border
                                                  text-text-muted hover:text-text-base
                                                  hover:border-primary/50 transition-colors
                                                  duration-200 cursor-pointer text-sm">
                Novo upload
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Drop zone */}
            <div
              role="button"
              tabIndex={0}
              aria-label="Área de upload — arraste um arquivo ou clique para selecionar"
              onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onClick={() => inputRef.current?.click()}
              onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer
                          transition-colors duration-200
                          ${dragging
                            ? 'border-primary bg-primary/10'
                            : 'border-border hover:border-primary/50 hover:bg-surface/60'
                          }`}
            >
              <UploadCloud className="w-12 h-12 text-text-muted mx-auto mb-3" aria-hidden="true" />
              <p className="text-text-base font-medium">Arraste um arquivo aqui</p>
              <p className="text-text-muted text-sm mt-1">ou clique para selecionar</p>
              <p className="text-xs text-text-muted mt-2">Formatos aceitos: .mp4, .avi</p>
              <input
                ref={inputRef}
                type="file"
                accept=".mp4,.avi"
                className="hidden"
                aria-hidden="true"
                onChange={(e) => e.target.files[0] && selectFile(e.target.files[0])}
              />
            </div>

            {extError && (
              <p role="alert" className="flex items-center gap-2 text-sm text-error-color
                                         bg-red-950/40 border border-red-800/50 rounded-lg px-3 py-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
                {extError}
              </p>
            )}

            {/* Selected file */}
            {file && (
              <div className="card flex items-center gap-3">
                <FileVideo className="w-8 h-8 text-primary flex-shrink-0" aria-hidden="true" />
                <div className="flex-1 min-w-0">
                  <p className="text-text-base text-sm font-medium truncate">{file.name}</p>
                  <p className="text-text-muted text-xs">{sizeMB} MB</p>
                </div>
                <button
                  onClick={reset}
                  aria-label="Remover arquivo"
                  className="text-text-muted hover:text-error-color transition-colors duration-200 cursor-pointer"
                >
                  <X className="w-4 h-4" aria-hidden="true" />
                </button>
              </div>
            )}

            {/* Progress bar */}
            {uploading && (
              <div aria-label={`Upload ${progress}%`} className="space-y-1">
                <div className="flex justify-between text-xs text-text-muted">
                  <span>Enviando...</span>
                  <span>{progress}%</span>
                </div>
                <div className="h-2 bg-border rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-300 rounded-full"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {error && (
              <p role="alert" className="flex items-center gap-2 text-sm text-error-color
                                         bg-red-950/40 border border-red-800/50 rounded-lg px-3 py-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
                {error}
              </p>
            )}

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full btn-primary py-3 flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" aria-hidden="true" />
                  Enviando…
                </>
              ) : (
                <>
                  <UploadCloud className="w-4 h-4" aria-hidden="true" />
                  Enviar vídeo
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </Layout>
  )
}
