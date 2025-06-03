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
        value = r.get(e+1) 
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

    
