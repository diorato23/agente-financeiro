# 🧪 Guia de Teste: Agente Financeiro

Use estes exemplos para testar seu agente no WhatsApp. Copie e cole as mensagens para ver como ele reage.

## 1. Registrar Gastos (Despesas)
O agente deve identificar valor, categoria e descrição.

| Cenário | Mensagem para enviar | O que deve acontecer |
| :--- | :--- | :--- |
| **Gasto Simples** | "Gastei 15 mil em taxi" | Salva 15.000 em *Transporte* |
| **Gasto com Detalhe** | "Comprei um tenis por 250000" | Salva 250.000 em *Compras/Vestuário* |
| **Pagamento** | "Paguei o aluguel 800000" | Salva 800.000 em *Moradia* |
| **Gíria / Natural** | "Me fui de rumba y se me fueron 120 mil" | Salva 120.000 em *Lazer/Entretenimento* |

**Resposta Esperada:**
> ✅ *Guardado!*
> 📝 [descrição]
> 💰 $[valor]

---

## 2. Registrar Entradas (Renda)
O agente deve identificar que é dinheiro entrando.

| Cenário | Mensagem para enviar | O que deve acontecer |
| :--- | :--- | :--- |
| **Salário** | "Recebi meu salário de 3 milhões" | Salva 3.000.000 como *Receita* |
| **Extra** | "Fiz um freela e ganhei 200 mil" | Salva 200.000 como *Renda Extra* |

---

## 3. Pedir Análise e Conselhos
O agente deve ler seu banco de dados e responder com a persona "Amigo Financeiro" (gírias colombianas).

| Cenário | Mensagem para enviar | O que deve acontecer |
| :--- | :--- | :--- |
| **Resumo Geral** | "Como vou?" | Mostra saldo, receitas vs despesas |
| **Saldo** | "Quanto saldo me queda?" | Mostra o saldo atual |
| **Conselho** | "Dame un consejo parcero" | Analisa gastos e dá uma dica |
| **Alerta** | "Resumen" | Se alguma categoria passou de 80%, mostra ⚠️ |

**Resposta Esperada (Exemplo):**
> Hola parcero! 👋
> 💰 Saldo Total: $1.200.000
> 📉 Gastos del mes: $450.000
>
> ⚠️ *Pilas!* Ya te gastaste el 90% en Alimentación.
>
> 💡 *Consejo:* Bájale a los domicilios esta semana.

---

## 4. Testes de Erro (Opcional)
Tente confundir o agente para ver se ele é robusto.

*   "O céu é azul" -> *Ele provavelmente não vai salvar nada ou vai pedir para você repetir.*
*   "Gastei mil" (sem número) -> *Pode falhar se não entender "mil" como 1000.*

---

### 💡 Dica para seu amigo
Quando seu amigo for testar, peça para ele começar cadastrando um orçamento no site (Dashboard) primeiro, assim os alertas (⚠️) vão funcionar na hora no WhatsApp!
