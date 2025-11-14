import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Search, Filter, UserPlus, Users, Sparkles, FileText, ArrowUpRight } from 'lucide-react'
import { Card, CardContent } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'

export default function StudentsPage() {
  const [searchTerm, setSearchTerm] = useState('')

  const students = [
    {
      id: 1,
      code: 'ALU-001',
      age: 10,
      grade: '5º Ano',
      diagnosis: 'Autismo Leve',
      activitiesCount: 15,
    },
    {
      id: 2,
      code: 'ALU-002',
      age: 8,
      grade: '3º Ano',
      diagnosis: 'Autismo Moderado',
      activitiesCount: 12,
    },
    {
      id: 3,
      code: 'ALU-003',
      age: 12,
      grade: '7º Ano',
      diagnosis: 'Autismo Leve',
      activitiesCount: 20,
    },
  ]

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-4xl font-bold font-display bg-gradient-to-r from-slate-900 via-blue-900 to-purple-900 bg-clip-text text-transparent">
              Alunos
            </h1>
            <Users className="w-8 h-8 text-blue-600" />
          </div>
          <p className="mt-3 text-lg text-slate-600">
            Gerencie os perfis dos seus alunos com TEA
          </p>
        </div>
        <Link to="/students/new">
          <Button className="flex items-center gap-2 h-12 px-6 bg-gradient-to-r from-[#6c8af5] to-[#8aa9ff] hover:from-[#5a78e3] hover:to-[#7897ed] text-white shadow-lg shadow-blue-300/50 rounded-2xl font-semibold transition-all">
            <UserPlus className="w-5 h-5" />
            Novo Aluno
          </Button>
        </Link>
      </div>

      {/* Search and Filter */}
      <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm">
        <CardContent className="pt-6 pb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Buscar alunos por código..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-12 h-12 rounded-2xl border-2 border-slate-200 focus:border-blue-400 bg-slate-50"
              />
            </div>
            <Button variant="outline" className="flex items-center gap-2 h-12 px-6 rounded-2xl border-2 border-slate-200 hover:border-blue-300 hover:bg-blue-50 font-semibold text-slate-700 hover:text-blue-700 transition-all">
              <Filter className="w-5 h-5" />
              Filtros
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Students Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {students.map((student) => (
          <Link key={student.id} to={`/students/${student.id}`}>
            <Card className="hover:shadow-2xl hover:shadow-blue-200/30 transition-all duration-300 cursor-pointer group border-0 bg-gradient-to-br from-white to-blue-50/20 backdrop-blur-sm overflow-hidden relative">
              <div className="absolute top-0 right-0 w-32 h-32 bg-blue-200/20 rounded-full -mr-16 -mt-16"></div>
              <CardContent className="pt-6 pb-6 relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-300/50 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                    {student.code.split('-')[1]}
                  </div>
                  <span className="px-3 py-1.5 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 rounded-full text-xs font-semibold border border-blue-200">
                    {student.diagnosis}
                  </span>
                </div>

                <h3 className="text-xl font-bold text-slate-900 mb-4">
                  Código: {student.code}
                </h3>

                <div className="space-y-3 text-sm">
                  <div className="flex justify-between p-3 bg-slate-50 rounded-xl">
                    <span className="text-slate-600 font-medium">Idade:</span>
                    <span className="font-bold text-slate-900">{student.age} anos</span>
                  </div>
                  <div className="flex justify-between p-3 bg-slate-50 rounded-xl">
                    <span className="text-slate-600 font-medium">Série:</span>
                    <span className="font-bold text-slate-900">{student.grade}</span>
                  </div>
                  <div className="flex justify-between p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl">
                    <span className="text-slate-600 font-medium flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      Atividades:
                    </span>
                    <span className="font-bold text-blue-700">
                      {student.activitiesCount}
                    </span>
                  </div>
                </div>

                <div className="mt-5 pt-5 border-t border-slate-200">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full h-11 rounded-2xl border-2 border-slate-200 group-hover:border-blue-400 group-hover:bg-gradient-to-r group-hover:from-blue-500 group-hover:to-purple-600 group-hover:text-white font-semibold transition-all duration-300 flex items-center justify-center gap-2"
                  >
                    Ver Perfil Completo
                    <ArrowUpRight className="w-4 h-4 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}

        {/* Add Student Card */}
        <Link to="/students/new">
          <Card className="border-3 border-dashed border-slate-300 hover:border-blue-400 hover:shadow-2xl hover:shadow-blue-200/30 transition-all duration-300 cursor-pointer group bg-gradient-to-br from-slate-50 to-blue-50/30 backdrop-blur-sm overflow-hidden relative">
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-200/10 rounded-full -mr-16 -mt-16"></div>
            <CardContent className="pt-6 h-full flex flex-col items-center justify-center text-center py-16 relative z-10">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg shadow-blue-200/50">
                <Plus className="w-10 h-10 text-blue-600 group-hover:text-purple-600 transition-colors" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">
                Adicionar Novo Aluno
              </h3>
              <p className="text-sm text-slate-600 max-w-[200px]">
                Cadastre um novo aluno com TEA na plataforma
              </p>
              <div className="mt-5 flex items-center gap-2 text-sm font-semibold text-blue-600 group-hover:text-purple-600 transition-colors">
                <Sparkles className="w-4 h-4" />
                Começar agora
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  )
}
