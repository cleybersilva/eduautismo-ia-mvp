import { Link } from 'react-router-dom'

function DashboardPage() {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Dashboard</h1>
      <p>Bem-vindo ao painel de controle do EduAutismo IA</p>
      <Link to="/">
        <button style={{ padding: '0.5rem 1rem', marginTop: '1rem' }}>
          Voltar
        </button>
      </Link>
    </div>
  )
}

export default DashboardPage
