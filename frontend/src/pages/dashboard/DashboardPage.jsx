import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Users,
  FileText,
  ClipboardCheck,
  TrendingUp,
  Plus,
  Calendar,
  Brain,
  Activity,
  Sparkles,
  ArrowUpRight
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { useAuthStore } from '../../store/authStore'

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState({
    totalStudents: 0,
    totalActivities: 0,
    totalAssessments: 0,
    activitiesThisWeek: 0,
  })

  useEffect(() => {
    setStats({
      totalStudents: 12,
      totalActivities: 45,
      totalAssessments: 28,
      activitiesThisWeek: 8,
    })
  }, [])

  const statCards = [
    {
      title: 'Total de Alunos',
      value: stats.totalStudents,
      icon: Users,
      gradient: 'from-blue-400 to-blue-600',
      bgGradient: 'from-blue-50 to-blue-100/50',
      href: '/students',
    },
    {
      title: 'Atividades Criadas',
      value: stats.totalActivities,
      icon: FileText,
      gradient: 'from-emerald-400 to-emerald-600',
      bgGradient: 'from-emerald-50 to-emerald-100/50',
      href: '/activities',
    },
    {
      title: 'Avaliações Realizadas',
      value: stats.totalAssessments,
      icon: ClipboardCheck,
      gradient: 'from-purple-400 to-purple-600',
      bgGradient: 'from-purple-50 to-purple-100/50',
      href: '/assessments',
    },
    {
      title: 'Esta Semana',
      value: stats.activitiesThisWeek,
      icon: TrendingUp,
      gradient: 'from-orange-400 to-orange-600',
      bgGradient: 'from-orange-50 to-orange-100/50',
      href: '/activities',
    },
  ]

  const recentActivities = [
    {
      id: 1,
      student: 'Aluno A',
      activity: 'Matemática - Adição',
      date: '2025-01-12',
      status: 'Concluída',
    },
    {
      id: 2,
      student: 'Aluno B',
      activity: 'Português - Leitura',
      date: '2025-01-12',
      status: 'Em andamento',
    },
    {
      id: 3,
      student: 'Aluno C',
      activity: 'Ciências - Animais',
      date: '2025-01-11',
      status: 'Concluída',
    },
  ]

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-4xl font-bold font-display bg-gradient-to-r from-slate-900 via-blue-900 to-purple-900 bg-clip-text text-transparent">
              Dashboard
            </h1>
            <Sparkles className="w-7 h-7 text-yellow-500 animate-pulse" />
          </div>
          <p className="mt-3 text-lg text-slate-600">
            Bem-vindo(a), <span className="font-semibold text-slate-900">{user?.name || 'Professor(a)'}</span>!
          </p>
        </div>
        <div className="flex gap-3">
          <Link to="/activities/new">
            <Button className="flex items-center gap-2 h-12 px-6 bg-gradient-to-r from-[#6c8af5] to-[#8aa9ff] hover:from-[#5a78e3] hover:to-[#7897ed] text-white shadow-lg shadow-blue-300/50 rounded-2xl font-semibold transition-all">
              <Plus className="w-5 h-5" />
              Nova Atividade
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Link key={index} to={stat.href}>
            <Card className="hover:shadow-2xl transition-all duration-300 cursor-pointer group border-0 backdrop-blur-sm overflow-hidden relative bg-white">
              <div className={`absolute inset-0 bg-gradient-to-br ${stat.bgGradient} opacity-100`}></div>
              <CardContent className="pt-6 pb-6 relative z-10">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-slate-600 uppercase tracking-wide">{stat.title}</p>
                    <p className="text-4xl font-bold text-slate-900 mt-3">{stat.value}</p>
                  </div>
                  <div className={`bg-gradient-to-br ${stat.gradient} p-4 rounded-2xl shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all duration-300`}>
                    <stat.icon className="w-7 h-7 text-white" />
                  </div>
                </div>
                <div className="mt-4 flex items-center gap-2 text-sm font-medium text-slate-700 group-hover:text-slate-900 transition-colors">
                  Ver detalhes
                  <ArrowUpRight className="w-4 h-4 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                </div>
              </CardContent>
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/20 rounded-full -mr-16 -mt-16"></div>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activities */}
        <Card className="lg:col-span-2 border-0 shadow-xl bg-white/80 backdrop-blur-sm">
          <CardHeader className="border-b border-slate-100">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl font-bold text-slate-900">Atividades Recentes</CardTitle>
                <CardDescription className="text-slate-600 mt-1">Últimas atividades dos seus alunos</CardDescription>
              </div>
              <div className="p-3 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl">
                <Activity className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-3">
              {recentActivities.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center justify-between p-5 bg-gradient-to-r from-slate-50 to-blue-50/30 rounded-2xl hover:shadow-md hover:from-slate-100 hover:to-blue-100/40 transition-all duration-200 border border-slate-100"
                >
                  <div className="flex-1">
                    <p className="font-semibold text-slate-900 text-base">{activity.activity}</p>
                    <p className="text-sm text-slate-600 mt-1 flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      {activity.student}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-slate-500 font-medium">{activity.date}</p>
                    <span
                      className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold mt-2 ${
                        activity.status === 'Concluída'
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                          : 'bg-amber-100 text-amber-800 border border-amber-200'
                      }`}
                    >
                      {activity.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6 text-center">
              <Link to="/activities">
                <Button variant="outline" className="w-full h-12 rounded-2xl border-2 border-slate-200 hover:border-blue-300 hover:bg-blue-50 font-semibold text-slate-700 hover:text-blue-700 transition-all">
                  Ver Todas as Atividades
                  <ArrowUpRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm">
          <CardHeader className="border-b border-slate-100">
            <CardTitle className="text-2xl font-bold text-slate-900">Ações Rápidas</CardTitle>
            <CardDescription className="text-slate-600 mt-1">Acesse rapidamente</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 pt-6">
            <Link to="/students/new">
              <Button variant="outline" className="w-full justify-start h-14 rounded-2xl border-2 border-slate-200 hover:border-blue-300 hover:bg-blue-50 font-semibold text-slate-700 hover:text-blue-700 transition-all group">
                <div className="p-2 bg-blue-100 rounded-xl mr-3 group-hover:bg-blue-200 transition-colors">
                  <Users className="w-5 h-5 text-blue-600" />
                </div>
                Cadastrar Aluno
              </Button>
            </Link>
            <Link to="/activities/generate">
              <Button variant="outline" className="w-full justify-start h-14 rounded-2xl border-2 border-slate-200 hover:border-purple-300 hover:bg-purple-50 font-semibold text-slate-700 hover:text-purple-700 transition-all group">
                <div className="p-2 bg-purple-100 rounded-xl mr-3 group-hover:bg-purple-200 transition-colors">
                  <Brain className="w-5 h-5 text-purple-600" />
                </div>
                Gerar com IA
              </Button>
            </Link>
            <Link to="/assessments/new">
              <Button variant="outline" className="w-full justify-start h-14 rounded-2xl border-2 border-slate-200 hover:border-emerald-300 hover:bg-emerald-50 font-semibold text-slate-700 hover:text-emerald-700 transition-all group">
                <div className="p-2 bg-emerald-100 rounded-xl mr-3 group-hover:bg-emerald-200 transition-colors">
                  <ClipboardCheck className="w-5 h-5 text-emerald-600" />
                </div>
                Nova Avaliação
              </Button>
            </Link>
            <Link to="/calendar">
              <Button variant="outline" className="w-full justify-start h-14 rounded-2xl border-2 border-slate-200 hover:border-orange-300 hover:bg-orange-50 font-semibold text-slate-700 hover:text-orange-700 transition-all group">
                <div className="p-2 bg-orange-100 rounded-xl mr-3 group-hover:bg-orange-200 transition-colors">
                  <Calendar className="w-5 h-5 text-orange-600" />
                </div>
                Ver Calendário
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Tips Card */}
      <Card className="border-0 shadow-2xl bg-gradient-to-br from-purple-50 via-blue-50 to-cyan-50 overflow-hidden relative">
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-purple-200/30 to-blue-200/30 rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-cyan-200/30 to-blue-200/30 rounded-full -ml-24 -mb-24"></div>
        <CardContent className="pt-8 pb-8 relative z-10">
          <div className="flex items-start gap-6">
            <div className="p-4 bg-gradient-to-br from-purple-500 to-blue-600 rounded-2xl shadow-2xl shadow-purple-300/50">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <h3 className="text-2xl font-bold text-slate-900">
                  Dica: Use a IA para Personalizar
                </h3>
                <Sparkles className="w-6 h-6 text-yellow-500" />
              </div>
              <p className="text-slate-700 text-base leading-relaxed">
                Nossa IA analisa o <span className="font-semibold text-purple-700">perfil cognitivo e sensorial</span> de cada aluno para criar
                atividades verdadeiramente personalizadas. Experimente gerar uma nova
                atividade e veja a diferença!
              </p>
              <Link to="/activities/generate">
                <Button className="mt-5 h-12 px-6 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg shadow-purple-300/50 rounded-2xl font-semibold transition-all">
                  <Brain className="w-5 h-5 mr-2" />
                  Experimentar Agora
                  <Sparkles className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
