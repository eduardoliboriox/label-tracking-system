eu quero ajustar algumas coisas no meu sistema, mas como o código é muito grande, vou mandar sempre o que eu quero descrito e parte do meu código e vc vai olhar minha estrutra e me dizer
se antes de fazer o ajuste vc precisa olhar outra parte do meu código, eu mando na hora. 

Sistema de Rastreabilidade via Etiquetas/
├─ static/
    └─ logo.png 
    └─ style.css  
  ├─ qrcodes/
       └─ da.png   
├─ templates/
    ├─ base.html
    ├─ dashboard.html    
    ├─ etiqueta_view.html
    ├─ form.html
    └─ history.html
    ├─ index.html
    ├─ label.html
    └─ movimentar.html
├─ app.py
├─ estrutura.txt
├─ models.db  
├─ README.md
├─ requirements.txt

assim está meu projeto.

solicitação: EU PRECISO DE MAIS UM AJUSTE REFINADO NA PARTE DE DASHBOARD.HTML E NO GERAL, TALVEZ.
                <option value="">-- Escolher Ponto --</option>
                <option value="Ponto-01">Ponto-01 • PTH </option>
                <option value="Ponto-02">Ponto-02 • SMT </option>
                <option value="Ponto-03">Ponto-03 • SMT (CQ)</option>
                <option value="Ponto-04">Ponto-04 • IM/PA </option>
                <option value="Ponto-05">Ponto-05 • IM/PA (CQ)</option>
                <option value="Ponto-06">Ponto-06 • IM/PA (CQ)</option>
                <option value="Ponto-07">Ponto-07 • Estoque</option>
Esses são os pontos pela empresa
A produção da empresa começa com o Ponto-01 • PTH, primeiro eles vão produzir, bipar produção. depois a placa vão pro SETOR SMT, onde algumas placas
possuem somente a fase top e após a montagem dos componentes estão prontas, mas muitos modelos são bottom e top, e somente quando a linha produzir as duas fases da mesma placa, quero dizer que primeiro fazem a parte de cima, depois eles fazem a parte de baixo, ai a placa ta realmente pronta, Ponto-02 • SMT, significa que produziram (mas ainda precisa saber se é um modelo so de top ou bottom e top), após a produção, as placas estão no status de AGUARDANDO LIBERAÇÃO DA QUALIDADE. ou seja elas estão esperando o Ponto-03 • SMT (CQ) bipar que já estão disponíveis (prontas) e liberadas no setor SMT.

os outros setores da empresa como IM, PA, vão pegar as placas prontas    no setor smt e levar pro setor deles para que colocados, montados outros componentes naquelas placas, e primeiro eles vao receber no Ponto-04 • IM/PA e depois ....vao marcar PRODUCAO, onde igual no setor smt, as placas vão ficar aguardando liberação da qualidade, mas dessa vez, quando estiver prontas, disponives, pode ser liberadas Ponto-05 • IM/PA (CQ) ou Ponto-06 • IM/PA (CQ), e assim que estiver pronto o pessoal do estoque (os motoristas de logística) vao pegar as placas, colocar no caminhão e antes de sair, vao bipar as etiquetas do material que vai sair pra entrega no cliente. no  Ponto-07 • Estoque, e com isto termina tudo.  agora eu preciso que o sistema tem esse raciocino e que a interface tem essas informações, sendo exibidas desse jeito.