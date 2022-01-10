from Noticia import Noticia
import numpy
import tratamientoDatos as td
import TransformTFIDF as tfidf

# pasamos un texto para buscar noticias a partir de su similitud
def texto_coseno(texto:str, top:int):

    # leer matriz y convertirla a tf-idf FIXME
    matriz_txt = numpy.loadtxt("matriz.txt")
    matriz_tfidf = tfidf.matrixToTFIDF(matriz_txt) 

    # procesar texto y convertirlo a tf-idf
    texto_procesado = buscadorFrase(texto)
    texto_tfidf = tfidf.listToTFIDF(matriz_tfidf, texto_procesado)

    return documento_tfidf_origen_a_diccionario_con_resultados(texto_tfidf, matriz_tfidf, top)

    

#pasamos una noticia para buscar otras similares
def noticias_coseno(noticia:Noticia, top:int):

    # FIXME coger matriz en tf-idf
    matriz_txt = numpy.loadtxt("matriz.txt")
    matriz_tfidf = tfidf.matrixToTFIDF(matriz_txt)

    # coger la noticia y comprobar en qué index está de la lista de ficheros leidos
    index_noticia=None
    with open("ficherosLeidos.txt") as f:
        index_fila_leidos = 0
        for fila in f:
            if noticia.url == fila:
                index_noticia = index_fila_leidos
                break
            else:
                index_fila_leidos =+1

    if index_noticia == None:
        print("No se encuentra la noticia") # Salta en caso de error y sale de la función para no tener que recorrer el resto de bucles
        return

    # buscar el index en la matriz para recuperar la fila
    doc1 = None
    for i in range(len(matriz_tfidf)):
        if i == index_noticia:
            doc1 = matriz_tfidf[index_noticia]
            break
    
    if doc1 == None:
        print("Documento no encontrado en la matriz") # Salta en caso de error y sale de la función para no tener que recorrer el resto de bucles
        return

    # hacer el teorema del coseno para cada documento de la matriz
    return documento_tfidf_origen_a_diccionario_con_resultados(doc1, matriz_tfidf, top)
    

'''
    El propósito de esto es rellenar el diccionario de resultados con una pareja de clave-valor pasando
    un documento o texto de origen, que es una lista de valores tfidf, la matriz en tfidf y el top resultados
    Se hace el teorema del coseno con la lista de valores y la matriz, y se devuelve un diccionario de resultados
    La clave corresponde a la ruta de la noticia de la matriz, que se saca comprobando el número de fila de la matriz
    con el número de fila de un archivo que contiene los nombres de las filas de la matriz en orden (ficherosLeidos)
    El valor es el resultado del teorema del coseno en porcentajes
    '''
def documento_tfidf_origen_a_diccionario_con_resultados(doc_o_texto_origen_tfidf:list, matriz_tfidf, top:int):
    lista_ratings = {} # diccionario donde vamos a guardar la ruta de la noticia y su rating como parejas de clave valor

    # hacer el teorema del coseno con el texto para cada documento de la matriz
    index_fila_matriz = 0
    for doc in matriz_tfidf:
        ruta_noticia = ""

        # recuperar ruta de la noticia
        with open("ficherosLeidos.txt") as f:
            index_fila_leidos = 0
            for fila in f:
                if index_fila_matriz == index_fila_leidos:
                    ruta_noticia = fila
                    break
                else:
                    index_fila_leidos =+1
        
        # teorema del coseno
        resultado = coseno(doc_o_texto_origen_tfidf, doc)

        # Guardar noticia y la similitud en el diccionario
        lista_ratings[ruta_noticia] = resultado*100

    # Ordeno el diccionario por el valor del rating
    lista = sorted(lista_ratings.items(), key=lambda x: x[1], reverse=True)
    lista_ratings.clear()
    
    i = 0
    for key in lista:
        if i<top:
            lista_ratings[key[0]] = key[1]
            i = i+1
        else:
            break

    return lista_ratings

'''
Cálculos del teorema del coseno
'''
#Metodo para calcular la similitud en función del coseno
def coseno(doc1, doc2):
    lenDoc1 = len(doc1)
    lenDoc2 = len(doc2)
    #Comprobamos que ambas listas son del mismo tamaño
    if lenDoc1 != lenDoc2:
        difLen = lenDoc1 - lenDoc2
        for i in range(difLen):
            doc1 = numpy.append(doc1,0)

    numerador = 0
    cuadradosDoc1 = 0
    cuadradosDoc2 = 0

    for i in range(lenDoc1):
        numerador += (doc1[i] * doc2[i])
        cuadradosDoc1 += doc1[i]**2
        cuadradosDoc2 += doc2[i]**2
    raizDoc1 = cuadradosDoc1**(0.5)
    raizDoc2 = cuadradosDoc2**(0.5)
    denominador = raizDoc1 * raizDoc2
    return numerador/denominador

'''
Tratamiento básico de la frase para luego pasarla a tf-idf en el método principal del coseno
'''
def buscadorFrase(frase):
    #leo el diccionario
    diccionario = td.leerFicheros("diccionario.txt")

    tokens = td.tokenizacion(frase)
    tokens = td.tratamientoBasico(tokens)
    tokens = td.listaParada(tokens)
    tokens = td.lematizacion(tokens)
    #Creo una linea de ceros del tamaño del diccionario
    linea = numpy.zeros(len(diccionario),dtype=int)
    for token in tokens:
        if(token in diccionario):
            linea[diccionario.index(token)] +=1
        else:
            linea = numpy.append(linea,1)
            diccionario.append(token)
    return linea