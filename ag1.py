# Autor: Alejandro Biasin, 2020
import pygame_textinput
# https://github.com/Nearoo/pygame-text-input
# otra opcion https://stackoverflow.com/questions/46390231/how-to-create-a-text-input-box-with-pygame
import pygame
from pygame.locals import *
from time import sleep
import random
from random import randrange
import math
import textwrap
import unicodedata
import os # para posicionar la ventana

def main():  # type: () -> None
    # Variables globales
    global screenrel
    global width
    global height
    global screen
    global clock
    global FPS
    global inventory
    global show_inventory
    global rooms
    global currentRoom
    global musica
    global global_text
    global show_message
    global message_time
    global previoustext
    global maxstringlength
    global smallfont
    global textcolor
    global cursorcolor
    global backtextcolor
    global backinvcolor
    global backitemcolor
    global fontsize
    global run
    global textinput
    global textX
    global textY
    global textinputX
    global textinputY
    global text # TODO: Quitar

    # Inicializar PyGame y pantalla
    pygame.init()
    screenrel = 1.5
    width = int(pygame.display.Info().current_w / screenrel)
    height = int(pygame.display.Info().current_h / screenrel)
    # posicionar la ventana centrada
    xc = ( pygame.display.Info().current_w - width ) / 2
    yc = ( pygame.display.Info().current_h - height ) / 2
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (xc,yc) 
    # los doble parentesis son "2-item sequence"
    screen = pygame.display.set_mode((width, height)) 
    gamename = 'Alex\'s First Graphic Adventure Game'
    pygame.display.set_caption(gamename)
    # en vez de pygame.time.delay(100), usar clock para controlar los FPS
    clock = pygame.time.Clock()
    FPS = 30 # Frames per second.
    # Message Box
    global_text = ''
    show_message = False
    message_time = 0
    previoustext = ''
    
    # defining a font 
    fontsize = int(40 / screenrel)
    maxstringlength = 50
    smallfont = pygame.font.SysFont('Corbel', fontsize)
    textcolor = (255, 220, 187) # RGB default textcolor
    cursorcolor = (187, 220, 255)
    backtextcolor = (170, 170, 170, 190) # fondo translucido de texto
    backinvcolor = (87, 27, 71, 150) # fondo translucido de inventario
    backitemcolor = (142, 67, 192, 190) # fondo translucido de inventario
    textX = width/3
    textY = height/3
    textinputX = 10
    textinputY = height-fontsize-10
    show_inventory = False
    currentRoom = ''
    run = True
    # Create TextInput-object (3rd party library)
    textinput = pygame_textinput.TextInput(text_color = textcolor, cursor_color = cursorcolor, font_size = fontsize, max_string_length = maxstringlength)

    # En pygame:
    #  - se usa Surface para representar la "apariencia", y
    #  - se usa Rect para representar la posicion, de un objeto.
    #  - se puede heredar de pygame.sprite.Sprite
    
    setRooms()
    setItems()
    # TEST rendering a text (TODO: QUITAR)
    text = smallfont.render('Hola' , True , textcolor)
    # Cargar sonido
    #grillos = pygame.mixer.Sound('grillos.wav')
    pygame.mixer.init()
    musica = pygame.mixer.music
    # start the player in the first room
    goToRoom(list(rooms)[0]) # Primer room de la lista
    # draw the initial screen
    draw_screen()
    # and let the game begin
    gameLoop()


def doQuit():
    # Desactivar sonido y video, y salir
    globalMessage(randomString(['Bye bye!','We\'ll miss you...','Don\'t be frustrated. You\'ll make it next time.']))
    draw_screen()
    sleep(1)
    musica.stop()
    pygame.quit()
    quit()

def globalMessage(texto):
    global global_text
    global show_message
    global message_time
    #global_text = filter_nonprintable(texto)
    global_text = texto
    show_message = True
    message_time = int(2 + math.sqrt(len(global_text)) * (FPS/2)) # tiempo en pantala proporcional al texto

