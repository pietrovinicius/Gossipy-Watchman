import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Search,
  Download,
  RefreshCw,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Film,
  Eye,
  EyeOff,
} from 'lucide-react'
import Layout from '../components/Layout'
import ConfirmModal from '../components/ConfirmModal'
import api from '../services/api'
import { useTheme } from '../contexts/ThemeContext'
import { useAuthVideoThumbnail } from '../hooks/useAuthVideoThumbnail'
import { useVideoActions } from '../hooks/useVideoActions'

const STATUS_COLORS = {
  'Pendente': { bg: 'bg-yellow-100', text: 'text-yellow-800', dark: 'dark:bg-yellow-900 dark:text-yellow-200', key: 'status.pending' },
  'Processando': { bg: 'bg-blue-100', text: 'text-blue-800', dark: 'dark:bg-blue-900 dark:text-blue-200', key: 'status.processing' },
  'Concluído': { bg: 'bg-green-100', text: 'text-green-800', dark: 'dark:bg-green-900 dark:text-green-200', key: 'status.completed' },
  'Erro': { bg: 'bg-red-100', text: 'text-red-800', dark: 'dark:bg-red-900 dark:text-red-200', key: 'status.error' },
}

function VideoCard({ video, onDelete, onReprocess, onExport, loading, loadingAction }) {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const dateLocale = i18n.language === 'pt-BR' ? 'pt-BR' : 'en-US'
  const status = video.status
  const colors = STATUS_COLORS[status] || STATUS_COLORS['Pendente']
  const thumbnailSrc = useAuthVideoThumbnail(video.id, Boolean(video.thumbnail_path))

  return (
    <div
      className="bg-card rounded-lg overflow-hidden border border-border hover:border-primary/50 transition-all duration-200 flex flex-col h-full cursor-pointer"
      onClick={() => navigate(`/videos/${video.id}`)}
    >
      {/* Thumbnail + Badge */}
      <div className="relative w-full pt-[56.25%] bg-slate-100 dark:bg-slate-800 overflow-hidden group">
        {thumbnailSrc ? (
          <img
            src={thumbnailSrc}
            alt={video.file_name}
            className="absolute inset-0 w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <Film className="w-12 h-12 text-slate-400 dark:text-slate-600" />
          </div>
        )}
        <div className={`absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center`}>
          <div className="text-center">
            <div className="text-white text-lg">▶</div>
            <div className="text-white text-xs mt-1">{t('personDetail.viewVideoDetails')}</div>
          </div>
        </div>
        <div className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium ${colors.bg} ${colors.text} ${colors.dark}`}>
          {colors.key ? t(colors.key) : status}
        </div>
      </div>

      {/* Metadados */}
      <div className="p-4 flex-1 flex flex-col">
        <h3 className="font-medium text-sm text-text-base truncate" title={video.file_name}>
          {video.file_name}
        </h3>
        <p className="text-xs text-text-muted mt-1">
          {new Date(video.uploaded_at).toLocaleDateString(dateLocale, {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
        <p className="text-xs text-text-muted mt-1">👤 {t('videos.people', { count: video.people_count })}</p>

        {/* Mini Galeria */}
        <div className="mt-3 flex items-center gap-2">
          <div className="flex items-center -space-x-2">
            {video.people_previews.slice(0, 4).map((person) => (
              <div
                key={person.person_id}
                className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-xs text-white font-medium border-2 border-card overflow-hidden flex-shrink-0"
                title={person.person_name}
              >
                {person.profile_image_path ? (
                  <img
                    src={`${import.meta.env.VITE_API_URL}/faces/${person.profile_image_path}`}
                    alt={person.person_name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none'
                      e.target.nextElementSibling.style.display = 'block'
                    }}
                  />
                ) : null}
                <span className="text-xs" style={{ display: person.profile_image_path ? 'none' : 'block' }}>
                  {person.person_name.charAt(0)}
                </span>
              </div>
            ))}
            {video.people_count > 4 && (
              <div className="w-7 h-7 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-xs font-medium text-text-base border-2 border-card flex-shrink-0">
                +{video.people_count - 4}
              </div>
            )}
          </div>
        </div>

        {video.people_count === 0 && video.status === 'Concluído' && (
          <p className="text-xs text-text-muted mt-2">{t('videos.noPeople')}</p>
        )}
      </div>

      {/* Ações */}
      <div className="p-4 border-t border-border flex items-center gap-2 justify-end" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={() => onExport(video.id, video.file_name)}
          disabled={loading === video.id && loadingAction === 'export'}
          className="p-2 hover:bg-card rounded-lg text-text-muted hover:text-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title={t('videoDetail.exportCsv')}
        >
          {loading === video.id && loadingAction === 'export' ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Download className="w-4 h-4" />
          )}
        </button>

        {(video.status === 'Concluído' || video.status === 'Erro') && (
          <button
            onClick={() => onReprocess(video.id)}
            disabled={loading === video.id && loadingAction === 'reprocess'}
            className="p-2 hover:bg-card rounded-lg text-text-muted hover:text-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title={t('common.reprocess')}
          >
            {loading === video.id && loadingAction === 'reprocess' ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
          </button>
        )}

        <button
          onClick={() => onDelete(video.id)}
          disabled={loading === video.id && loadingAction === 'delete'}
          className="p-2 hover:bg-card rounded-lg text-text-muted hover:text-error-color transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title={t('common.delete')}
        >
          {loading === video.id && loadingAction === 'delete' ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Trash2 className="w-4 h-4" />
          )}
        </button>
      </div>
    </div>
  )
}

function VideoCardSkeleton() {
  return (
    <div className="bg-card rounded-lg overflow-hidden border border-border animate-pulse">
      <div className="w-full pt-[56.25%] bg-slate-200 dark:bg-slate-700" />
      <div className="p-4 space-y-3">
        <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4" />
        <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/2" />
        <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/3" />
      </div>
      <div className="p-4 border-t border-border flex justify-end gap-2">
        <div className="h-8 w-8 bg-slate-200 dark:bg-slate-700 rounded" />
        <div className="h-8 w-8 bg-slate-200 dark:bg-slate-700 rounded" />
      </div>
    </div>
  )
}

export default function VideosCatalog() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { theme } = useTheme()
  const [videos, setVideos] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(12)
  const [totalPages, setTotalPages] = useState(0)
  const [loading, setLoading] = useState(false)
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [status, setStatus] = useState('')
  const [sortBy, setSortBy] = useState('uploaded_at_desc')
  const [layout, setLayout] = useState(() => localStorage.getItem('gw-videos-layout') || 'grid')
  const [includeDeleted, setIncludeDeleted] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const { exportCsv, reprocess, softDelete, loadingId, loadingAction } = useVideoActions({
    onSuccess: (action) => {
      if (['delete', 'reprocess', 'restore'].includes(action)) setRefreshKey((k) => k + 1)
    },
    onError: () => {},
  })

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 400)
    return () => clearTimeout(timer)
  }, [query])

  // Fetch videos
  const fetchVideos = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (debouncedQuery) params.append('q', debouncedQuery)
      if (status) params.append('status', status)
      params.append('sort_by', sortBy)
      params.append('page', page)
      params.append('page_size', pageSize)
      params.append('include_deleted', includeDeleted)

      const res = await api.get(`/videos/catalog?${params}`)
      setVideos(res.data.items)
      setTotal(res.data.total)
      setTotalPages(res.data.total_pages)
    } catch (error) {
      console.error('Error fetching videos:', error)
    } finally {
      setLoading(false)
    }
  }, [debouncedQuery, status, sortBy, page, pageSize, includeDeleted, refreshKey])

  useEffect(() => {
    setPage(1)
  }, [debouncedQuery, status, sortBy, includeDeleted])

  useEffect(() => {
    fetchVideos()
  }, [fetchVideos])

  const handleDelete = (videoId) => {
    setDeleteConfirm(videoId)
  }

  const confirmDelete = () => {
    if (!deleteConfirm) return
    const id = deleteConfirm
    setDeleteConfirm(null)
    softDelete(id)
  }

  const handleReprocess = (videoId) => { reprocess(videoId) }

  const handleExport = (videoId, fileName) => { exportCsv(videoId, fileName) }

  const handleLayoutChange = (newLayout) => {
    setLayout(newLayout)
    localStorage.setItem('gw-videos-layout', newLayout)
  }

  const startIndex = (page - 1) * pageSize + 1
  const endIndex = Math.min(page * pageSize, total)

  return (
    <Layout>
      <div className="p-6 max-w-full">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-base">{t('videos.title')}</h1>
          <p className="text-text-muted mt-2">
            {t('videos.totalCount', { count: total })}
          </p>
        </div>

        {/* Controls Bar */}
        <div className="mb-6 flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
            <input
              type="text"
              placeholder={t('videos.searchPlaceholder')}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-lg border border-border bg-card text-text-base placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="px-3 py-2 rounded-lg border border-border bg-card text-text-base focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">{t('common.all')}</option>
            <option value="Pendente">{t('status.pending')}</option>
            <option value="Processando">{t('status.processing')}</option>
            <option value="Concluído">{t('status.completed')}</option>
            <option value="Erro">{t('status.error')}</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 rounded-lg border border-border bg-card text-text-base focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="uploaded_at_desc">{t('videos.sortOptions.newest')}</option>
            <option value="uploaded_at_asc">{t('videos.sortOptions.oldest')}</option>
            <option value="name_asc">{t('videos.sortOptions.nameAsc')}</option>
            <option value="name_desc">{t('videos.sortOptions.nameDesc')}</option>
            <option value="people_desc">{t('videos.sortOptions.mostPeople')}</option>
          </select>

          <div className="flex gap-2 border border-border rounded-lg p-1 bg-card">
            <button
              onClick={() => handleLayoutChange('grid')}
              className={`px-3 py-1 rounded transition-colors ${
                layout === 'grid'
                  ? 'bg-primary/20 text-primary'
                  : 'text-text-muted hover:text-text-base'
              }`}
              title={t('videos.layout.grid')}
            >
              ⊞
            </button>
            <button
              onClick={() => handleLayoutChange('list')}
              className={`px-3 py-1 rounded transition-colors ${
                layout === 'list'
                  ? 'bg-primary/20 text-primary'
                  : 'text-text-muted hover:text-text-base'
              }`}
              title={t('videos.layout.list')}
            >
              ⊟
            </button>
          </div>

          <button
            onClick={() => setIncludeDeleted(!includeDeleted)}
            className={`px-3 py-2 rounded-lg border transition-colors ${
              includeDeleted
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border bg-card text-text-muted hover:text-text-base'
            }`}
            title={t('common.showDeleted')}
          >
            {includeDeleted ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>
        </div>

        {/* Content */}
        {loading && videos.length === 0 ? (
          <div className={`grid gap-4 ${layout === 'grid' ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4' : ''}`}>
            {[...Array(6)].map((_, i) => (
              <VideoCardSkeleton key={i} />
            ))}
          </div>
        ) : videos.length === 0 ? (
          <div className="text-center py-12">
            <Film className="w-16 h-16 text-text-muted mx-auto opacity-20 mb-4" />
            <p className="text-text-muted">{t('videos.noVideos')}</p>
            {(query || status) && (
              <p className="text-sm text-text-muted mt-1">{t('videos.noVideosFiltered')}</p>
            )}
            {!query && !status && (
              <button
                onClick={() => navigate('/upload')}
                className="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
              >
                {t('videos.goToUpload')}
              </button>
            )}
          </div>
        ) : (
          <>
            <div className={layout === 'grid' ? 'grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4' : 'space-y-2'}>
              {videos.map((video) => (
                <VideoCard
                  key={video.id}
                  video={video}
                  onDelete={handleDelete}
                  onReprocess={handleReprocess}
                  onExport={handleExport}
                  loading={loadingId}
                  loadingAction={loadingAction}
                />
              ))}
            </div>

            {/* Pagination */}
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-4 p-4 border-t border-border pt-6">
              <p className="text-sm text-text-muted">
                {t('videos.showing', { start: startIndex, end: endIndex, total })}
              </p>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="p-2 rounded-lg border border-border hover:bg-card disabled:opacity-50 disabled:cursor-not-allowed"
                  title={t('videos.previousPage')}
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                <div className="flex gap-1">
                  {[...Array(Math.min(7, totalPages))].map((_, i) => {
                    let pageNum
                    if (totalPages <= 7) {
                      pageNum = i + 1
                    } else if (page <= 3) {
                      pageNum = i + 1
                    } else if (page >= totalPages - 2) {
                      pageNum = totalPages - 6 + i
                    } else {
                      pageNum = page - 3 + i
                    }

                    if (pageNum < 1 || pageNum > totalPages) return null

                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`px-3 py-1 rounded-lg transition-colors ${
                          pageNum === page
                            ? 'bg-primary text-white'
                            : 'border border-border hover:bg-card'
                        }`}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                </div>

                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="p-2 rounded-lg border border-border hover:bg-card disabled:opacity-50 disabled:cursor-not-allowed"
                  title={t('videos.nextPage')}
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      <ConfirmModal
        isOpen={deleteConfirm !== null}
        title={t('videos.deleteConfirmTitle')}
        message={t('videos.deleteConfirmMessage')}
        onConfirm={confirmDelete}
        onCancel={() => setDeleteConfirm(null)}
        isDangerous
      />
    </Layout>
  )
}
