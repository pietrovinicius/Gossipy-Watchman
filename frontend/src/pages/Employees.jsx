import { useState, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { UserPlus, ExternalLink, Edit2, Trash2, AlertCircle } from 'lucide-react'
import Layout from '../components/Layout'
import ConfirmModal from '../components/ConfirmModal'
import api from '../services/api'

function EmployeeRow({ employee, onEdit, onDelete }) {
  const { t } = useTranslation()
  return (
    <tr className="border-b border-border/50 hover:bg-card/50 transition-colors">
      <td className="px-4 py-3">
        {employee.photo_path ? (
          <div className="w-10 h-10 rounded-lg overflow-hidden bg-surface">
            <img
              src={`/storage/employees/${employee.photo_path.split('/').pop()}`}
              alt={employee.name}
              className="w-full h-full object-cover"
            />
          </div>
        ) : (
          <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center text-text-muted text-xs">
            —
          </div>
        )}
      </td>
      <td className="px-4 py-3 font-medium text-text-base">{employee.name}</td>
      <td className="px-4 py-3 font-mono text-sm text-text-muted">
        {employee.registration}
      </td>
      <td className="px-4 py-3 text-sm text-text-muted">{employee.department || '—'}</td>
      <td className="px-4 py-3 text-sm text-text-muted">{employee.role || '—'}</td>
      <td className="px-4 py-3 text-sm text-text-muted">
        {employee.person_id ? (
          <a
            href={`/people/${employee.person_id}`}
            className="text-primary hover:underline flex items-center gap-1"
          >
            #{employee.person_id}
            <ExternalLink className="w-3 h-3" />
          </a>
        ) : (
          '—'
        )}
      </td>
      <td className="px-4 py-3">
        <span
          className={`badge text-xs ${
            employee.active
              ? 'bg-success/20 text-success'
              : 'bg-error-color/20 text-error-color'
          }`}
        >
          {employee.active ? t('common.active') : t('common.inactive')}
        </span>
      </td>
      <td className="px-4 py-3 flex gap-2">
        <button
          onClick={() => onEdit(employee)}
          className="text-text-muted hover:text-primary transition-colors"
          aria-label={t('common.edit')}
        >
          <Edit2 className="w-4 h-4" />
        </button>
        <button
          onClick={() => onDelete(employee.id)}
          className="text-text-muted hover:text-error-color transition-colors"
          aria-label={t('employees.deactivateAria')}
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </td>
    </tr>
  )
}

export default function Employees() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showInactive, setShowInactive] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [deleteId, setDeleteId] = useState(null)
  const [editingEmployee, setEditingEmployee] = useState(null)

  const fetchEmployees = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/employees', {
        params: { active_only: !showInactive },
      })
      setEmployees(res.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [showInactive])

  useEffect(() => {
    fetchEmployees()
  }, [fetchEmployees])

  const handleDelete = async (id) => {
    try {
      await api.delete(`/employees/${id}`)
      setDeleteModalOpen(false)
      fetchEmployees()
    } catch (err) {
      setError(err.message)
      setDeleteModalOpen(false)
    }
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-base">
              {t('employees.title')} ({employees.length})
            </h1>
          </div>
          <button
            onClick={() => {
              setEditingEmployee(null)
              setModalOpen(true)
            }}
            className="flex items-center gap-2 btn-primary"
          >
            <UserPlus className="w-4 h-4" />
            {t('employees.register')}
          </button>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showInactive}
              onChange={(e) => setShowInactive(e.target.checked)}
              className="w-4 h-4 rounded border border-border"
            />
            <span className="text-text-muted">{t('employees.showInactive')}</span>
          </label>
        </div>

        {error && (
          <div className="card border border-error-color/30 bg-red-950/10 flex items-start gap-3 p-3">
            <AlertCircle className="w-5 h-5 text-error-color flex-shrink-0 mt-0.5" />
            <p className="text-sm text-error-color">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="card text-center py-12">
            <p className="text-text-muted">{t('common.loading')}</p>
          </div>
        ) : employees.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-text-muted">{t('employees.noEmployees')}</p>
          </div>
        ) : (
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left px-4 py-3 text-text-muted font-medium text-xs">
                    {t('employees.columns.photo')}
                  </th>
                  <th className="text-left px-4 py-3 text-text-muted font-medium text-xs">
                    {t('employees.columns.name')}
                  </th>
                  <th className="text-left px-4 py-3 text-text-muted font-medium text-xs">
                    {t('employees.columns.registration')}
                  </th>
                  <th className="text-left px-4 py-3 text-text-muted font-medium text-xs">
                    {t('employees.columns.department')}
                  </th>
                  <th className="text-left px-4 py-3 text-text-muted font-medium text-xs">
                    {t('employees.columns.role')}
                  </th>
                  <th className="text-left px-4 py-3 text-text-muted font-medium text-xs">
                    {t('employees.columns.linkedProfile')}
                  </th>
                  <th className="text-left px-4 py-3 text-text-muted font-medium text-xs">
                    {t('employees.columns.status')}
                  </th>
                  <th className="text-left px-4 py-3 text-text-muted font-medium text-xs">
                    {t('employees.columns.actions')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <EmployeeRow
                    key={emp.id}
                    employee={emp}
                    onEdit={(e) => {
                      setEditingEmployee(e)
                      setModalOpen(true)
                    }}
                    onDelete={(id) => {
                      setDeleteId(id)
                      setDeleteModalOpen(true)
                    }}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <ConfirmModal
        isOpen={deleteModalOpen}
        title={t('employees.deactivateConfirmTitle')}
        message={t('employees.deactivateConfirmGeneric')}
        confirmLabel={t('common.deactivate')}
        onConfirm={() => handleDelete(deleteId)}
        onCancel={() => setDeleteModalOpen(false)}
      />
    </Layout>
  )
}
