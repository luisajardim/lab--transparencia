# Reflexões — Lab 04: Transparência em Sistemas Distribuídos

**Aluno:** Luísa Oliveira Jardim  
**Data:** Março/2026

---

## Bloco de Reflexão Obrigatório

### 1. Síntese: Qual dos 7 tipos de transparência você considera mais difícil de implementar corretamente em um sistema real?

Pra mim, a **Transparência de Concorrência** foi a mais complicada de entender e implementar. Na Tarefa 6 eu vi que não dá pra usar um `threading.Lock()` normal quando temos processos separados — precisei usar um **lock distribuído no Redis** com o comando `SET NX EX`. O problema é que se um processo travar segurando o lock, os outros ficam esperando pra sempre (isso é um **deadlock**). A gente resolve isso com o TTL (tempo de expiração), mas aí surge outro problema: e se o TTL acabar antes da operação terminar? Outro processo pode pegar o lock e bagunçar tudo. Achei bem mais difícil que as outras transparências porque tem muitos casos de erro pra pensar.

---

### 2. Trade-offs: Descreva um cenário concreto em que esconder completamente a distribuição levaria a um sistema menos resiliente

Pensei no **Netflix** quando a gente tá assistindo um filme. Imagina se o app escondesse totalmente que depende da internet — quando a conexão ficasse ruim, o vídeo simplesmente travaria sem avisar nada. Só que o Netflix faz diferente: ele mostra aquela bolinha de carregamento, avisa quando a qualidade vai cair, e deixa a gente baixar o filme antes pra assistir offline. Isso é parecido com o **Circuit Breaker** que a gente viu na Tarefa 7 — o sistema "quebra" a transparência de propósito pra avisar o usuário que algo tá errado. É muito melhor do que o `anti_pattern.py` que simplesmente retorna `None` e deixa o código quebrar com `KeyError` depois.

---

### 3. Conexão com Labs anteriores: Como o conceito de `async/await` se conecta com a decisão de quebrar a transparência conscientemente?

O `async/await` é um jeito de deixar claro no código que aquela função pode demorar ou falhar. Quando eu escrevo `async def buscar_usuario()`, qualquer pessoa que ler o código já sabe que não é uma função instantânea — ela vai precisar esperar alguma coisa (tipo uma resposta da rede). O chamador é **obrigado** a usar `await`, então não tem como ignorar isso. É diferente do `anti_pattern.py` da Tarefa 7, onde a função `get_user()` parece uma coisa simples mas na verdade faz uma chamada de rede que pode dar timeout. O `async/await` força a gente a pensar nas falhas desde o início, em vez de fingir que a rede sempre funciona. Isso conecta com o Lab 02 porque lá a gente aprendeu que operações de I/O (rede, disco) são diferentes de cálculos normais.

---

### 4. GIL e multiprocessing: Explique por que a Tarefa 6 usa `multiprocessing` em vez de `threading`

A Tarefa 6 usa `multiprocessing` por causa do **GIL (Global Interpreter Lock)** do Python. O GIL é tipo uma trava que só deixa uma thread rodar código Python por vez dentro do mesmo processo. Então mesmo que você crie várias threads, elas ficam se revezando em vez de rodar ao mesmo tempo de verdade. Por causa disso, uma **race condition** com threads pode nem aparecer direito nos testes — às vezes funciona, às vezes não. Com `multiprocessing`, cada processo tem seu próprio Python rodando separado, então a race condition acontece de verdade, igual seria em um sistema distribuído real com vários servidores. Foi por isso que precisei usar o lock do Redis em vez de um `threading.Lock()` — o lock normal só funciona dentro de um processo, não entre processos diferentes.

---

### 5. Desafio técnico: Descreva uma dificuldade técnica encontrada durante o laboratório

O maior problema que tive foi no `com_concorrencia.py` da Tarefa 6. Quando rodei pela primeira vez, o código dava erro porque os dois processos tentavam pegar o **lock** ao mesmo tempo, e o segundo processo falhava na hora com `RuntimeError`. Demorei um pouco pra entender que o problema era que o código não tentava de novo — ele só desistia se o lock já tivesse ocupado. A solução foi criar um **mecanismo de retry**: o processo fica tentando pegar o lock várias vezes (com um pequeno delay entre as tentativas) até conseguir ou estourar um limite. Depois que fiz isso, o saldo final passou a dar R$500 certinho, provando que o lock distribuído tava funcionando. Foi legal porque vi na prática a diferença entre código com e sem controle de concorrência.

---

## Questões Bônus — Tarefa 7 (Transparência de Falha)

### Qual das oito falácias da computação distribuída o `anti_pattern.py` viola diretamente?

O `anti_pattern.py` viola a **primeira falácia de Peter Deutsch: "A rede é confiável"**. O código faz `get_user(user_id)` como se fosse uma função normal que sempre funciona, mas na real ela faz uma query num banco remoto. O problema é que a rede pode cair, o servidor pode demorar, pode dar timeout... e o código não trata nada disso. Ele só assume que vai receber um dicionário válido e já sai usando `user["name"]`. Quando a função retorna `None` (porque falhou), o código quebra com `KeyError` e ninguém entende o que aconteceu. É o tipo de bug chato de achar porque parece que o código tá certo, mas ele só funciona quando a rede tá perfeita.

### Por que `async/await` é uma forma deliberada de quebrar a transparência — e por que isso é a decisão correta?

O `async/await` quebra a transparência **de propósito** porque deixa óbvio que a função faz algo que pode demorar ou falhar. Quando vejo `async def fetch_user_remote()` já sei que: é assíncrono (pode pausar), é remoto (depende de rede), e o `Optional[dict]` no retorno me avisa que pode vir `None`. Isso me obriga a tratar o caso de erro com `if user:` antes de usar. É a decisão certa porque tentar esconder que o sistema é distribuído só cria problemas piores depois. O `bom_pattern.py` da Tarefa 7 mostra isso bem — o código é um pouco mais verboso, mas pelo menos não quebra silenciosamente. Como o Tanenbaum fala no livro, transparência total é uma ilusão — melhor aceitar que a rede falha e programar pensando nisso.

