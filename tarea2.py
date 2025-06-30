from fastapi import FastAPI
import redis
import os
import requests
import json
from random import choice

app = FastAPI()

# Conexión a Redis (host viene de docker-compose)
r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

# Este endpoint usted NO lo puede modificar y/o alterar, cualquier modificacion a este endpoint para efectos de su tarea incurre en un descuento de 70 puntos por no seguir las instrucciones.
# Si usted quiere entender mejor los que hace este endpoint los print dentro de este endpoint si son permitidos y no se incurren en el descuento anteriormente mencionado.
@app.get("/pokemon/extrac_pokemon")
def get_pokemon():
    # 1
    url = "https://pokeapi.co/api/v2/pokemon/?limit=151"
    response = requests.get(url)
    # 2
    poke_json = json.loads(response.text)
    pokemons = poke_json["results"]
    # 3
    for e,pokemon in enumerate(pokemons):
        poke_url = pokemon["url"]
        # 4
        value = r.get(e+1) # busca en redis
        # si value tiene valor 5.a
        if value:
            # 6.a
            continue
        # 5.b esta implicito, ya que value sera None si el pokemon no exite, por ende el if anterior no hace el continue
        # 6b
        poke_response = requests.get(poke_url)
        # 7.b
        poke_json_info = json.loads(poke_response.text)
        # 8.b
        poke_json_object = json.dumps(poke_json_info) # Convertimos a tipo json, les toca investigar el por qué
        r.set(e+1, poke_json_object, ex=3600)
    # 9
    return {"ok": True}

'''
Un endpoint del tipo GET, cuya URL sea /pokemon/ID, que entregue como JSON la
información de cada Pokémon dado su ID.
'''
@app.get("/pokemon/{idPokemon}")
def get_idPokemon(idPokemon: int):
    cache = r.get(idPokemon) # le pregunto a redis por los pokemones con la id
    if cache: # si está el pokemon {id} entonces lo paso a json
        return  json.loads(cache)  
    else:
        return {"pokemon": "Pokemon no existe - no se encuentra"} # sino está el pokemon no se encuentra o no existe
    
'''
Un endpoint del tipo GET, cuya URL sea /pokemon/filter/type/TYPE, que entregue
una lista en JSON con todos los Pokemon cuyo tipo primario corresponda al tipo
entregado en la variable TYPE
'''
@app.get("/pokemon/filter/type/{tipo}") # 'ice', 'grass', etc
def get_pokemonPrimario(tipo: str): # 'ice', 'grass', etc    
    tipo_pokemon = [] # lista vacia para agregar los diccionarios completos
    for n in range(1,152): # recorro 
        cache = r.get(n) # busco en redis 
        if not cache: # si no está lo salto
            continue

        poke_json = json.loads(cache) # lo convierto a json para poder indexarlo
        for i in poke_json["types"]: 
            if i["slot"] == 1 and i["type"]["name"] == tipo:
                tipo_pokemon.append({
                    "pokemon": poke_json["name"],
                    "tipo": tipo}) #lo agrego solo el nombre y el tipo y no el paño completo de los pokemones
    return tipo_pokemon 

'''
Un endpoint del tipo GET, cuya URL sea /pokemon/filter/type/TYPE/2, similar al
anterior, pero que entregue todos los Pokemon cuyo segundo tipo sea el tipo entregado
en la variable TYPE.
'''
@app.get("/pokemon/filter/type/{tipo}/2")
def get_pokemonSecundario(tipo: str): # 'ice', 'grass', etc    
    tipo_pokemon = [] # lista vacia para agregar los diccionarios completos
    for n in range(1,152): # recorro 
        cache = r.get(n) # busco en redis 
        if not cache: # si no está lo salto
            continue

        poke_json = json.loads(cache) # lo convierto a json para poder indexarlo
        for i in poke_json["types"]: 
            if i["slot"] == 2 and i["type"]["name"] == tipo:
                tipo_pokemon.append({
                    "pokemon": poke_json["name"],
                    "tipo": tipo})
    return tipo_pokemon 

'''
Un endpoint del tipo GET, cuya URL sea /pokemon/filter/power/, que entregue los
Pokemon mas fuertes segun su stat de ataque. Por defecto, debe entregar un top 5,
pero puede recibir un parametro opcional llamado results (de tipo entero), que haga
referencia a la cantidad de resultados que debe entregar el endpoint.

Realice lo mismo con la defensa, la velocidad y el peso. Los endpoints deben llamarse
defense, speed y weight, respectivamente.

'''
@app.get("/pokemon/filter/{stats}/")
@app.get("/pokemon/filter/{stats}/{results}")
def filtrarPorStat(stats: str, results: int=5):
    '''
    Dos endpoints donde /pokemon/filter/{stats}/ filtra los primeros 5
    y /pokemon/filter/{stats}/{results}/ que filtra por el numero que uno quiera, 
    los dos endpoints apuntan a la misma función
    '''
    top = []
    for n in range(1, 152):
        cache = r.get(n) #busco en redis a los pokemones
        if not cache:
            continue
        poke_stats = json.loads(cache) #lo convierto en json para indexar

