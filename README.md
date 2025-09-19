---

# Wazuh Teams Integration

Integração do **Wazuh** com **Microsoft Teams**, permitindo que alertas do Wazuh sejam enviados diretamente para um canal do Teams via webhook.

---

## 1. Configuração do Webhook no Teams

1. Acesse o canal do Teams onde deseja receber os alertas.
2. Adicione um **Webhook Connector**.
3. Copie a URL gerada, que será utilizada no script de integração.

---

## 2. Testando o Webhook

Edite o arquivo `run.sh`:

```bash
webhookUrl="COLE_AQUI_SUA_URL_DO_TEAMS"
```

Em seguida, execute o script para validar se os testes de envio funcionam corretamente.

---

## 3. Script de Alerta

Copie os arquivos para o diretório de integrações do Wazuh:

```bash
cp custom-teams /var/ossec/integrations/
cp custom-teams.py /var/ossec/integrations/
```

Ajuste permissões e propriedade:

```bash
chmod 750 /var/ossec/integrations/custom-teams
chown root:wazuh /var/ossec/integrations/custom-teams

chmod 750 /var/ossec/integrations/custom-teams.py
chown root:wazuh /var/ossec/integrations/custom-teams.py
```

---

## 4. Configuração no `ossec.conf`

Adicione o bloco de integração no arquivo `ossec.conf`:

```xml
<integration>
    <name>custom-teams</name>
    <level>3</level>
    <hook_url>WEBHOOK_URL</hook_url>
    <format>json</format>
</integration>
```

**Observações importantes:**

| Item                  | Detalhe                                                    |
| --------------------- | ---------------------------------------------------------- |
| Nome da integração    | Deve começar com `custom-`, caso contrário será rejeitada. |
| Níveis                | Pode ser configurado para alertas específicos.             |
| Múltiplas integrações | É possível adicionar mais de um bloco no `ossec.conf`.     |

> Salve a configuração e reinicie o Wazuh Manager usando o botão **Restart Manager**.

---

## 5. Verificação

* Gere um alerta no Wazuh.
* Verifique se o alerta aparece corretamente no canal do Teams.

---

## 6. Troubleshooting

Use os logs para diagnosticar problemas:

```text
/var/ossec/logs/ossec.log
/var/ossec/logs/microsoft-teams.log
```

* `ossec.log`: erros do Wazuh.
* `microsoft-teams.log`: detalhes do envio para o Teams, útil para debug.

---

## 7. Personalização Avançada

* Edite o arquivo `custom-teams.py` para customizar o **layout do card do Teams**.
* Utilize o **[Adaptive Card Designer](https://adaptivecards.io/designer/)** para facilitar a criação de cards.
* Sempre siga a formatação correta no script para evitar erros.

**Exemplo de customização:**

```python
payload = {
    "type": "message",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "contentUrl": "",
            "content": {
                "type": "AdaptiveCard",
                "body": [
                    {"type": "TextBlock", "text": "Custom Alert", "weight": "Bolder", "size": "Large"},
                    {"type": "TextBlock", "text": alert["rule"]["description"], "wrap": True},
                    {"type": "FactSet", "facts": [
                        {"title": "Alert ID", "value": alert["id"]},
                        {"title": "Agent Name", "value": alert["agent"]["name"]},
                        {"title": "Timestamp", "value": formatted_timestamp}
                    ]}
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.5"
            }
        }
    ]
}
```

---

Se você quiser, posso ainda **adicionar uma seção com screenshots e fluxograma do fluxo do alerta do Wazuh até o Teams**, deixando o README ainda mais visual e amigável.

Quer que eu faça isso também?
