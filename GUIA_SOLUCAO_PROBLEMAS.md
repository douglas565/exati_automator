# Guia de Solução de Problemas - Automação Exati

Este guia contém soluções para problemas comuns que podem ocorrer durante o uso da ferramenta de automação Exati.

## Problemas de Instalação

### Erro: "Import X could not be resolved"

**Problema:** Mensagens de erro indicando que módulos como `requests`, `selenium`, `pandas` ou `office365` não podem ser importados.

**Solução:** Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

Se o erro persistir para um módulo específico, instale-o diretamente:

```bash
pip install requests selenium pandas office365-rest-python-client
```

### Erro: "WebDriver not found"

**Problema:** O Selenium não consegue encontrar o ChromeDriver.

**Solução:** Instale o ChromeDriver:

```bash
# Para Windows (usando chocolatey)
choco install chromedriver

# Para Linux
apt-get install chromium-chromedriver

# Ou baixe manualmente de https://chromedriver.chromium.org/downloads
```

## Problemas de Conexão

### Erro: "Failed to connect to SharePoint"

**Problema:** A ferramenta não consegue se conectar ao SharePoint.

**Solução:**
1. Verifique se a URL do SharePoint está correta
2. Confirme suas credenciais de acesso
3. Verifique sua conexão com a internet
4. Se estiver usando VPN corporativa, certifique-se de que está conectado

### Erro: "Failed to login to Exati"

**Problema:** A ferramenta não consegue fazer login no Exati.

**Solução:**
1. Verifique se a URL do Exati está correta
2. Confirme seu nome de usuário e senha
3. Tente fazer login manualmente para verificar se suas credenciais estão funcionando

## Problemas de Execução

### Erro: "SyntaxError: Failed to execute 'json' on 'Response'"

**Problema:** Erro na comunicação entre o frontend e o backend.

**Solução:**
1. Reinicie a aplicação
2. Verifique se o servidor Flask está rodando corretamente
3. Limpe o cache do navegador e tente novamente

### Erro: "Imagem do ponto não disponível"

**Problema:** As imagens dos pontos não estão sendo exibidas.

**Solução:**
1. Verifique se o ponto realmente possui imagens no Exati
2. Tente navegar manualmente até o ponto no Exati para confirmar
3. Reinicie a aplicação e tente novamente

### Erro: "Nenhum ponto encontrado para o usuário"

**Problema:** A ferramenta não encontra pontos associados ao seu nome.

**Solução:**
1. Verifique se seu nome está escrito exatamente como aparece na coluna N da planilha
2. Confirme se existem pontos não verificados (coluna J vazia) associados ao seu nome
3. Verifique se a planilha está acessível e se você tem permissões de leitura

## Problemas de Desempenho

### Problema: "A automação está muito lenta"

**Solução:**
1. Feche outras aplicações que consomem muitos recursos
2. Verifique sua conexão com a internet
3. Se estiver processando muitos pontos, considere dividir o trabalho em sessões menores

## Contato para Suporte

Se você continuar enfrentando problemas após tentar as soluções acima, entre em contato com o suporte técnico:

- **Email:** suporte.ti@empresa.com
- **Ramal:** 1234
