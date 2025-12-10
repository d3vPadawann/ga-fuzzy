# GA-Fuzzy: Carrinho Autônomo com Lógica Fuzzy e Algoritmo Genético

Este projeto implementa um **carrinho autônomo** que aprende a navegar em um circuito utilizando **Lógica Fuzzy** otimizada por **Algoritmo Genético (GA)**.

## Sobre o Projeto

O sistema simula um veículo equipado com **5 sensores de distância** que detectam obstáculos (paredes do circuito). Um controlador Fuzzy processa as leituras dos sensores e decide o ângulo de direção do carrinho.

O diferencial do projeto é que as **regras Fuzzy são evoluídas automaticamente** através de um Algoritmo Genético, eliminando a necessidade de definir manualmente as regras de navegação.

### Como Funciona

1. **Sensores**: O carrinho possui 5 sensores em ângulos diferentes (-45°, -22.5°, 0°, 22.5°, 45°) que medem a distância até as paredes
2. **Controlador Fuzzy**: Processa as leituras dos sensores usando conjuntos fuzzy e gera um comando de direção
3. **Algoritmo Genético**: Evolui as regras do sistema Fuzzy ao longo de gerações, maximizando a exploração do circuito

### Função de Fitness

O algoritmo otimiza:
-  **Exploração**: Recompensa por visitar novos setores do mapa
-  **Estabilidade**: Penaliza rotações excessivas
- ⏱ **Eficiência**: Considera o tempo de navegação

##  Requisitos

- Python 3.8+
- OpenCV
- NumPy
- PyGAD

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/d3vPadawann/ga-fuzzy.git
cd ga-fuzzy
```

2. Instale as dependências:
```bash
pip install opencv-python numpy pygad
```

## Como Executar

Execute o script principal:

```bash
python main.py
```

Durante a execução:
- Uma janela será aberta mostrando o treinamento em tempo real
- Cada geração exibe o melhor indivíduo navegando no circuito
- Pressione **Q** para interromper a simulação atual
- Ao final, um vídeo do melhor resultado é salvo automaticamente

## Estrutura do Projeto

```
├── main.py              # Código principal
├── circuit0.png         # Circuito de treinamento
├── circuit1.png         # Circuito alternativo
├── resultado_final.mp4  # Vídeo do melhor resultado
└── README.md
```

## Configurações

No início do arquivo `main.py`, você pode ajustar:

| Parâmetro | Descrição | Valor Padrão |
|-----------|-----------|--------------|
| `TRACK_IMAGE_PATH` | Imagem do circuito | `circuit0.png` |
| `NUM_SENSORS` | Quantidade de sensores | `5` |
| `NUM_RULES` | Número de regras Fuzzy | `10` |
| `num_generations` | Gerações do GA | `20` |

## Resultados

O algoritmo gera um vídeo `resultado_final.mp4` demonstrando o comportamento do melhor controlador Fuzzy evoluído.

## Licença

Este projeto foi desenvolvido para fins acadêmicos.

Este readme foi gerado com IA. :)