def drawText(texto, color, x, y):
    textosurf = smallfont.render(texto , True , color)
    screen.blit(textosurf, (x, y) )
        
def updateMessage():
    global show_message
    global message_time
    message_time -= 1
    if message_time == 0:
        show_message = False # si la cuenta regresiva termino, quitar mensaje
    ancho_recuadro = 40 # en caracteres
    aspectw = int(14 / screenrel)
    # TODO: Arreglar ancho cuando hay 2 renglones desproporcionados
    wrappedlines = textwrap.wrap(global_text, ancho_recuadro, replace_whitespace=False)
    lineas_recuadro = len(wrappedlines)
    dw = 5 # delta/margen de ancho
    dh = 5 # delta/margen de alto
    maxlen = 0
    for line in wrappedlines: # obtengo ancho maximo
        if len(line) > maxlen:
            maxlen = len(line)
    #w = (len(global_text)*aspectw + dw) / lineas_recuadro # ancho de la caja de texto (teniendo en cuenta wrap)
    w = int(maxlen * aspectw) + dw
    fh = fontsize + dh # alto de una linea de texto
    h = fh * lineas_recuadro # altura total del recuadro (teniendo en cuenta wrap)
    x = width/2 - w/2
    y = height/2 - h/2
    drawRect(x,y,w,h,backtextcolor) # recuadro de fondo
    i = 0
    for line in wrappedlines:
        drawText(line, textcolor, x+dw, y+dh+i*fh)
        i = i + 1

def procesarComando(comando):
    words = comando.lower().split()
    if words[0] in ('quit','salir'):
        doQuit()
    if words[0] in ('help','ayuda','?'):
        showHelp()
    #some fun
    elif words[0] == 'jump':
        globalMessage(randomString(['There is no jumping in this game','This is Kaos. We don\'t jump here!']))
    elif words[0] == 'dive':
        globalMessage(randomString(['Are you nuts?','You should change your pills.','No diving in this area!']))
    elif words[0] == 'sleep':
        globalMessage(randomString(['Come on you lazy cow!','There is no time for a nap','No! Wake up!']))
    elif words[0] in ('talk','scream','shout'):
        globalMessage(randomString(['Shhh!']))
    elif words[0] in ('look','mirar','ver'):
        if len(words) == 1:
            comandoLookRoom()
        else:
            comandoLookItem(words[1])
    elif words[0] in ('get','take','grab','agarrar'):
        if len(words) > 1:
            itemstr = words[1]
            comandoGetItem(itemstr)
    elif (words[0] in ('go','ir')) and (len(words)>1):
        comandoGoRoom(words[1])
    elif (words[0] == 'use') and (len(words)>3) and (words[2] == 'with'):
        comandoUse(words[1], words[3])
    else:
        globalMessage(randomString(['Incorrect command','Not sure what you mean','Try something else']))

def showHelp():
#2345678901234567890123456789012345678901234567890123456789012345678901234567890
    helpmessage = """               -< Command Help >-                                        
look : describes what's around you.                                             
look [item] : describes an item in your inventory or in the room.               
get [item] : takes an object of the room and keeps it in your inventory.        
use [item] with [item] : tries to make an interaction between the two items.    
go [direction] : walk to another room.                                           
F3 : repeats last command.                                                      
TAB : shows your inventory.                                                     
"""
    globalMessage(helpmessage)
    
def comandoGoRoom(direction):
    #check that they are allowed wherever they want to go
    if direction in rooms[currentRoom]['directions']:
        #set the current room to the new room
        goToRoom( rooms[currentRoom]['directions'][direction] )
    else: # there is no door (link) to the new room
        globalMessage(randomString(['You can\'t go that way!','Really? '+direction+'?','Consider getting a compass','I don\'t think going that way is the right way','Danger! Going that way is demential (because it doesn\'t exists)']))

