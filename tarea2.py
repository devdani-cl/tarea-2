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
    cached = r.get(idPokemon) # le pregunto a redis por los pokemones con la id
    if cached: # si está el pokemon {id} entonces lo paso a json
        return  json.loads(cached)  
    else:
        return {"pokemon": "Pokemon no existe - no se encuentra"} # sino está el pokemon no se encuentra o no existe
    

'''
Un endpoint del tipo GET, cuya URL sea /pokemon/filter/type/TYPE, que entregue
una lista en JSON con todos los Pokemon cuyo tipo primario corresponda al tipo
entregado en la variable TYPE
'''
@app.get("/pokemon/filter/type/{tipo}") # 'ice', 'grass', etc
def get_pokemonPrimario(tipo: str): # 'ice', 'grass', etc
#    info_pokemon = get_idPokemon(idPokemon=int) # aca entro al método donde me entrega el id 
    '''
    El tema es hacer la iteración sobre la redis ¿cómo lo hago?
    '''
    info_pokemon = r.get("https://pokeapi.co/api/v2/pokemon/?limit=151")
    for n in info_pokemon["results"]:
        nombrePokemon = n["name"]
        primertipo = n["types"]["slot"] 
        if  primertipo == 1 and primertipo["type"]["name"] == tipo:
            return  [{"{nombrePokemon}": tipo}]

'''
    for i in info_pokemon["results"]["types"]: #esto podría estar bien
        if i["slot"] == 1:
            primario = i["type"]["name"]  
            return [{"{nombrePokemon}": primario}]
'''            