#filtro por stats
        if stats == "power":
            for s in poke_stats["stats"]:
                if s["stat"]["name"] == "attack":
                    top.append((
                        s["base_stat"],
                        {"pokemon": poke_stats["name"], "stat_attack": s["base_stat"]}
                    ))
                    break

        if stats == "defense":
            for s in poke_stats["stats"]:
                if s["stat"]["name"] == "defense":
                    top.append((
                        s["base_stat"],
                        {"pokemon": poke_stats["name"], "stat_defense": s["base_stat"]}
                    ))
                    break

        if stats == "speed":
            for s in poke_stats["stats"]:
                if s["stat"]["name"] == "speed":
                    top.append((
                        s["base_stat"],
                        {"pokemon": poke_stats["name"], "stat_speed": s["base_stat"]}
                    ))
                    break

        if stats == "weight":
            peso = poke_stats["weight"]
            top.append((
                peso,
                {"pokemon": poke_stats["name"], "stat_weight": peso}
            ))

    top_sorted = sorted(top, key=lambda x: x[0], reverse=True) # ordenar de mayor a menor 
    return [e for _, e in top_sorted[:results]] # creo una nueva lista, por defecto devuelve los primeros 5 con el endpoint /pokemon/filter/{stats}/,
# ya que results por defecto vale 5. El endpoint /pokemon/filter/{stats}/{results}/ tambien apunta a la misma función,
# donde results indica el top que uno quiera mostrar. 

'''
Cree un endpoint tipo GET, cuya URL sea /pokemon/extract_power_move capaz de
consultar la informacion de un movimiento, si el movimiento fue consultado por primera
vez, este debe ser guardado en redis, por consecuencia, si el movimiento existe en redis
se debe entregar la informacion obtenida desde este. PD: Si usted quiere verificar su
respuesta, dentro del json que devuelva su api debe estar la llave power
'''
@app.get("/pokemon/extract_power_move/{idPokemon}/")
def get_extractPowerMove(idPokemon: int):
    datos = r.get(idPokemon) #se lee el pokmeon con la id desde redis
    if not datos: # si no existe error
        return {"error": "no encontrado"}
    poke = json.loads(datos) #se convierte a json(diccionario) para indexar
    result = []

    if "moves" in poke: #si existe la clave move en el json itero
        for mov in poke["moves"]: #itero cada entrada en moves
            name = mov["move"]["name"] #nombre del movimiento
            key = f"move_power:{name}" #se crea la clave que estará en redis, para luego reviar el mov
            cache = r.get(key) # se lee el cache del movimiento
            if cache:
                info = json.loads(cache) 
            else:
                resp = requests.get(mov["move"]["url"]) 
                info = resp.json()
                if "power" not in info: #solo se guarda si existe el campo "power"
                    continue
                r.set(key, json.dumps(info), ex=3600)                
            result.append(info) #guarda 

    return result


'''
Cree un endpoint que devuelva una batalla Pokemon por turnos, cuya URL sea
/pokemon/fight/ID1vsID2, donde ID1 e ID2 hacen referencia a los IDs de dos Pokemon.
En cada turno, cada Pokemon lanza un ataque; el que comienza se elige de forma aleato-
ria. Todos los ataques tienen un porcentaje de efectividad del 100%. La batalla debe
iterar hasta que un Pokemon quede fuera de combate. El historial de la batalla debe
ser guardado en algun tipo de estructura que usted estime conveniente, con tal de que
el endpoint devuelva un JSON.
'''
@app.get("/pokemon/fight/{id1}/{id2}/")
def batallaPokemon(id1: int, id2: int):
    p1 = None #inicializo los pokemon en None para despues rellenar con datos
    p2 = None
    for i in range(1,152):
        cache = r.get(i)
        if not cache:
            continue
        poke_json = json.loads(cache)
        if i == id1:
            hp1, ataque1 = 0, 0 #inicializo la vida y el ataque en 0
            for s in poke_json["stats"]:
                if s["stat"]["name"] == "hp": #busca la vida del pokemon
                    hp1 = s["base_stat"] # se encuentra la vida y se le asigna
                    break 
            for s in poke_json["stats"]:
                if s["stat"]["name"] == "attack": #busca la vida del pokemon
                    ataque1 = s["base_stat"] # se encuentra la vida y se le asigna
                    break 
            p1 = {"id": id1, "pokemon": poke_json["name"], "vida": hp1, "ataque": ataque1} # pokemon con sus datos para la batalla
        
        if i == id2:
            hp2, ataque2 = 0, 0 #inicializo la vida y el ataque en 0
            for s in poke_json["stats"]:
                if s["stat"]["name"] == "hp": #busca la vida del pokemon
                    hp2 = s["base_stat"] # se encuentra la vida y se le asigna
                    break 
            for s in poke_json["stats"]:
                if s["stat"]["name"] == "attack": #busca la vida del pokemon
                    ataque2 = s["base_stat"] # se encuentra la vida y se le asigna
                    break 
            p2 = {"id": id2, "pokemon": poke_json["name"], "vida": hp2, "ataque": ataque2} # pokemon con sus datos para la batalla
    
    resultados = [] 
    atacante = choice([1,2])
    while p1["vida"] > 0 and p2["vida"] > 0:
        if atacante == 1: # si es 1 el pokemon1 ataca primero 
            p2["vida"] = max(p2["vida"] - p1["ataque"], 0) #la vida nunca es negativa, el min es cero
            resultados.append(f"{p1["pokemon"]} ataca a {p2["pokemon"]} → {p2["pokemon"]} HP = {p2["vida"]}")
            atacante = 2
        else:
            p1["vida"] = max(p1["vida"] - p2["ataque"], 0)
            resultados.append(f"{p2["pokemon"]} ataca a {p1["pokemon"]} → {p1["pokemon"]} HP = {p1["vida"]}")
            atacante = 1

    ganador = p1["pokemon"] if p1["vida"] > 0 else p2["pokemon"]
    return {"resultado": resultados, "ganador": ganador}