##Author: Bruno Miranda de Souza
##Application for electronic boards elements recognition and comparison to a template board for four different board models 

##bibliotecas
import cv2
try:

    from PIL import Image
except ImportError:
    import Image
    
import pytesseract
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
import math # importando a biblioteca math para cálculos mateáticos

#funções
##thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#definindo uma função de seleção das placas de comparação
            #placaComp = placaCorrigida   placaEnt = duplicate
def apontarGabarito(placaComp, placaEnt, b, g, r):
    if placaComp == "AB01":
        ele1 = ((86,41), (49,81), (127,81), (86,124))
        ele2 = ((397,170), (262,212), (397,245), (546,212))
        localizarElemento(ele1, ele2, placaEnt, b, g, r)
    elif  placaComp == "AB02":
        ele1 = ((89,106), (54,147), (86,186), (129,144))
        ele2 = ((400,108), (258,144), (399,184), (542,142))
        localizarElemento(ele1, ele2, placaEnt, b, g, r)
    elif  placaComp == "AC01":
        ele1 = ((106,180), (71,218), (104,259), (145,219))
        ele2 = ((429,34), (388,137), (428,258), (473,136))
        localizarElemento(ele1, ele2, placaEnt, b, g, r)
    elif  placaComp == "AC02":
        ele1 = ((284,112), (249,146), (284,193), (323,151))
        ele2 = ((431,39), (390,151), (431,166), (474,152))
        localizarElemento(ele1, ele2, placaEnt, b, g, r)

# definindo uma função de localização da cor vermelha em uma posição específica indicando o parafuso correspondendte
def localizarElemento(ele1, ele2, img, b, g, r):
    placaAceitavel  = True
    elemento = "direito"
    for ponto in ele1:
        (b, g, r) = img[ponto[1],ponto[0]]
        if b == 0 and g == 0 and r == 255:
            print("Elemento " + elemento + " da placa faltando ou fora da posição correta.")
            placaAceitavel  = False
            break
        
    elemento = "esquerdo"
    for ponto in ele2:
        (b, g, r) = img[ponto[1],ponto[0]]
        if b == 0 and g == 0 and r == 255:
            print("Elemento " + elemento + " da placa faltando ou fora da posição correta.")
            placaAceitavel  = False
            break

    if placaAceitavel:
        print("Montagem de placa aceitável")
    else:
        print("Montagem de placa inaceitável")

#placas a serem analisadas
listaPlacas = ["Erro_Slide1.JPG", "Erro_Slide2.JPG", "Erro_Slide6.JPG", "Erro_Slide8.JPG", "Slide3.JPG", "Slide8.JPG", "Slide10.JPG", "Slide12.JPG"]
listaPlacasReconhecidas = []
listaPlacasGabarito = ["AB01", "AB02", "AC01", "AC02"]

