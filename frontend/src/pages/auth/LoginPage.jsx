import { useState, useEffect } from "react";
import "./login.css";

export default function LoginPage() {
  const [highContrast, setHighContrast] = useState(false);
  const [fontSize, setFontSize] = useState("normal");
  const [showPassword, setShowPassword] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // Array com todas as imagens para o slideshow
  const heroImages = [
    "https://images.pexels.com/photos/8364026/pexels-photo-8364026.jpeg?auto=compress&cs=tinysrgb&w=1200", // Criança feliz na escola
    "https://images.pexels.com/photos/8612990/pexels-photo-8612990.jpeg?auto=compress&cs=tinysrgb&w=1200", // Blocos coloridos
    "https://images.pexels.com/photos/8613089/pexels-photo-8613089.jpeg?auto=compress&cs=tinysrgb&w=1200", // Criança concentrada
  ];

  // Efeito para trocar imagem automaticamente a cada 5 segundos
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) =>
        prevIndex === heroImages.length - 1 ? 0 : prevIndex + 1
      );
    }, 5000); // Troca a cada 5 segundos

    return () => clearInterval(interval);
  }, [heroImages.length]);

  const rootClasses = [
    "login-page",
    highContrast ? "login-page--high-contrast" : "",
    `login-page--font-${fontSize}`,
  ].join(" ");

  return (
    <div className={rootClasses}>
      <div className="login-layout">
        {/* ÁREA VISUAL / IMAGEM */}
        <div
          className="login-hero"
          style={{ backgroundImage: `url(${heroImages[currentImageIndex]})` }}
        >
          <div className="login-hero-overlay">
            <h1 className="login-hero-title">
              Aprendizagem inclusiva com tecnologia que entende você
            </h1>
            <p className="login-hero-subtitle">
              Plataforma pedagógica desenvolvida com carinho para alunos no
              espectro autista, famílias e profissionais da educação.
            </p>
          </div>
        </div>

        {/* CARD DE LOGIN */}
        <div className="login-panel-wrapper">
          <div className="login-panel">
            <div className="login-logo">
              <span className="login-logo-icon">💜</span>
              <div>
                <h2 className="login-logo-title">EduAutismo IA</h2>
                <p className="login-logo-subtitle">
                  Entre com segurança e tranquilidade
                </p>
              </div>
            </div>

            {/* Barra de acessibilidade */}
            <div className="login-accessibility">
              <button
                type="button"
                className={`acc-chip ${highContrast ? "acc-chip--active" : ""}`}
                onClick={() => setHighContrast((v) => !v)}
              >
                ⚪ Alto contraste
              </button>

              <div className="acc-font">
                <span>Texto:</span>
                <select
                  value={fontSize}
                  onChange={(e) => setFontSize(e.target.value)}
                >
                  <option value="small">Pequeno</option>
                  <option value="normal">Normal</option>
                  <option value="large">Grande</option>
                </select>
              </div>
            </div>

            <form className="login-form">
              <label className="login-field">
                <span className="login-field-label">E-mail</span>
                <div className="login-input-wrapper">
                  <span className="login-input-icon">📧</span>
                  <input
                    type="email"
                    placeholder="seuemail@exemplo.com"
                    required
                  />
                </div>
              </label>

              <label className="login-field">
                <span className="login-field-label">Senha</span>
                <div className="login-input-wrapper">
                  <span className="login-input-icon">🔒</span>
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Digite sua senha"
                    required
                  />
                  <button
                    type="button"
                    className="login-input-ghost"
                    onClick={() => setShowPassword((v) => !v)}
                  >
                    {showPassword ? "🙈" : "👁️"}
                  </button>
                </div>
              </label>

              <div className="login-links-row">
                <button type="button" className="login-link">
                  Esqueci minha senha
                </button>
              </div>

              <button type="submit" className="login-btn-primary">
                Entrar com segurança
              </button>

              <div className="login-divider">
                <span></span>
                <p>ou continue com</p>
                <span></span>
              </div>

              <div className="login-social">
                <button type="button" className="login-social-btn">
                  <span className="login-social-icon">G</span>
                  Google
                </button>
                <button type="button" className="login-social-btn">
                  <span className="login-social-icon"></span>
                  Apple
                </button>
              </div>

              <p className="login-footer-text">
                Não tem uma conta?{" "}
                <button type="button" className="login-link">
                  Criar conta gratuita
                </button>
              </p>
            </form>
          </div>

          <p className="login-bottom-quote">
            &ldquo;Tecnologia a serviço de uma educação mais humana, acessível e
            acolhedora para pessoas no espectro autista.&rdquo;
          </p>
        </div>
      </div>
    </div>
  );
}