def comandoLookRoom():
    # mostrar descripcion del room actual, y posibles salidas
    mensaje = rooms[currentRoom]['desc']
    # mostrar los items que hay en el room actual
    if bool(rooms[currentRoom]['items']):
        mensaje += ' You see '
        i = 0
        cantitems = len(list(rooms[currentRoom]['items']))
        for item in rooms[currentRoom]['items']:
            i += 1
            if i > 1:
                mensaje += ', '
                if cantitems == i:
                    mensaje += 'and '
            mensaje += rooms[currentRoom]['items'][item]['roomdesc']
        mensaje += '.                                          '
    
    moves = rooms[currentRoom]['directions'].keys()
    movelist = list(moves)
    cantmoves = len(movelist)
    if cantmoves == 1:
        mensaje += 'Your only move is ' + movelist[0]
    else:
        mensaje += 'Your possible moves are '
        #i = 0
        for i in range(cantmoves):
            #i += 1
            if i > 0:
                if cantmoves-1 == i:
                    mensaje += ' and '
                else:
                    mensaje += ', '
            mensaje += movelist[i]
        mensaje += '.'
    
    globalMessage(mensaje)

def comandoLookItem(itemstr):
    # el item a mirar puede estar en el inventario o en el room actual
    if (itemstr in inventory.keys()):
        mensaje = inventory[itemstr]['desc']
    else:
        if (itemstr in rooms[currentRoom]['items'].keys()):
            mensaje = 'You see ' + rooms[currentRoom]['items'][itemstr]['roomdesc']
        else:
            if (itemstr in rooms[currentRoom]['directions'].keys()):
                mensaje = 'Yes, you can go ' + itemstr
            else:
                mensaje = randomString(['The ' + itemstr + ' is not here' , 'I don\' see any ' + itemstr])
    globalMessage(mensaje)

def comandoGetItem(itemstr):
#    'descwords' ??
    #print ('inventory.keys() : ' + str(inventory.keys()))
    if (itemstr in inventory.keys()):
        globalMessage('You already have the ' + itemstr)
    else:
        if (itemstr in rooms[currentRoom]['items']):
            if (rooms[currentRoom]['items'][itemstr]['takeable']):
                #add the item to their inventory
                # inventory.update(rooms[currentRoom]['items'][itemstr])
                inventory[itemstr] = rooms[currentRoom]['items'][itemstr]
                #display a helpful message
                globalMessage(randomString([itemstr + ' got!','Yeah! You have gotten the '+itemstr,'The '+itemstr+', just what you\'ve been looking for','At last, the glorious '+itemstr ]))
                #delete the item from the room
                del rooms[currentRoom]['items'][itemstr]
            else:
                globalMessage(randomString(['You can\'t get the ' + itemstr, 'Nah! It\'s like painted to the background', 'You wish!']))
        else:
            #tell them they can't get it
            globalMessage(randomString([itemstr + ' is not here', 'Nah!', 'You wish!']))

def comandoUse(item1, item2):
    # item1 debe estar en el inventory
    # item2 puede estar en el room (para accionar algo) o en el inventory (para mezclarlos)
    if (item1 in inventory.keys()):
        if (item2 in inventory.keys()): # mezclar 2 items del inventory
            if ('mixwith' in inventory[item1]) and ('mixwith' in inventory[item2])==True and (inventory[item1]['mixwith']['otheritem'] == item2) and (inventory[item2]['mixwith']['otheritem'] == item1):
                # creo el nuevo item
                nuevoitem = inventory[item2]['mixwith']['summon']
                inventory[nuevoitem] = ghostitems[nuevoitem]
                # delete both original items from the inventory
                del inventory[item1]
                del inventory[item2]
                del ghostitems[nuevoitem]
                #display a helpful message
                #globalMessage('summoned a ' + nuevoitem)
                globalMessage(inventory[nuevoitem]['summonmessage'])
            else:
                globalMessage(randomString(['Can\'t use ' + item1 + ' with ' + item2 + '!','I don\'t think the '+item1+' is meant to be used with the '+item2,'...'+item1+' with '+item2+' does not compute.']))
        elif (item2 in rooms): # accionar algo
            globalMessage('TODO: accionar algo')
