# SK-AI-Net v1.0.1 clean

Autor: Mateus Arêas

Status: release candidate auditável para integração ao ecossistema MatVerse/Symbios.

## Finalidade

SK-AI-Net é uma stack Python auditável para triagem de risco de desinformação em redes sociais, com foco em integridade informacional eleitoral. O sistema não declara verdade definitiva, não acusa sujeitos e não automatiza sanção. Ele mede risco, lacunas probatórias, cadeia de custódia, sensibilidade eleitoral, coerência Ψ, CVaR e decisão Ω-Gate.

## Artefato validado

Nome do pacote: `sk-ai-net-production-v1.0.1-clean.zip`

SHA-256 do arquivo entregue nesta conversa:

```text
10c3c793cea8fbe1f2f8d155dd3a3c2daa3c23cae7f66b9bb6580e177e024f37
```

## Validações locais executadas

```text
python3 -m pytest -q                  PASS, 6 testes
python3 scripts/audit_package.py      PASS, 0 findings
python3 scripts/release_check.py      PASS, 0 findings
python3 scripts/package_release.py    PASS
grep marcador proibido                PASS, saída vazia
```

## Higiene de release

```text
PASS: árvore única do projeto
PASS: sem __pycache__
PASS: sem .pytest_cache
PASS: sem .pyc
PASS: sem ZIP aninhado
PASS: sem ledger/evidence runtime pré-gerados
PASS: sem credenciais hard-coded
PASS: sem assinatura de agente ou modelo
PASS: autoria declarada como Mateus Arêas
PASS: Docker image tag ajustada para 1.0.1
PASS: relatório de auditoria sem caminho absoluto local
```

## Componentes

```text
sk_ai_net/main.py        API FastAPI
sk_ai_net/gradio_app.py  UI Gradio local
sk_ai_net/risk.py        TACE Risk Engine
sk_ai_net/gate.py        Ω-Gate fail-closed
sk_ai_net/ledger.py      ledger JSONL + hash chain + Merkle root
sk_ai_net/service.py     orquestra análise, receipt, evidência e replay
```

## Execução local

```bash
python -m pip install -r requirements.txt
uvicorn sk_ai_net.main:app --host 0.0.0.0 --port 8000
```

UI:

```bash
python -m sk_ai_net.gradio_app
```

Docker:

```bash
docker compose up --build
```

## Limites constitucionais

SK-AI-Net é ferramenta de governança probatória. Não deve ser usada para censura automática, perfilamento político, identificação de culpados, microtargeting, repressão de grupos, ranqueamento de cidadãos ou declaração final de verdade. O uso correto é preservar evidência, medir risco, documentar lacunas, criar recibos, registrar ledger e escalar conteúdo sensível para revisão humana qualificada.

## Nota operacional

Configuração sensível deve permanecer fora do código versionado. Deploys devem usar o cofre nativo da plataforma de execução, nunca valores diretamente gravados em arquivos do repositório.
