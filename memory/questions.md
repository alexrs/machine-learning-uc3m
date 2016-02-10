###¿Qué infomación se muestra en la interfaz? ¿Y en la terminal? ¿Cuál es la posición que ocupa incialmente?
###¿Qué datos podrían ser útiles para decidir lo que tiene que hacer Pac-Man en cada momento?

Posición y dirección de PacMan: si conocemos la posición actual de PacMan y la posición en la que se está moviendo, podremos decidir mejor a por qué fantasmas nos conviene ir. Por ejemplo, si PacMan se está moviendo hacia la derecha y uno de los fantasmas se mueve hacia la izquierda, PacMan llegará hasta él antes que hasta otro fantasma que esté a priori más cerca, pero se esté moviendo en la misma dirección.

###¿Cómo están definidos los mapas en estos ficheros?
###En el fichero games.py ¿Qué información ofrece este código sobre el estado del juego en cada turno? ¿Cuál crees que podría ser útil para decidir automáticamente qué tiene que hacer Pac-Man?
###Programa una función que imprima en un fichero toda la información del estado del Pac-Man. 

El objetivo de este apartado era crear una función que sacase a un archivo de texto inforamción relevante acerca del estado de la partida para que nuestro agente pueda aprender de estos datos en un futuro. El formato del archivo se corresponde con una línea por cada turno de la partida en la que los valores se encuentran separados por una coma.
Para abrir (o crear en el caso de que no exista) un archivo en Python y añadir nuevas líneas sin borrar las ya existentes, debemos hacerlo de la siguiente manera:
        f = open('filename', 'a+')

Los datos que obtenemos son:
- Fantasmas que están vivos: Se representan por booleanos, siendo True, que el fantasma que se encuentra en la posición i está vivo, y False, no. El primer dato se corresponde con un placeholder para PacMan cuyo valor será siempre False.
Distancia de PacMan a cada uno de los fantasmas: Esta distancia contendrá cierto ruido y no será del todo precisa.
- Puntuación de la partida: La puntuación de la partida en cada turno se obtiene por si el objetivo de la práctica es maximizar este valor.
- Posición de PacMan: Obtenemos la posición de PacMan para saber en qué lugar del mapa nos encontramos.
- Dirección de PacMan: La dirección de PacMan también se obtiene para saber hacia dónde nos estamos moviendo.
Además, los últimos datos recogidos se corresponden con 8 valores booleanos, los cuatro primeros indican si alguna de las celdas adyacentes a las que PacMan podría moverse se corresponden con un muro, y los otros cuatro, si alguna de estas cuatro celdas contiene comida.

###Implementa un comportamiento para el Pac-Man. Modificar la clase del agente GreedyBustersAgent, en bustersAgents.py. Pac-Man debe perseguir y comerse a los fantasmas.
###Qué ventajas puede tener el aprendizaje automático para controlar a Pac-Man?
