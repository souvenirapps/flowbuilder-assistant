from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import (SlotSet, EventType)
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import logging
logger = logging.getLogger(__name__)
ALLOWED_PIZZA_SIZES = ["small", "medium", "large",
                       "extra-large", "extra large", "s", "m", "l", "xl"]
ALLOWED_PIZZA_TYPES = ["mozzarella", "fungi", "veggie", "pepperoni", "hawaii"]
ALLOWED_RESOURCE_TYPES = ["variable", "variables",
                          "one dimensional array", "two dimensional array", "pointer", "pointers"]
ALLOWED_DATA_TYPES = ["short", "unsigned short", "int", "unsigned int", "long int",
                      "unsigned long int", "long long int", "unsigned long long int", "float", "double", "long double"]


class ValidateSimplePizzaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_pizza_form"

    def validate_pizza_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_size` value."""

        if slot_value.lower() not in ALLOWED_PIZZA_SIZES:
            dispatcher.utter_message(
                text=f"We only accept pizza sizes: s/m/l/xl.")
            return {"pizza_size": None}
        dispatcher.utter_message(
            text=f"OK! You want to have a {slot_value} pizza.")
        return {"pizza_size": slot_value}

    def validate_pizza_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_type` value."""

        if slot_value not in ALLOWED_PIZZA_TYPES:
            dispatcher.utter_message(
                text=f"I don't recognize that pizza. We serve {'/'.join(ALLOWED_PIZZA_TYPES)}.")
            return {"pizza_type": None}
        dispatcher.utter_message(
            text=f"OK! You want to have a {slot_value} pizza.")
        return {"pizza_type": slot_value}


class ValidateResourceForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_resource_form"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:

        additional_slots = []
        if tracker.slots.get("resource_type") == "one dimensional array":
            # If the user wants to sit outside, ask
            # if they want to sit in the shade or in the sun.
            additional_slots.append("data_types")
            additional_slots.append("variable_names")
            additional_slots.append("array_size")
        if tracker.slots.get("resource_type") == "two dimensional array":
            # If the user wants to sit outside, ask
            # if they want to sit in the shade or in the sun.
            additional_slots.append("data_types")
            additional_slots.append("variable_names")
            additional_slots.append("dimension1")
            additional_slots.append("dimension2")
        if tracker.slots.get("resource_type") == "variables" or tracker.slots.get("resource_type") == "pointer variables":
             additional_slots.append("data_types")
             additional_slots.append("variable_names")
        return additional_slots + domain_slots

    def validate_resource_type(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `resource_type` value."""

        if slot_value.lower() not in ALLOWED_RESOURCE_TYPES:
            dispatcher.utter_message(
                text=f"We only accept resource types: variable,one dimensional array,two dimensional array and pointer.")
            return {"resource_type": None}
        dispatcher.utter_message(
            text=f"OK! You want to add a resource type {slot_value}")
        return {"resource_type": slot_value}

    def validate_data_types(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `data_types` value."""
        if len(slot_value) == 0:
            dispatcher.utter_message(text=f"You need to specify data type")
            return {"data_types": None}
        dispatcher.utter_message(text=f"OK! You want to add a the following type of variables:,".join(
            tracker.get_slot("data_types")))
        return {"data_types": slot_value}

    def extract_variable_names(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate `variable_names` value."""
        logger.debug('in extract_variable_names:')
        logger.debug(tracker.get_slot('requested_slot'))

        
        if tracker.get_slot('requested_slot') == 'variable_names':
            variables = tracker.latest_message.get("text").split()
            variables = [x.strip() for x in variables]
            return {"variable_names": variables}
        else:
            if tracker.get_slot('requested_slot') == 'array_size' and tracker.latest_message.get("text").isnumeric():
                return {"array_size": tracker.latest_message.get("text")}
            elif tracker.get_slot('requested_slot') == 'dimension1' and tracker.latest_message.get("text").isnumeric():
                return {"dimension1": tracker.latest_message.get("text")}
            elif tracker.get_slot('requested_slot') == 'dimension2' and tracker.latest_message.get("text").isnumeric():
                return {"dimension2": tracker.latest_message.get("text")}
            else:
                intVariables = tracker.get_latest_entity_values(
                entity_type="variable_name", entity_group="int")
                longintVariables = tracker.get_latest_entity_values(
                entity_type="variable_name", entity_group="long int")
                doubleVariables = tracker.get_latest_entity_values(
                entity_type="variable_name", entity_group="double")
                variables = []
                if intVariables != None:
                    variables += list(intVariables)
                if longintVariables != None:
                    variables += list(longintVariables)
                if doubleVariables != None:
                    variables += list(doubleVariables)
                logger.debug(len(variables))
                if(len(variables) == 0):
                    variables = None
                return {"variable_names": variables}

    def validate_variable_names(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `variable_names` value."""
        if slot_value == None or slot_value[0] in ALLOWED_DATA_TYPES:
            return {"variable_names": None}
        if len(slot_value) == 0:
            dispatcher.utter_message(
                text=f"You need to specify at least one variable name")
            return {"variable_names": None}
        if(slot_value != None):
            dispatcher.utter_message(text=f"OK! You want to add a the following type of variables:,".join(
                str(v) for v in slot_value))
        return {"variable_names": slot_value}


class ActionAddResources(Action):
    """Transfers Money."""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_add_resources"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the action"""
        slots = {
            "resource_type": None,
            "variable_names": None,
            "data_types": None,
            "array_size": None,
            "int": None,
            "double": None,
            "long int": None,
            "long double": None,
            "long long int": None,
            "char": None,
            "short": None,
            "unsigned short": None,
            "float": None,
            "dimension1": None,
            "dimension2": None
        }

        if tracker.get_slot("resource_type") == "variables":
            if(len(tracker.get_slot("data_types")) == 1 and tracker.get_slot("variable_names") != None):
                variables = ",".join(str(v)
                                     for v in tracker.get_slot("variable_names"))
                dataType = tracker.get_slot("data_types")[0]
                dispatcher.utter_message(text=dataType + " "+variables+";")
            else:
                if tracker.get_slot("int") != None:
                    variables = ",".join(tracker.get_slot("int"))
                    dispatcher.utter_message(text=f"int "+variables+";")
                if tracker.get_slot("double") != None:
                    variables = ",".join(tracker.get_slot("double"))
                    dispatcher.utter_message(text=f"double "+variables+";")
                if tracker.get_slot("long int") != None:
                    variables = ",".join(tracker.get_slot("long int"))
                    dispatcher.utter_message(text=f"long int "+variables+";")
                if tracker.get_slot("long double") != None:
                    variables = ",".join(tracker.get_slot("long double"))
                    dispatcher.utter_message(
                        text=f"long double "+variables+";")
                if tracker.get_slot("long long int") != None:
                    variables = ",".join(tracker.get_slot("long long int"))
                    dispatcher.utter_message(
                        text=f"long long int "+variables+";")
                if tracker.get_slot("unsigned long long int") != None:
                    variables = ",".join(
                        tracker.get_slot("unsigned long long int"))
                    dispatcher.utter_message(
                        text=f"unsigned long long int "+variables+";")
                if tracker.get_slot("char") != None:
                    variables = ",".join(tracker.get_slot("char"))
                    dispatcher.utter_message(text=f"char "+variables+";")
        elif tracker.get_slot("resource_type") == "pointer variables":
            if(len(tracker.get_slot("data_types")) == 1 and tracker.get_slot("variable_names") != None):
                variables = ",*".join(str(v)
                                     for v in tracker.get_slot("variable_names"))
                dataType = tracker.get_slot("data_types")[0]
                dispatcher.utter_message(text=dataType + " "+variables+";")
            else:
                if tracker.get_slot("int") != None:
                    variables = ",*".join(tracker.get_slot("int"))
                    dispatcher.utter_message(text=f"int "+variables+";")
                if tracker.get_slot("double") != None:
                    variables = ",*".join(tracker.get_slot("double"))
                    dispatcher.utter_message(text=f"double "+variables+";")
                if tracker.get_slot("long int") != None:
                    variables = ",".join(tracker.get_slot("long int"))
                    dispatcher.utter_message(text=f"long int "+variables+";")
                if tracker.get_slot("long double") != None:
                    variables = ",".join(tracker.get_slot("long double"))
                    dispatcher.utter_message(
                        text=f"long double "+variables+";")
                if tracker.get_slot("long long int") != None:
                    variables = ",".join(tracker.get_slot("long long int"))
                    dispatcher.utter_message(
                        text=f"long long int "+variables+";")
                if tracker.get_slot("unsigned long long int") != None:
                    variables = ",".join(
                        tracker.get_slot("unsigned long long int"))
                    dispatcher.utter_message(
                        text=f"unsigned long long int "+variables+";")
                if tracker.get_slot("char") != None:
                    variables = ",".join(tracker.get_slot("char"))
                    dispatcher.utter_message(text=f"char "+variables+";")
        elif tracker.get_slot("resource_type") == "one dimensional array":
            if(len(tracker.get_slot("data_types")) == 1 and len(tracker.get_slot("variable_names")) > 0):
                variables = ",".join(str(v)
                                     for v in tracker.get_slot("variable_names"))
                dataType = tracker.get_slot("data_types")[0]
                dispatcher.utter_message(
                    text=dataType + " "+variables+"["+tracker.get_slot("array_size")+"];")
            else:
                if tracker.get_slot("int") != None:
                    variables = ",".join(tracker.get_slot("int"))
                    dispatcher.utter_message(
                        text=f"int "+variables+"["+tracker.get_slot("array_size")+"];")
                if tracker.get_slot("double") != None:
                    variables = ",".join(tracker.get_slot("double"))
                    dispatcher.utter_message(
                        text=f"double "+variables+"["+tracker.get_slot("array_size")+"];")
                if tracker.get_slot("long int") != None:
                    variables = ",".join(tracker.get_slot("long int"))
                    dispatcher.utter_message(
                        text=f"long int "+variables+"["+tracker.get_slot("array_size")+"];")
                if tracker.get_slot("long double") != None:
                    variables = ",".join(tracker.get_slot("long double"))
                    dispatcher.utter_message(
                        text=f"long double "+variables+"["+tracker.get_slot("array_size")+"];")
                if tracker.get_slot("long long int") != None:
                    variables = ",".join(tracker.get_slot("long long int"))
                    dispatcher.utter_message(
                        text=f"long long int "+variables+"["+tracker.get_slot("array_size")+"];")
                if tracker.get_slot("char") != None:
                    variables = ",".join(tracker.get_slot("char"))
                    dispatcher.utter_message(
                        text=f"char "+variables+"["+tracker.get_slot("array_size")+"];")
        elif tracker.get_slot("resource_type") == "two dimensional array":
            if(len(tracker.get_slot("data_types")) == 1 and len(tracker.get_slot("variable_names")) > 0):
                variables = ",".join(str(v)
                                     for v in tracker.get_slot("variable_names"))
                dataType = tracker.get_slot("data_types")[0]
                dispatcher.utter_message(
                    text=dataType + " "+variables+"["+tracker.get_slot("dimension1")+"]["+tracker.get_slot("dimension2")+"];")
        else:
            dispatcher.utter_message(
                text=f"Sorry! I can add only variables and one dimensional arrays right now")

        return [SlotSet(slot, value) for slot, value in slots.items()]