#            else:
#                globalMessage(randomString(['Can\'t use ' + item1 + ' with ' + item2 + '!','I don\'t think the '+item1+' is meant to be used with the '+item2,'...'+item1+' with '+item2+' does not compute.']))
        else:
            globalMessage(randomString(['There is no ' + item2 + ' around.', 'Try something else.']))
    else:
        globalMessage('You don\'t have any ' + item1)

def goToRoom(newroom):
    global currentRoom
    global background
    global textcolor
    # Cargar fondo en memoria y redimensionarlo para que ocupe la ventana
    backimage = rooms[newroom]['background']
    background = pygame.image.load(backimage)
    background = pygame.transform.scale(background, (width, height))
    # Cargar musica de fondo del room
    tema = rooms[newroom]['music']
    #print ('yendo de ' + currentRoom + ' a ' + newroom + ' con tema ' + tema)
    currentRoom = newroom
    musica.load(tema)
    musica.play(-1) # If the loops is -1 then the music will repeat indefinitely.
    
    #textcolor = (34, 120, 87)
    
def drawRect(x,y,w,h,color):
    surf = pygame.Surface([w, h], pygame.SRCALPHA)
    surf.fill(color)
    screen.blit(surf, [x,y,w,h])

def drawItem(x,y,w,h,itemimagefile):
    itemimage = pygame.image.load(itemimagefile)
    itemimage = pygame.transform.scale(itemimage, (int(w), int(h)))
    screen.blit(itemimage, (x, y))

def drawInventory():
    # si no tengo nada en el inventario, mostrar mensaje
    if bool(inventory) == False:
        globalMessage(randomString(['You are carrying nothing!', 'Nothing in your pockets so far', 'Maybe if you start using the "get" command...']))
    else:
        #globalMessage(str(inventory))
        itemsperrow = 2 # max columns
        listaitems = list(inventory)
        cantitems = len(listaitems)
        rows = math.ceil(cantitems / itemsperrow)
        if cantitems > itemsperrow:
            cols = itemsperrow
        else:
            cols = cantitems
        #print ('rows: ' + str(rows) + '. columns: ' + str(cols) + '. cant: ' + str(cantitems))
        pad = 5 # pixels de padding entre objetos
        aspectw = 9
        aspecth = 8
        itemw = width/aspectw
        itemh = height/aspecth
        # calcular recuadro en funcion a la cantidad de items
        fontheight = fontsize
        xback = 10
        yback = 10
        #w = width/10
        #h = height/10
        wback = (itemw + 2*pad) * cols
        hback = (itemh + 2*pad + fontheight) * rows
        drawRect(xback,yback,wback,hback,backinvcolor) # recuadro de fondo 
        
        i = 0 # indice del item en la lista de items
        #for item in inventory['items']:
        for r in range(rows): # por cada fila del cuadro (comenza desde cero)
            for c in range(cols): # por cada columna del cuadro (comenza desde cero)
                #print ('r=' + str(r) + ', c=' + str(c))
                if i < cantitems:
                    x = (xback + pad) + (itemw + pad) * c
                    y = (yback + pad) + (itemh + pad + fontheight) * r
                    drawRect(x,y,itemw,itemh,backitemcolor) # recuadro del item
                    imagefile = inventory[listaitems[i]]['image']
                    drawItem(x,y,itemw,itemh,imagefile)
                    xt = x
                    yt = y + itemh + pad
                    item = listaitems[i]
                    drawText(item, textcolor, xt, yt)
                i += 1

