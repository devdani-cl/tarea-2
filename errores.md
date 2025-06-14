# Documentación de errores por item.

# item 2:

Un endpoint del tipo GET, cuya URL sea /pokemon/filter/type/TYPE, que entregue
una lista en JSON con todos los Pokemon cuyo tipo primario corresponda al tipo
entregado en la variable TYPE

### Código:

```py
@app.get("/pokemon/filter/type/{tipo}") # 'ice', 'grass', etc
def get_pokemonPrimario(tipo: str): # 'ice', 'grass', etc    
    tipo_pokemon = []
    for n in range(1,152):
        cache = r.get(n)
        if not cache:
            continue
        # ¿lo paso a diccionario?
        for i in cache["types"]:
            if i["slot"] == 1 and i["type"]["name"] == tipo:
                tipo_pokemon.append(tipo)
    
    return tipo_pokemon
```
### Error:
![alt text](image.png)
- `if cache: continue` salta cuando hay dato.
- `cache["types"]` es una cadena JSON, por lo tanto hay que convertirlo
 
### Solucion:
 ```py
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
 ```


