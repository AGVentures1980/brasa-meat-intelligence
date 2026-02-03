# BRASA Meat Intelligence™

Plataforma corporativa para controle de consumo de proteína via delivery (OLO),
com extração por IA, histórico em Postgres e forecast de compra semanal.

## Variáveis de Ambiente
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
STRICT_STORE_PIN=true
STORE_PINS=390=TDB390
DATABASE_URL=postgres://...

## Endpoints
/ → Login da Loja
/upload → API de upload (interno)
/report.csv → Relatório semanal/mensal
/forecast.csv → Compra sugerida (Forecast™)
