# 🚀 Atualização: Agente Financeiro V5

Foi criado um novo arquivo de workflow (`agente_financeiro.json`) com **todas as funcionalidades** que você pediu!

## 1. Como Atualizar (Importante!)
Como o arquivo mudou muito, você precisa reimportar:
1.  No seu n8n, delete o workflow antigo.
2.  Vá em **Menu (canto superior direito) -> Import from File**.
3.  Selecione o arquivo `agente_financeiro.json` na pasta do projeto.
4.  **IMPORTANTE:** Abra os nós do WhatsApp ("Enviar Conselho", "Confirmar Transação", etc) e coloque suas credenciais de novo (Phone Number ID, etc), se necessário.

## 2. O que tem de novo?
Agora seu agente entende 4 modos:

### 🟢 1. Modo Transação (Melhorado)
Ele sabe diferenciar Gasto de Receita e não inventa mais categorias.
- "Gastei 20 mil" -> Saída / General
- "Recebi 500 mil" -> Entrada / Salário (se você disser)

### 🔵 2. Modo Orçamento (Novo!)
Você pode criar metas de gastos pelo Zap.
- **Diga:** "Definir orçamento de 800 mil para Comida"
- **O que acontece:** Ele cria (ou tenta atualizar) o limite dessa categoria no site.

### 🔴 3. Modo Deletar (Novo!)
Errou o último lançamento? Pode apagar.
- **Diga:** "Apagar último gasto", "Me equivoqué", "Deshacer"
- **O que acontece:** Ele busca a última transação do sistema e deleta ela.

### 🟡 4. Modo Análise (Consultor)
Continua igual, mas agora com dados mais precisos.
- "Como vou?", "Resumo", "Saldo".

## Teste agora!
Tente mandar:
> "Definir orçamento de 200 mil para Lazer"
> "Gastei 300 mil em Lazer" (Deve alertar que estourou!)
> "Apagar último gasto"
