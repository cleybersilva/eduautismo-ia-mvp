import { Link } from 'react-router-dom'

function HomePage() {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>🧩 EduAutismo IA</h1>
      <p>Plataforma Inteligente de Apoio Pedagógico para Alunos com TEA</p>
      <Link to="/dashboard">
        <button style={{ padding: '0.5rem 1rem', marginTop: '1rem' }}>
          Acessar Dashboard
        </button>
      </Link>
    </div>
  )
}

export default HomePage
