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

solicitação: eu percebi que quando eu gero uma nova ordem de produção, aguardo a produção, quando produzem e colocam no magazine, uma etiqueta é colocada e para registrar a produção
os funcionários levam o magazine no ponto do PTH, que é o ponto 01 e estamos falando do setor pth, e bipam, marcam PRODUÇÃO E apertam registrar movimentação.

Mas o problema que não deveria ser possivel as pessoas biparem a mesma etiqueta marcando a mesma coisa no ponto de movimentação. Por exemplo: uma etiqueta, magazine de 50, levei
para bipar E marcar PRODUÇÃO, no ponto 01 do pth. mas se eu bipar de novo a mesma etiqueta e marcando a mesma coisa o sistema aceito. não pode acontecer isto. SOMENTE É PERMITIDO BIPAR
A MESMA ETIQUETA. QUANDO EU LEVAR O MAGAZINE PARA OUTRO SETOR. E LA NO OUTRO PONTO EU VOU BIPAR MARCANDO RECEBIMENTO. como resolver, eu vou mandar primeiro o app.py, mas nao quero me
responda de imediato, espere eu mandaro movimentar.html e dashboard.html. depoiis vc manda a resposta. 
















TEMOS QUE AJUSTAR A TELA DASHBOARD, VOU EXPLICAR DETALHADAMENTE. atualmente, um dos botões/filtros são:
AGUARDANDO, DISPONIVEL, EXPEDIDO, MOSTRAR TODOS.
AGORA VOU DIZER O QUE DEVERIA SER, MAS ANTES VAMOS RESALTAR QUE ISTO SE SEPARA ANTES PELO FILTRO DE SETORES: PTH, SMT, IM, PA, ESTOQUE, MOSRTRA TODOS. E PORTANTO, ISTO AGUARDANDO, DISPONIVEL, EXPEDIDO, MOSTRAR TODOS. VALE PARA CADA SETORES
NO ENTANTO, A ESTRUTURA CORRETA É:
SELECIONEI SETOR: PTH
AGUARDANDO PRODUÇÃO, PLACAS DISPONIVEIS, MOSTRAR TODOS.
ISTO VALE PARA PTH, SMT, IM, PA
QUANTO AO EXPEDIDO, ISTO VALE QUANDO EU SELECIONAR ESTOQUE, MAS QUANDO EU ESCOLHER ESTOQUE,
EXPEDIDO (SAIU PARA ENTREGA), EU AINDA NÃO TENHO UMA FORMA QUE CONFIRMAR QUE O MATERIAL FOI ENTREGUE, EU NAO FALO COM OS MOTORISTAS, VOU PENSAR NUM JEITO DEPOIS.DeprecationWarning

AGORA VOU EXPLICAR: PASSO A PASSO DA PRODUÇÃO PARA ENTENDERMOS O SISTEMA

GERAR UMA ORDEM DE PRODUÇÃO NO PTH, PARA GERAR AS ETIQUETAS, NESSE MOMENTO, O SISTEMA NO SETOR PTH, NA PARTE AGUARDANDO PRODUÇÃO VAI MARCAR A QUANTIDADE.
ASSIM QUE AS PLACAS FOREM PRODUZIDAS E COLOCADAS NO MAGAZINES VOU BIPAR NO Ponto-01 • PTH, E MARCAR PRODUÇÃO. NESSE MOMENTO, A QDT BIPADA E MARCADA VAI PARA PLACAS DISPONIVEIS, DO SETOR PTH, E
LEMBRAR QUE ABATER A MESMA QDT QUE TAVA NO AGUARDANDO PRODUCAO NO SETOR PTH. 
VOU LEVAR ESSE MAGAZINE DISPONIVEL PARA O SETOR SMT Ponto-02 • SMT, VOU BIPAR E MARCAR RECEBIMENTO. E ESSAS PLACAS VAO PARA AGUARDANDO PRODUÇÃO NO SETOR SMT. isto que ta confundindo o sistema, pq
as etiquetas eram do pth, eu recebi no smt e ainda vou produzir, mas preciso gerar novas etiquetas, no SETOR SMT, mas quando eu gerar as etiquetas, o sistema tbm já vai pensar em 
lançar a qdt no AGUARDANDO PRODUÇÃO DO SMT, a conta vai ficar errada ou precisamos entender o sistema, para nao confundir. É O MESMO MAGAZINE, COMO RECEBI NO OUTRO SETOR, VOU GERAR ETIQUETAS DO SMT.

DEPOIS, A LINHA DO SMT VAI PEGAR O MAGAZINE QUE CHEGOU E VAI PRODUZIR, TEM MODELOS QUE SAO BOTTOM E TOP E OUTROS SOMENTE TOP PARA FICAR REALMENTE PRONTO. DEVIDO A TER ESSE LANCE COM BOTTOM E TOP
TEMOS QUE AJUSTAR A INFORMACAO NA TELA ONDE MOSTRA OS DADOS EM DASHBOARD. ATUALMENTE:  Modelo	Código	Setor	Fase	Saldo, MAS ESSE FASE PODERIA SER STATUS, E SE COLOCASSEMOS
Modelo	Código	Setor	Fase Status	Saldo, e o fase seria BOTTOM ou top, EU CASO EU TENHO FEITO OS DOIS DAS MESMA PLACAS ENTAO BOTTOM E TOP. uma forma de vinculo faz total sentido

quando tiver feito essa prte de producao do smt. as PLACAS FICANDO, AGUARDANDO LIBERAÇÃO CQ. e depois o Ponto-03 • SMT (CQ) vai analisar o magazine e bipar CQ / LIBERAR, nesse momento, as placas
vao PLACAS DISPONIVEIS NO SETOR SMT,

depois alguem da IM OU PA PEGAR ESSE MAGAZINE PRONTO NO SMT. vai produzir, mas eles nao vao trocar a etiquetas do que tava no MAGAZINE QUE ERA DO SMT. primeiro, alguem no Ponto-04 ,
vai bipar RECEBIMENTO, e essas placas ficam AGUARDANDO PRODUÇÃO NO IM OU PA, como eles nao geram etiquetas no momento.mas eu acho até que deveriam. eu so vou saber que as placas estão PRONTAS, QUANDO O 
QUANDO O Ponto-05 • IM/PA (CQ) OU Ponto-06 • IM/PA (CQ) BIPAR A ETIQUETA E MARCAR CQ / LIBERAR, o que indica que as placas estão PLACAS DISPONIVEIS, DENTRO DO IM OU PA, DEPENDE DO SETOR, depois
o ultimo bipe vai ser do estoque quando marcar RECEBIMENTO. como o que eles fazem é sair pra entrega, SE BIPAR RECEBIMENTO no Ponto-07 • Estoque, eu vou pensar que saiu pra entrega. EU VOU TE MANDAR O 
MEU DASHBOARD.HTML. MAS IMAGINE QUE AJUSTE AINDA VOU SER FEITOS NO APP.PY, EU ACHO. VC ME AVISA. 






























EU PRECISO DE MAIS UM AJUSTE REFINADO NA PARTE DE DASHBOARD.HTML E NO GERAL, TALVEZ.
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

APESAR DO MEU APP.PY TER SIDO AJUSTADO COM ESSE PENSAMENTO, A TELA DE DAHSBOARD AINDA NAO É ASSIM. 