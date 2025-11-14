import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  FileText,
  ClipboardList,
  Settings,
  LogOut,
  GraduationCap,
  Brain,
  Sparkles
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { clsx } from 'clsx'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Alunos', href: '/students', icon: Users },
  { name: 'Atividades', href: '/activities', icon: FileText },
  { name: 'Avaliações', href: '/assessments', icon: ClipboardList },
  { name: 'Configurações', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()

  return (
    <div className="flex flex-col h-full bg-white/95 backdrop-blur-sm border-r border-slate-200/50 shadow-xl">
      {/* Logo */}
      <div className="px-6 py-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="relative">
            <div className="w-12 h-12 bg-gradient-to-br from-[#b7d8ff] to-[#e6e8ff] rounded-2xl flex items-center justify-center shadow-lg shadow-blue-200/50">
              <GraduationCap className="w-7 h-7 text-[#4f70c8]" />
            </div>
            <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-br from-[#6c8af5] to-[#8aa9ff] rounded-full flex items-center justify-center shadow-md">
              <Brain className="w-3.5 h-3.5 text-white" />
            </div>
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold font-display text-slate-900">EduAutismo IA</h1>
            <p className="text-xs text-slate-500 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              Powered by AI
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 space-y-1.5 overflow-y-auto">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-4 py-3.5 rounded-2xl text-sm font-semibold transition-all duration-200',
                isActive
                  ? 'bg-gradient-to-r from-[#b7d8ff] to-[#d4e4ff] text-[#4f70c8] shadow-md shadow-blue-200/50'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              )
            }
          >
            {({ isActive }) => (
              <>
                <div className={clsx(
                  'p-2 rounded-xl transition-colors',
                  isActive ? 'bg-white/60' : 'bg-slate-100'
                )}>
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                </div>
                {item.name}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User Profile */}
      <div className="p-4 border-t border-slate-200/50">
        <div className="flex items-center gap-3 px-4 py-3.5 rounded-2xl bg-gradient-to-br from-slate-50 to-blue-50/30">
          <div className="w-11 h-11 bg-gradient-to-br from-[#6c8af5] to-[#8aa9ff] rounded-full flex items-center justify-center shadow-md">
            <span className="text-sm font-bold text-white">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-slate-900 truncate">
              {user?.name || 'Usuário'}
            </p>
            <p className="text-xs text-slate-500 truncate">
              {user?.email || 'email@example.com'}
            </p>
          </div>
        </div>

        <button
          onClick={logout}
          className="w-full mt-3 flex items-center gap-3 px-4 py-3.5 rounded-2xl text-sm font-semibold text-slate-600 hover:bg-red-50 hover:text-red-600 transition-all duration-200 group"
        >
          <div className="p-2 rounded-xl bg-slate-100 group-hover:bg-red-100 transition-colors">
            <LogOut className="w-5 h-5" />
          </div>
          Sair
        </button>
      </div>
    </div>
  )
}