for plc in listaPlacas:
    
    ###etapa de inclinação
    original = cv2.imread(plc) #colorida # incluir a imagem original no framwork
    img = cv2.imread(plc,0) #monocromática = binária # incluir a imagem original para ser convertida em PB
    (alt, lar) = img.shape[:2] #captura altura e largura # definindo altura e largura da imagem pelo formato e alocando nas variáveis alt e lar
    ret, imgT = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)#230 # transformando a imagem em PB e alocando em duas variáveis ret e imgT

    # descobrindo a inclinação da imagem
    p1=0 # ponto 1 encontrado sim (1) ou não (2)
    p2=0 # ponto 2 encontrado sim (1) ou não (2)
    xi=lar # x inicial definido como a largura da imagem
    inc=0 # inclinação da imagem negativa (0) ou positiva (1)

    for y in range (0,alt,1): # percorrendo toda a altura da imagem 1 pixel de cada vez
        for x in range (0,lar,1): # percorrendo toda a largura da imagem 1 pixel de cada vez
            cor = imgT[y,x] # identificando a cor da imagem PB nos pontos x e y do loop
            if cor!=255 and(p1==0):  # se a cor for outra que não branco e p1 ainda não for identificado:
                ponto1=(x,y) # definir a localização atual como o ponto 1
                xi=x # definir o x atual como x inicial
                p1=1 # identificar que p1 já foi identificado
                if x>(lar/2): # se o x identificado para o ponto 1 for maior que a metade da figura:
                    inc=1 # para saber se a inclinação é positiva ou negativa # a inclinação é identificada como positiva
                            
            if (p1==1) and (inc==1) and (cor!=255) and (x<xi): # se o p1 foi encontrado, a inclinação for positiva, a cor for diferente de branco e x atual for menor que o x inicial:
                ponto2=(x,y) # definir o ponto atual como o ponto 2
                xi=x # definir o x atual como x inicial
                
            if (p1==1) and (inc==0) and (cor!=255) and (x>xi): # similar a condição inicial mas indicando o ponto 2 para inclinação negativa
                ponto2=(x,y)
                xi=x

    cv2.circle(original, (ponto1), 5, (0, 255, 0), -1) # identificando o ponto 1 com um circulo verde
    cv2.circle(original, (ponto2), 5, (0, 255, 0), -1) # identificando o ponto 2 com um circulo verde

    #cv2.imshow("Imagem original com marcações", original) # mostrando a imagem original com os pontos identificados
                           
    angulo = math.atan2 (ponto1[1]-ponto2[1],ponto1[0]-ponto2[0]) # definindo o angulo de inclinação da imagem pelo arctan da diferença dos dois pontos
    if inc==1:
        angulo = math.degrees(angulo) # se a inclinação for positiva o angulo será o correspondente em graus do arctan identificado
    if inc==0:
        angulo = math.degrees(angulo)+180 # se a inclinação for negativa o angulo será o correspondente em graus do arctan identificado + 180 graus
        # invertendo o os pontos 1 e 2
        aux=ponto1
        ponto1=ponto2
        ponto2=aux
        
    #print ('Inclinacao = ', angulo) # imprimindo o angulo encontrado

    # girando a imagem monocromatica
    M = cv2.getRotationMatrix2D(ponto1, angulo, 1.0) # encontrando a matriz de rotação 2D para o angulo definido a partir do ponto 1 e alocando na variavel M
    img_rotacionada = cv2.warpAffine(imgT, M, (lar, alt)) # rotacionando a imagem PB de acordo com a matriz M identificada
    #cv2.imshow("Imagem rotacionada", img_rotacionada) # mostrando a imagem PB rotacionada

    # girando a imagem original  
    original_rotacionada = cv2.warpAffine(original, M, (lar, alt)) # rotacionando a imagem original de acordo com a matriz M identificada
    #cv2.imshow("Original rotacionada", original_rotacionada) # mostrando a imagem PB rotacionada

    # cortando a imagem original
    pontoinicial=ponto1 # ponto 0,0 da imagem recortada
    larguraPlaca = 602 # largura padrão da placa já conhecida
    alturaPlaca = 295 # altura padrão da placa já conhecida

    # definindo os pontos de recorte em x e y considerando o início da imagem até o ponto 1
    xi=pontoinicial[0]-larguraPlaca
    xf=pontoinicial[0]
    yi=pontoinicial[1]
    yf=pontoinicial[1]+alturaPlaca

    recorte = original_rotacionada[yi:yf,xi:xf] # recortando a imagem original nos trechos encontrados
    cv2.imshow("Placa original", original)
    cv2.imshow("Placa tratada", recorte) # mostrando imagem recortada
    cv2.imwrite("Recorte.jpg", recorte) #salvando a imagem recortada no disco
    #cv2.waitKey()



    ###etapa de identificação de numero das placas
    imgIdent = "Recorte.jpg"
    image1 = cv2.imread(imgIdent)
    image1 = cv2.resize(image1, (1806, 885))
    #image1_resized = cv2.resize(image1, (1806, 885))
    #cv2.imshow('Original', image1_resized)
    #cv2.imshow('Original',image1 )

    ## Tratamento da imagem ##
    image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    thresh = thresholding(image1)
    #cv2.imshow('Thresh',image1 )

    #print ('Final com tratamento')
    custom_config = r'-c tessedit_char_blacklist=abcdefghijklmnopqrstuvwxyz/ --psm 12'
    a=(pytesseract.image_to_string(thresh, config=custom_config))
    #print('Reconhecido: ', a)
    placaCorrigida = ''
    for letra in a:
        if letra in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmbopqrstuvwxyz0123456789':
            if letra in 'OQ':
                placaCorrigida += '0'
            else:
                placaCorrigida += letra
        else:
            continue
    print("Placa " + str(listaPlacas.index(plc)+1) + ": " + placaCorrigida)
    listaPlacasReconhecidas.append(placaCorrigida)



    ###etapa de comparação
    # identifica a primeira imagem como original
    original = cv2.imread("Recorte.jpg")
    #identifica a segunda imagem como duplicada
    if placaCorrigida == "AB01":
        duplicate = cv2.imread("Gabarito AB01.jpg")
    elif  placaCorrigida == "AB02":
        duplicate = cv2.imread("Gabarito AB02.jpg")
    elif  placaCorrigida == "AC01":
        duplicate = cv2.imread("Gabarito AC01.jpg")
    elif  placaCorrigida == "AC02":
        duplicate = cv2.imread("Gabarito AC02.jpg")
    else:
        print("Placa não reconhecida!")
        break

    # verifica se as imagens possuem o mesmo formato e canais de cores a partir do atributo .shape
    #if original.shape == duplicate.shape:
    #    print("The images have same size and channels")

    # subtraindo as diferenças dos pixeis das duas imagens no modelo RGB de 0 a 255
    # se a subtração for zero, os pixeis são iguais
    difference = cv2.subtract(original, duplicate)

    # separando as subtrações entre os canais de cores e alocando nas variaveis b, g e r
    b, g, r = cv2.split(difference)

    # correndo todos os pixeis do eixo y da imagem original
    for y in range (0,original.shape[0],1):
        # correndo todos os pixeis do eixo x da imagem original
        for x in range (0,original.shape[1],1):
            # comparando de os canais b, g e r são similares na mesma posição do pixel analisado
            # caso a diferença seja outra que não zero o pixel é marcado em vermelho na imagem duplicada
            if b[y,x] > 40 or g[y,x] > 40 or r[y,x] > 40:
                duplicate [y,x]=(0,0,255)



    ###etapa de identificação de erro das placas
    apontarGabarito(placaCorrigida, duplicate, b, g, r)
    print()
    
    cv2.imshow("Diferenca", duplicate)
    cv2.waitKey()

cv2.destroyAllWindows()
