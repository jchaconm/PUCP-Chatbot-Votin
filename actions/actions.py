from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from Levenshtein import distance
import requests
from transformers import *
import json 

#with open('partidos_politicos_data.json') as json_file:
# data = json.load(json_file)
data = []
TEMAS = ['Salud','Economía','Educación', 'Seguridad ciudadana'] #x terminar DEBE E estar igual que en el json de arriba

class ActionButton(Action):
    def name(self):
        return "action_buttons_topics"

    def run(self, dispatcher, tracker, domain):
        buttons = []
        for ix,t in enumerate(TEMAS):
            button_content = t
            payload = "/inform{\"tipo_tema\": \"" + str(ix) + "\"}"
            buttons.append(
                {"title": "{}".format(button_content),
                 "payload": payload})
        
        # TODO: update rasa core version for configurable `button_type`
        dispatcher.utter_button_template("utter_greet", buttons, tracker)
        return []
 
class ActionHelloWorld(Action):
    def name(self):
        return "action_helloworld"

    def run(self, dispatcher, tracker, domain):

        dispatcher.utter_message(f"Hello World, un clásico")
        return []
		
class ActionQuestionAnswering(Action):
    def name(self):
        return "action_question_answering"

    def run(self, dispatcher, tracker, domain):
        pregunta = None #reemplazar
        candidato  = None #reemplazar
        postulantes_lst = list(filter(lambda x: distance(x['candidato_nombres'], candidato) < 5, data))
        ix_postulante = data.index(postulantes_lst[0])
        if not postulantes_lst:
            output = "No se encontró la información del candidato lo sentimos"
        ngrok_ip = 'https://a10374d23683.ngrok.io'
        r = requests.get(ngrok_ip+'/tema-qa?index={ix_postulante}&question={pregunta}')
        answer = r.content.decode('UTF-8')        
        dispatcher.utter_message(f"{answer}")
        return []

class ActionGetHojaDeVida(Action):
    def name(self):
        return "action_hoja_de_vida"

    def run(self, dispatcher, tracker, domain):
        last_message = tracker.latest_message['text'] 
        #postulant = tracker.get_slot('postulant')
        postulantes_lst = list(filter(lambda x: distance(x['candidato_nombres'],last_message) < 5, data))
        if not postulantes_lst:
            output = "No se encontró la información que se esperaba :c . Lo sentimos"
        else:
            hoja_vida = postulantes_lst[0]['hoja_de_vida']
            output = ''
            for key,item  in hoja_vida.items():
                output += f'{key} : {item}\n'
        dispatcher.utter_message(f"{output}")
        return []

		
class ActionGetPlanGobiernoxTema(Action):
    def name(self):
        return "action_plan_gobierno_x_tema"

    def run(self, dispatcher, tracker, domain):
        categoria = tracker.latest_message['text'] 
        postulant = tracker.get_slot('postulant')
        postulantes_lst = [ix for ix,partido in enumerate(data) if distance(partido['candidato_nombres'],postulant) < 5]
        if not postulantes_lst:
            contenido = "No se encontró información del tema seleccionado para este candidato"
        else:
            postulant_ix = postulantes_lst[0]
            plan_tema = next(tema for tema in data[postulant_ix]['temas'] if tema['tema'] == categoria)
            contenido = "Su candidato plantea lo siguiente sobre " + categoria
            contenido += '\n'.join(plan_tema['contenido'])
        dispatcher.utter_message(f"{contenido}")
        return []