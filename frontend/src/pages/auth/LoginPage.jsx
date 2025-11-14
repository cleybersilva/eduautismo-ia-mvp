import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useNavigate, Link } from 'react-router-dom'
import { Mail, Lock, Eye, EyeOff, ShieldCheck, Info, HelpCircle } from 'lucide-react'

import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Card } from '../../components/ui/Card'
import { useAuthStore } from '../../store/authStore'

// Schema de validação com mensagens claras
const loginSchema = z.object({
  email: z
    .string({ required_error: 'Digite seu e-mail' })
    .email('Digite um e-mail válido (exemplo: professor@escola.com.br)'),
  password: z
    .string({ required_error: 'Digite sua senha' })
    .min(6, 'A senha precisa ter no mínimo 6 caracteres'),
  rememberMe: z.boolean().optional(),
})

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, isLoading, error, clearError, isAuthenticated } = useAuthStore()

  const [showPassword, setShowPassword] = useState(false)
  const [showHelp, setShowHelp] = useState(false)
  const [highContrast, setHighContrast] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
  } = useForm({
    resolver: zodResolver(loginSchema),
    mode: 'onChange',
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  })

  const watchEmail = watch('email')
  const watchRemember = watch('rememberMe')

  // Salvar e-mail no localStorage se marcou "Lembrar-me"
  useEffect(() => {
    if (typeof window === 'undefined') return
    if (watchRemember && watchEmail) {
      localStorage.setItem('eduautismo-remembered-email', watchEmail)
    } else {
      localStorage.removeItem('eduautismo-remembered-email')
    }
  }, [watchEmail, watchRemember])

  // Redirecionar se já estiver autenticado
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  // Limpar erros ao montar
  useEffect(() => {
    clearError()
  }, [clearError])

  const onSubmit = handleSubmit(async (data) => {
    try {
      await login(data.email, data.password)
      navigate('/dashboard')
    } catch (err) {
      console.error('Erro no login:', err)
    }
  })

  return (
    <div className="min-h-screen bg-red-500">
      <div className="flex min-h-screen bg-yellow-300">
        {/* Coluna Esquerda - Formulário de Login */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-4 sm:p-8">
          <Card className="w-full max-w-md">
            <div className="p-8 sm:p-10">
              {/* Cabeçalho */}
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-purple-500 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-300/50">
                    <ShieldCheck className="w-8 h-8 text-white" aria-hidden="true" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-slate-900">EduAutismo IA</h1>
                    <p className="text-sm text-slate-600">Plataforma de Apoio Pedagógico</p>
                  </div>
                </div>

                {/* Botões de Acessibilidade */}
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setHighContrast(!highContrast)}
                    className="p-2 rounded-xl hover:bg-slate-100 transition-colors"
                    aria-label={highContrast ? 'Desativar alto contraste' : 'Ativar alto contraste'}
                  >
                    <span className="text-xs font-medium text-slate-600">
                      {highContrast ? 'Padrão' : 'Alto Contraste'}
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setShowHelp(!showHelp)}
                    className="p-2 rounded-xl hover:bg-slate-100 transition-colors"
                    aria-label="Mostrar ajuda"
                    aria-expanded={showHelp}
                  >
                    <HelpCircle className="w-5 h-5 text-slate-600" aria-hidden="true" />
                  </button>
                </div>
              </div>

              {/* Painel de Ajuda */}
              {showHelp && (
                <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-2xl">
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" aria-hidden="true" />
                    <div className="text-sm text-slate-700 space-y-2">
                      <p className="font-semibold text-slate-900">Como fazer login:</p>
                      <ol className="list-decimal list-inside space-y-1">
                        <li>Digite seu e-mail cadastrado</li>
                        <li>Digite sua senha com calma</li>
                        <li>Clique em "Entrar com segurança"</li>
                      </ol>
                      <p className="text-xs text-slate-600 mt-3">
                        Esqueceu sua senha? Use o link "Esqueceu a senha?" abaixo.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Título do Formulário */}
              <div className="mb-8">
                <h2 className="text-3xl font-bold text-slate-900 mb-2">
                  Bem-vindo(a) de volta
                </h2>
                <p className="text-slate-600">
                  Entre com suas credenciais para acessar a plataforma
                </p>
              </div>

              {/* Mensagens de Erro */}
              {(error || errors.email || errors.password) && (
                <div
                  role="alert"
                  className="mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl"
                >
                  <p className="text-sm text-red-700 font-medium">
                    {error || errors.email?.message || errors.password?.message}
                  </p>
                </div>
              )}

              {/* Formulário */}
              <form onSubmit={onSubmit} className="space-y-6" noValidate>
                {/* Campo de E-mail */}
                <Input
                  id="email"
                  type="email"
                  label="E-mail"
                  icon={Mail}
                  placeholder="seu.email@escola.com.br"
                  error={errors.email?.message}
                  helpText="Use o e-mail cadastrado na plataforma"
                  disabled={isLoading}
                  {...register('email')}
                />

                {/* Campo de Senha */}
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    label="Senha"
                    icon={Lock}
                    placeholder="Digite sua senha"
                    error={errors.password?.message}
                    helpText="Mínimo 6 caracteres"
                    disabled={isLoading}
                    {...register('password')}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-[46px] p-2 rounded-lg hover:bg-slate-100 transition-colors"
                    aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                    aria-pressed={showPassword}
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5 text-slate-500" aria-hidden="true" />
                    ) : (
                      <Eye className="w-5 h-5 text-slate-500" aria-hidden="true" />
                    )}
                  </button>
                </div>

                {/* Lembrar-me e Esqueceu a senha */}
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      {...register('rememberMe')}
                      className="w-5 h-5 rounded border-slate-300 text-blue-500 focus:ring-4 focus:ring-blue-100"
                    />
                    <span className="text-sm font-medium text-slate-700">
                      Lembrar-me neste dispositivo
                    </span>
                  </label>

                  <Link
                    to="/forgot-password"
                    className="text-sm font-semibold text-blue-600 hover:text-blue-700 hover:underline focus:outline-none focus:ring-4 focus:ring-blue-100 rounded px-2 py-1"
                  >
                    Esqueceu a senha?
                  </Link>
                </div>

                {/* Botão de Envio */}
                <Button
                  type="submit"
                  disabled={!isValid || isLoading}
                  loading={isLoading}
                  className="w-full"
                  size="lg"
                >
                  {isLoading ? 'Entrando...' : 'Entrar com segurança'}
                </Button>
              </form>

              {/* Link para Criar Conta */}
              <div className="mt-8 pt-6 border-t border-slate-200">
                <p className="text-center text-sm text-slate-600">
                  Ainda não tem uma conta?{' '}
                  <Link
                    to="/signup"
                    className="font-semibold text-blue-600 hover:text-blue-700 hover:underline focus:outline-none focus:ring-4 focus:ring-blue-100 rounded px-2 py-1"
                  >
                    Criar conta gratuita
                  </Link>
                </p>
              </div>

              {/* Informações de Segurança */}
              <div className="mt-6 p-4 bg-slate-50 rounded-2xl">
                <div className="flex items-center gap-2 text-xs text-slate-600">
                  <ShieldCheck className="w-4 h-4 text-green-600" aria-hidden="true" />
                  <span>Conexão segura e criptografada • Compatível com leitores de tela</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Coluna Direita - Ilustração (apenas desktop) */}
        <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 relative overflow-hidden">
          {/* Decorações de fundo */}
          <div className="absolute inset-0">
            <div className="absolute top-20 left-20 w-64 h-64 bg-blue-200/30 rounded-full blur-3xl"></div>
            <div className="absolute bottom-20 right-20 w-80 h-80 bg-purple-200/30 rounded-full blur-3xl"></div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-200/20 rounded-full blur-3xl"></div>
          </div>

          {/* Conteúdo */}
          <div className="relative z-10 flex flex-col justify-center px-16 py-20">
            <div className="max-w-xl">
              <h2 className="text-4xl font-bold text-slate-900 mb-6">
                Educação Inclusiva com Inteligência Artificial
              </h2>
              <p className="text-lg text-slate-700 mb-8 leading-relaxed">
                Plataforma desenvolvida especialmente para professores da rede pública
                que trabalham com alunos do Transtorno do Espectro Autista (TEA).
              </p>

              {/* Ilustração SVG */}
              <div className="bg-white/60 backdrop-blur-sm rounded-3xl p-8 shadow-2xl shadow-slate-300/50">
                <svg
                  viewBox="0 0 400 300"
                  className="w-full h-auto"
                  role="img"
                  aria-labelledby="illustration-title"
                >
                  <title id="illustration-title">
                    Ilustração de professor e aluno trabalhando juntos
                  </title>

                  {/* Fundo */}
                  <rect x="0" y="0" width="400" height="300" fill="#f8f9fa" rx="20" />

                  {/* Elementos decorativos */}
                  <circle cx="80" cy="80" r="20" fill="#bae6fd" opacity="0.5" />
                  <circle cx="320" cy="100" r="25" fill="#ddd6fe" opacity="0.5" />
                  <circle cx="350" cy="250" r="15" fill="#fecaca" opacity="0.5" />

                  {/* Professor */}
                  <circle cx="130" cy="120" r="35" fill="#e9d5ff" />
                  <rect x="90" y="150" width="80" height="90" rx="25" fill="#bfdbfe" />

                  {/* Aluno */}
                  <circle cx="270" cy="130" r="38" fill="#bbf7d0" />
                  <rect x="230" y="165" width="85" height="95" rx="28" fill="#fde68a" />

                  {/* Mesa/Livro */}
                  <rect x="150" y="240" width="100" height="10" rx="5" fill="#cbd5e1" />
                  <rect x="160" y="220" width="80" height="20" rx="3" fill="#e2e8f0" />

                  {/* Símbolos de comunicação */}
                  <circle cx="200" cy="100" r="8" fill="#60a5fa" />
                  <circle cx="220" cy="90" r="6" fill="#a78bfa" />
                  <circle cx="180" cy="95" r="7" fill="#f472b6" />
                </svg>
              </div>

              {/* Destaques */}
              <div className="mt-8 space-y-3">
                {[
                  'Interface amigável e previsível',
                  'Atividades personalizadas com IA',
                  'Adaptação ao perfil de cada aluno',
                  'Recursos de acessibilidade integrados',
                ].map((feature, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-green-400 rounded-full flex items-center justify-center flex-shrink-0">
                      <svg
                        className="w-4 h-4 text-white"
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="3"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                    <span className="text-slate-700 font-medium">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
