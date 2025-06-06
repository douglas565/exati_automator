# Automação Exati - Verificação de Pontos (Versão 3.0)

Este projeto implementa uma interface web simplificada para automatizar o processo de verificação de pontos de serviço entre uma planilha do Excel no SharePoint e o sistema Exati.

## Novidades na Versão 3.0

- **Interface simplificada**: Apenas os campos essenciais são exibidos inicialmente
- **Detecção automática de usuários**: Botão para escanear e selecionar seu nome diretamente da planilha
- **Opções avançadas ocultas**: Configurações adicionais disponíveis apenas quando necessárias
- **Experiência mais rápida**: Fluxo otimizado para iniciar a automação com menos cliques

## Funcionalidades Gerais

- Suporte a múltiplas imagens por ponto com navegação intuitiva
- Filtragem automática apenas dos pontos associados ao usuário selecionado
- Processamento apenas dos pontos que ainda não foram verificados
- Automação de login e navegação no sistema Exati
- Verificação simplificada (OK ou potência corrigida)
- Log detalhado de atividades

## Como Usar

1. Preencha apenas os campos essenciais:
   - URL da Planilha (SharePoint)
   - URL do Exati
   - Usuário Exati
   - Senha Exati

2. Clique em "Escanear Usuários da Planilha"

3. Selecione seu nome na lista de usuários detectados

4. Clique em "Iniciar Automação"

5. Para cada ponto exibido:
   - Navegue entre as imagens usando os botões "Anterior" e "Próxima"
   - Verifique as imagens do ponto
   - Clique em "OK" se a luminária estiver conforme
   - Ou insira a potência corrigida e clique em "Confirmar Potência"

6. A automação avançará automaticamente para o próximo ponto associado ao seu usuário

## Requisitos

- Python 3.11+
- Flask
- Selenium
- Chrome WebDriver
- Pandas
- Office365-REST-Python-Client
- Requests

## Instalação

1. Extraia o arquivo zip
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```
   python src/main.py
   ```
4. Acesse a interface web em `http://localhost:8080`

## Observações

- Este é um protótipo e pode requerer ajustes para funcionar com a estrutura específica do Exati e da planilha do SharePoint
- A integração com o SharePoint requer configurações adicionais de autenticação em ambiente de produção
- Os seletores de elementos no Exati podem precisar de ajustes conforme a estrutura real da página
