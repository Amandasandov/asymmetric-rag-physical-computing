import itertools
import os
import json
import time

# Assicurati di aver installato: pip install google-genai
from google import genai
from google.genai import types

# --- CONFIGURAZIONE ---

# Inserisci la tua API Key o impostala come variabile d'ambiente
API_KEY = os.environ.get("GEMINI_API_KEY", "api_key")

# Modello consigliato: gemini-2.0-flash-exp (veloce e ottimo col JSON) o gemini-1.5-pro
MODEL_ID = "gemini-3-pro-preview" 

# Simulazione (True non consuma token)
SIMULATE_API_CALL = False
SIMULATION_DELAY_SECONDS = 1

# --- DEFINIZIONE COMPONENTI (I nomi rimangono in inglese per la logica interna, ma il prompt li gestisce) ---
INPUTS = {
    'Light Intensity',
    'Noise Level', 'Motion', 'Inclination',
    'Compass', 'Switch', 'Touch Button'
}
OUTPUTS = {
    'Audio Player', 'Musical Keyboard', 'Musical Drum',
    'Lamp', 'LED Matrix'
}
ALL_COMPONENTS = {
    'Light Intensity', 'Noise Level', 'Compass','Audio Player',
    'Musical Keyboard', 'Musical Drum', 'Motion', 'Inclination',
    'Lamp', 'Switch', 'Touch Button', 'LED Matrix'
}

COMPONENT_NUMBER = 2

# --- PROMPT DI SISTEMA (IN SPAGNOLO) ---
SPANISH_SYSTEM_INSTRUCTION = """
Eres un Asistente Creativo encargado de conceptualizar aplicaciones innovadoras para una plataforma de desarrollo que cuenta con una variedad de componentes diseñados para interacciones en el mundo real. Tu objetivo es generar ideas de actividades creativas y luego transformarlas en desafíos atractivos de pensamiento computacional para jóvenes estudiantes, considerando cuidadosamente la idoneidad para la edad y la dificultad de implementación.

Descripciones Funcionales de los Componentes de la Plataforma
Sensor de Ruido (Noise Level): Detecta niveles de ruido ambiental.
Reproductor de Audio (Audio Player): Reproduce y controla la reproducción general de audio.
Teclado Musical (Musical Keyboard): Reproduce notas musicales de un piano.
Baterìa Musical (Musical Drum): Reproduce notas musicales de una baterìa (percusión).
Sensor de Movimiento (Motion): Mide cambios en el movimiento a lo largo de los ejes X, Y y Z.
Sensor de Inclinación (Inclination): Mide la inclinación y la desviación angular a lo largo de los ejes X, Y y Z.
Brújula (Compass): Componente de brújula digital que detecta la dirección y encuentra el Norte.
Lámpara (Lamp): Un elemento de luz (color ajustable).
Interruptor (Switch): Un botón de encendido/apagado personalizable.
Botón Táctil (Touch Button): Un botón digital sensible al tacto.
Matriz LED (LED Matrix): Muestra figuras simples píxel por píxel utilizando una cuadrícula LED de 7x7.
Intensidad de Luz (Light Intensity): Mide la cantidad de luz ambiental.

Tarea General (Dividida en Dos Partes)
Parte 1: Generar Ideas de Actividades Creativas
Debes generar 20 ideas de actividades creativas distintas. Cada idea debe combinar dos o más componentes de una manera significativa e innovadora.

Parte 2: Transformar Ideas en Actividades Atractivas de Pensamiento Computacional
Para cada una de las 20 ideas, transfórmala en una actividad de pensamiento computacional.
- Replantear la Actividad Central: Usa un tema atractivo.
- Preservar la Lógica.
- Motivar a los Estudiantes.
- Determinar Edad Objetivo y Dificultad.

Formato de Salida Final:
Por favor proporciona tu respuesta completa como un único arreglo JSON. 
Cada elemento en el arreglo debe ser un objeto JSON que contenga los siguientes campos:

componentUsed: Un arreglo de cadenas (ej. ["Motion", "Lamp"]).
originalIdeaTitle: Título descriptivo (6–8 palabras).
originalIdeaDescription: Descripción original (60–80 palabras).
transformedIdeaTitle: Título atractivo de la actividad transformada.
transformedIdeaDescription: Descripción completa de la actividad transformada.
minAge: Entero (ej. 10).
maxAge: Entero (ej. 13).
difficultyLevel: Entero (1=fácil, 2=medio, 3=difícil).
algorithmUsed: Cadena que representa la lógica (ej: "IF motion THEN Lamp.on()").
"""

