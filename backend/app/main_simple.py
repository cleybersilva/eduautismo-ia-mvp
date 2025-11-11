"""
EduAutismo IA - FastAPI Simple Test App
Versão minimalista para testes e validação de documentação
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(
    title="EduAutismo IA",
    description="API para educação e análise de comportamento",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial da API"""
    return """
    <html>
        <head>
            <title>EduAutismo IA - API</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                }
                h1 { color: #333; }
                a { color: #0066cc; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>🎓 EduAutismo IA - API</h1>
            <p>Bem-vindo à API do EduAutismo IA!</p>
            <ul>
                <li><a href="/docs">Documentação Swagger (/docs)</a></li>
                <li><a href="/redoc">Documentação ReDoc (/redoc)</a></li>
                <li><a href="/health">Status de Saúde (/health)</a></li>
            </ul>
        </body>
    </html>
    """


@app.get("/health", response_model=dict)
async def health():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "service": "EduAutismo IA",
        "version": "1.0.0",
    }


@app.get("/api/v1/students", response_model=dict)
async def list_students():
    """Lista de estudantes (stub para documentação)"""
    return {
        "students": [],
        "total": 0,
        "page": 1,
        "page_size": 10,
    }


@app.post("/api/v1/auth/login", response_model=dict)
async def login(username: str = "", password: str = ""):
    """Login stub para documentação"""
    return {
        "access_token": "test-token",
        "token_type": "bearer",
        "user": {"id": 1, "username": username},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