# Mostrar fondo
def draw_screen():
    # pintar fondo del room en la pantalla
    screen.blit(background, (0, 0))
    screen.blit(text, (textX, textY) )
    # Caja translucida para el textInput
    drawRect(textinputX-3,textinputY-3,maxstringlength*9,fontsize+5,backtextcolor)
    # Blit textInput surface onto the screen
    screen.blit(textinput.get_surface(), (textinputX, textinputY))
    # Si el inventario esta activo, mostrarlo
    if show_inventory == True:
        drawInventory()
    # Si hay un mensaje global, mostrarlo
    if show_message == True:
        updateMessage()
    # Actualizar pantalla con los elementos de screen
    pygame.display.update()

# EJ: print (randomString(['uno','dos','tres','cuatro']))
def randomString(stringList):
    selected = random.choice(stringList)
    return selected

def filter_nonprintable(texto):
    #print('antes  : '+texto)
    #textof = filter(lambda x: x in string.printable, texto) # filtrar caracteres no imprimibles
    textof = ''.join(c for c in texto if not unicodedata.category(c).startswith('C'))
    #print('despues: '+textof)
    return textof

def setRooms():
    global rooms
    # A dictionary linking a room to other rooms. Properties:
    # * Room
    #   - desc: to describe the room or item. [begins with Uppercase and ends with dot]
    #   - background : image of the room
    #   - directions: where to go from this room
    #   - music: background mp3 music for this room
    #   * Item
    #     - image: image to display in the inventory
    #     - roomimage: image to display on top of the original room background
    #     - roomxy: position in the room
    # TODO: ¿como hacer dinamica una descripcion?
    # ¿y si uso items dentro de items? EJ: key behind bushes, knife inside box, etc.
    #     - roomdesc: brief description of the item while still in the room
    #     - desc: item description
    #     - descwords: different words (synonims) that match the item 
    #  ¿Como hacer para modificar la imagen/descripcion del item en funcion a eventos pasados?
    #     - takeable: whether this item can ba taken and put in our inventory
    #     - openable: Para cajas, cajones, puertas.
    #     - locked: Si es True, para poder abrirse con 'open' primero hay que usar el 'unlockeritem'
    #     - unlockeritem: el item de inventario a usar para destrabar y poder abrir este item/objeto de room.
    #     - unlockingtext: El mensaje a mostrar al destrabar un item/objeto de room.
    #     - mixwith: el otro item con el cual me puedo mergear y summonear uno nuevo (del ghostdict)
    #     - iteminside: Es otro item que hay dentro (esta en el room), y queda visible en el room si es abierto este.
    #     - visible: Indica si un item en el room es visible. Si no lo es, antes hay que abrir otro item.
    #     - opened: Indica si el item esta abierto.
    rooms = {
        'Forest' : {
            'desc' : 'You are in a deep and millenary forest.',
            'background' : 'bosque.jpg',
            'directions' : {
               'south' : 'Beach',
               'east' : 'Beach',
               'north' : 'Beach',
               'west' : 'Beach'
              },
            'music' : 'grillos.mp3',
            'items' : {
               'key' : {
                   'image' : 'key.png',
                   'roomimage' : 'key_room.jpg',
                   'roomxy' : [20, 30],
                   'roomdesc' : 'a key',
                   'desc' : 'It\'s a golden key',
                   'descwords' : ['key'],
                   'takeable' : True
                        },
               'knife' : {
                   'image' : 'knife.png',
                   'roomimage' : 'knife_room.jpg',
                   'roomxy' : [30, 40],
                   'roomdesc' : 'a knife beneath the tree',
                   'desc' : 'Some rusty knife',
                   'descwords' : ['knife','blade','cutter'],
                   'mixwith' : {
                       'otheritem' : 'stick',
                       'summon' : 'bayonet'
                       },
                   'takeable' : True
                   },
               'stick' : {
                   'image' : 'stick.png',
                   'roomimage' : 'stick_room.jpg',
                   'roomxy' : [30, 40],
                   'roomdesc' : 'a stick',
                   'desc' : 'A heavy and strong wood stick',
                   'descwords' : ['branch','stick'],
                   'visible' : False,
                   'mixwith' : {
                       'otheritem' : 'knife',
                       'summon' : 'bayonet'
                       },
                   'takeable' : True
                   },
               'bushes' : {
                   'image' : '',
                   'roomdesc' : 'some bushes',
                   'desc' : 'a few thick bushes',
                   'descwords' : ['bush','bushes'],
                   'locked' : True,
                   'unlockeritem' : 'knife',
                   'unlockingtext' : 'You have cut through the bushes and uncovered something.',
                   'iteminside' : 'stick',
                   'opened' : True,
                   'openable' : False,
                   'takeable' : False
                   }
              }
            },
        'Beach' : {
            'desc' : 'This is a quiet and sunny beach.',
            'background' : 'playa-isla.jpg',
            'directions' : {
               'north' : 'Forest'
              },
            'music' : 'seawaves.mp3',
            'items' : {
               'sand' : {
                   'image' : 'sand.png',
                   'desc' : 'Just, you know, sand.',
                   'roomdesc' : 'sand',
                   'takeable' : True
                }
              }
            }
        }