def get_valid_combinations():
    """Genera le combinazioni valide di componenti."""
    valid_combos = []
    for combo_tuple in itertools.combinations(ALL_COMPONENTS, COMPONENT_NUMBER):
        combo = set(combo_tuple)
        has_input = bool(combo.intersection(INPUTS))
        has_output = bool(combo.intersection(OUTPUTS))
        if has_input and has_output:
            valid_combos.append(sorted(list(combo)))
    return valid_combos

def call_generative_agent(components_list):
    """Chiama Google Gemini con il prompt in Spagnolo."""
    
    # Prepara la stringa dei componenti per il messaggio utente
    components_str = ", ".join(components_list)
    
    # Messaggio utente in Spagnolo
    user_message = f"Las combinaciones que debes usar ahora son: {components_str}. Genera 20 objetos JSON."

    if SIMULATE_API_CALL:
        print("   (Simulación Activa)")
        time.sleep(SIMULATION_DELAY_SECONDS)
        # Dummy response per testare il flusso
        return json.dumps([{
            "componentUsed": components_list,
            "originalIdeaTitle": "Título de Prueba Simulado",
            "originalIdeaDescription": "Descripción simulada en español.",
            "transformedIdeaTitle": "Título Transformado Simulado",
            "transformedIdeaDescription": "Descripción transformada simulada.",
            "minAge": 10, "maxAge": 12, "difficultyLevel": 1,
            "algorithmUsed": "IF simulacion THEN exito()"
        }], indent=2)

    try:
        client = genai.Client(api_key=API_KEY)

        # Configurazione:
        # response_mime_type="application/json" costringe il modello a dare SOLO JSON valido.
        generate_config = types.GenerateContentConfig(
            temperature=1.0,
            response_mime_type="application/json", 
            system_instruction=[
                types.Part.from_text(text=SPANISH_SYSTEM_INSTRUCTION)
            ]
        )

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_message)]
                )
            ],
            config=generate_config
        )

        return response.text

    except Exception as e:
        print(f"   --> ERRORE Google Gemini: {e}")
        return json.dumps({"error": str(e)})

def main():
    output_dir = "dataset_gemini_es_2c"
    os.makedirs(output_dir, exist_ok=True)

    all_combinations = get_valid_combinations()
    total = len(all_combinations)

    print(f"--- Iniciando generación en Español para {total} combinaciones ---")

    for i, combo in enumerate(all_combinations):
        components_str = ", ".join(combo)
        filename = f"{'-'.join(combo)}.json"
        full_path = os.path.join(output_dir, filename)

        print(f"[{i+1}/{total}] Procesando: {components_str}")

        # Se vuoi saltare file già esistenti, decommenta:
        if os.path.exists(full_path):
            continue

        response_str = call_generative_agent(combo)

        # Salvataggio e validazione JSON
        try:
            data = json.loads(response_str)
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"   --> Guardado en: {full_path}")
        except json.JSONDecodeError:
            print("   --> ERROR: Respuesta no es un JSON válido. Guardando como texto.")
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(response_str)
        except Exception as e:
            print(f"   --> ERROR guardando archivo: {e}")

    print("--- Proceso completado ---")

if __name__ == "__main__":
    main()