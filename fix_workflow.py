import json
import uuid

# Load v2 file
input_path = r"c:\Users\diora\OneDrive\Documentos\Agente Financeiro\Jarvis_Finanzas_v2.json"
output_path = r"c:\Users\diora\OneDrive\Documentos\Agente Financeiro\Jarvis_Finanzas_v3.json"

with open(input_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Define the new node (Create Client)
new_node_id = str(uuid.uuid4())
new_node = {
    "parameters": {
        "tableId": "clientes",
        "fieldsUi": {
            "fieldValues": [
                {
                    "fieldId": "nome",
                    "fieldValue": "={{ $('WhatsApp Trigger').item.json.contacts[0].profile.name }}"
                },
                {
                    "fieldId": "telefone",
                    "fieldValue": "={{ $('WhatsApp Trigger').item.json.contacts[0].wa_id }}"
                }
            ]
        }
    },
    "type": "n8n-nodes-base.supabase",
    "typeVersion": 1,
    "position": [
        -2224, 
        616
    ],
    "id": new_node_id,
    "name": "Criar Cliente",
    "alwaysOutputData": True,
    "credentials": {
        "supabaseApi": {
            "id": "8NB4PaXlDfP5Wf1b",
            "name": "Supabase Carnes Española"
        }
    }
}

# Add new node to the list
workflow['nodes'].append(new_node)

# Update Connections
# 1. Update IF node to point to New Node instead of "Create a row" (Chat)
if_node_connection = workflow['connections']['If']['main'][1] # False path
# Find the connection to "Create a row"
for conn in if_node_connection:
    if conn['node'] == 'Create a row':
        conn['node'] = 'Criar Cliente'
        break

# 2. Add connection from New Node to "Create a row" (Chat)
workflow['connections']['Criar Cliente'] = {
    "main": [
        [
            {
                "node": "Create a row",
                "type": "main",
                "index": 0
            }
        ]
    ]
}

# Save v3
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print("Successfully created Jarvis_Finanzas_v3.json")
