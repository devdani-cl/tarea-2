from fastapi import FastAPI
import redis
import os
import requests
import json

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
                tipo_pokemon.append(poke_json) #lo agrego
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
                tipo_pokemon.append(poke_json) #lo agrego
    return tipo_pokemon 

'''
Un endpoint del tipo GET, cuya URL sea /pokemon/filter/power/, que entregue los
Pokemon mas fuertes segun su stat de ataque. Por defecto, debe entregar un top 5,
pero puede recibir un parametro opcional llamado results (de tipo entero), que haga
referencia a la cantidad de resultados que debe entregar el endpoint.

Realice lo mismo con la defensa, la velocidad y el peso. Los endpoints deben llamarse
defense, speed y weight, respectivamente.

'''
@app.get("/pokemon/filter/{stats}/") # power, defense, speed, weigth
def filtrarPorStat(stats: str):
    top = []
    for n in range(1,152):
        cache = r.get(n)
        if not cache:
            continue

        poke_json = json.loads(cache)
        if stats == "power": 
            for i in poke_json["stats"]:
                if i["stat"]["name"] == "attack":
                    top.append((i["base_stat"], poke_json)) 

        if stats == "defense":
            for i in poke_json["stats"]:
                if i["stat"]["name"] == "defense":
                    top.append((i["base_stat"], poke_json))
        
        if stats == "speed":
            for i in poke_json["stats"]:
                if i["stat"]["name"] == "speed":
                    top.append((i["base_stat"], poke_json))
        
        if stats == "weight":
            top.append((poke_json["weight"], poke_json))

    top_stats =  sorted(top, key=lambda x:x[0], reverse=True)
    return [p for _, p in top_stats[:5]]



'''
Cree un endpoint muy similar a /pokemon/extract pokemon del tipo GET, cuya URL
sea /pokemon/extract power move, que sea capaz de guardar en Redis (de la forma
que usted estime conveniente) el poder del ataque consultado.
'''
@app.get("/pokemon/extract_powe_move/")
def get_extractPowerMove():
    pass