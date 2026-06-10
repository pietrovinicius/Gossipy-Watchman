import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { BarChart2, Users, Video, Layers } from 'lucide-react'
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts'
import Layout from '../components/Layout'
import api from '../services/api'

function MetricCard({ label, value, Icon }) {
  return (
    <div className="bg-surface border border-border rounded-xl p-5 flex items-center gap-4">
      <div className="bg-primary/10 rounded-lg p-3">
        <Icon className="w-5 h-5 text-primary" aria-hidden="true" />
      </div>
      <div>
        <p className="text-2xl font-bold text-text-base">{value}</p>
        <p className="text-xs text-text-muted">{label}</p>
      </div>
    </div>
  )
}

export default function AnalyticsDashboard() {
  const { t } = useTranslation()
  const [overview, setOverview] = useState(null)
  const [timeline, setTimeline] = useState([])
  const [topPeople, setTopPeople] = useState([])
  const [perVideo, setPerVideo] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchAll() {
      try {
        const [ovRes, tlRes, tpRes, pvRes] = await Promise.all([
          api.get('/analytics/overview'),
          api.get('/analytics/activity-timeline?days=30'),
          api.get('/analytics/top-people?limit=10'),
          api.get('/analytics/appearances-per-video'),
        ])
        setOverview(ovRes.data)
        setTimeline(tlRes.data)
        setTopPeople(tpRes.data)
        setPerVideo(pvRes.data.slice(0, 10))
      } catch (err) {
        setError(err.message || t('analytics.errorLoading'))
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center py-24">
          <div role="status" aria-label={t('analytics.loading')}
               className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout>
        <p role="alert" className="text-error-color text-sm">{error}</p>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="flex items-center gap-3">
          <BarChart2 className="w-6 h-6 text-primary" aria-hidden="true" />
          <h1 className="text-xl font-bold text-text-base">{t('analytics.title')}</h1>
        </div>

        {/* Metric cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <MetricCard label={t('analytics.videosProcessed')} value={overview?.total_videos ?? 0} Icon={Video} />
          <MetricCard label={t('analytics.peopleCataloged')} value={overview?.total_people ?? 0} Icon={Users} />
          <MetricCard label={t('analytics.appearancesRegistered')} value={overview?.total_appearances ?? 0} Icon={Layers} />
        </div>

        {/* Timeline */}
        <div className="bg-surface border border-border rounded-xl p-5">
          <h2 className="text-sm font-semibold text-text-base mb-4">{t('analytics.activityLast30Days')}</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={timeline}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: "var(--chart-text)" }} />
              <YAxis tick={{ fontSize: 10, fill: "var(--chart-text)" }} allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="count" name={t('analytics.videosProcessed')} stroke="#6366f1" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top pessoas */}
          <div className="bg-surface border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold text-text-base mb-4">{t('analytics.topPeopleByAppearances')}</h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={topPeople} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                <XAxis type="number" tick={{ fontSize: 10, fill: "var(--chart-text)" }} allowDecimals={false} />
                <YAxis dataKey="person_name" type="category" tick={{ fontSize: 10, fill: "var(--chart-text)" }} width={80} />
                <Tooltip />
                <Bar dataKey="appearance_count" name={t('analytics.appearances')} fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <ol className="mt-3 space-y-1">
              {topPeople.slice(0, 5).map((p, i) => (
                <li key={p.person_id} className="flex justify-between text-xs text-text-muted">
                  <span>{i + 1}. {p.person_name}</span>
                  <span>{p.appearance_count} {t('analytics.appearances')}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Aparições por vídeo */}
          <div className="bg-surface border border-border rounded-xl p-5">
            <h2 className="text-sm font-semibold text-text-base mb-4">{t('analytics.appearancesPerVideoTop10')}</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={perVideo}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                <XAxis dataKey="file_name" tick={{ fontSize: 9, fill: "var(--chart-text)" }} />
                <YAxis tick={{ fontSize: 10, fill: "var(--chart-text)" }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" name={t('analytics.appearances')} fill="#22d3ee" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </Layout>
  )
}