def setItems():
    global inventory
    global ghostitems
    # start with nothing on you
    inventory = {}

    # dictionary of items that will be available later on
    ghostitems = {
            'bayonet' : {
            'image' : 'bayonet.png',
            'roomimage' : 'bayonet_room.jpg',
            'roomxy' : [70, 80],
            'roomdesc' : 'a bayonet',
            'desc' : 'A handy although not that sharp custom bayonet',
            'descwords' : ['spear','bayonet'],
            'summonmessage' : 'Clever! You have made a bayonet out of a stick and that rusty knife.',
            'visible' : True,
            'takeable' : False
            },
        }

def gameLoop():
    global run
    global textX
    global textY
    global show_inventory
    global textinput
    while run: # Game Loop
        dt = clock.tick(FPS) / 1000 # Returns milliseconds between each call to 'tick'. The convert time to seconds.
        #pygame.time.delay(100)

        events = pygame.event.get() # para el textInput
        
        for event in events:
            #print(event) # DEBUG: imprimir todos los eventos
            if (event.type == pygame.QUIT):
                run = False
            if (event.type == pygame.KEYUP):
                if (event.key == pygame.K_ESCAPE):
                    events.remove(event) # no imprimo este caracter
                    run = False
                if (event.key == pygame.K_TAB):
                    #show_inventory = not(show_inventory)
                    show_inventory = False
                    events.remove(event) # no imprimo este caracter
                if (event.key == pygame.K_F1):
                    showHelp()
                if (event.key == pygame.K_F3):
                    largo = len(previoustext)
                    if (largo > 0):
                        textinput.input_string = previoustext # repetir el ultimo comando
                        textinput.cursor_position = largo
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    events.remove(event) # no imprimo este caracter
                    run = False
                if (event.key == pygame.K_TAB):
                    #show_inventory = not(show_inventory)
                    show_inventory = True
                    events.remove(event) # no imprimo este caracter
            
        # Feed textInput with events every frame
        if textinput.update(events): # capturar texto con ENTER
            texto = textinput.get_text()
            #texto = filter_nonprintable(texto)
            if len(texto)>0:
                textinput.clear_text()
                # Procesar comando ingresado
                #globalMessage(texto)
                previoustext = texto
                procesarComando(texto)
        
        keys = pygame.key.get_pressed()
    #    if keys[pygame.K_ESCAPE]:
    #      run = False
          
        if keys[pygame.K_LEFT]:
            textX -= 5

        if keys[pygame.K_RIGHT]:
            textX += 5

        if keys[pygame.K_UP]:
            textY -= 5

        if keys[pygame.K_DOWN]:
            textY += 5

        draw_screen()

    doQuit()

if __name__ == "__main__":
    main()
