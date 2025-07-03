from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

#this stuff is to be able to include the pint lib directly as a vendor library
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vendor'))

from pint import UnitRegistry
from pint.errors import UndefinedUnitError, DimensionalityError
from decimal import Decimal
import re

ureg = UnitRegistry(non_int_type=Decimal)

def convert_units(user_input):
    try:
        user_input = user_input.split(' to ')
    except:
        return "Syntax: <number> <unit1> to <unit2>"
    
    if len(user_input) != 2:
        return "Add a second unit."
    
    src = user_input[0]
    dst = user_input[1]

    try:
        return ureg(src).to(dst)
    except UndefinedUnitError as e:
        e_value = str(e).split("'")[1]
        return f"I couldn't find the unit \"{e_value}\""
    except DimensionalityError as e:
        #e.g.: Cannot convert from 'centimeter' ([length]) to 'speed_of_light' ([length] / [time])
        e_values = re.split(r'\(|\)', str(e))
        e_values = [e_values[1], e_values[3]]
        return f"Dimension mismatch: {e_values[0]} to {e_values[1]}."
    except:
        return "I can't convert that!?"


def cleantruncate(number:float, max_digits:int, ellipsis="...") -> str:
    if (len(str(number)) > max_digits):
        if (max_digits-len(ellipsis)) > 0:
            return str(number)[0:max_digits-len(ellipsis)] + ellipsis
        else:
            return (str(number))[0:max_digits]
            
    return str(number)

#makes sure that a float datatype that is actually an integer doesn't have .0 at the end
#eg: 60.0 -> 60
def number_to_str(number):
    if (number - int(number)) == 0: #get the fractional part
        return str(int(number))
    else:
        return str(number)



class DemoExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        result = convert_units(event.get_argument())
        
        if type(result) != str:
            pretty_result = "{:~P}".format(result)
            items.append(ExtensionResultItem(

                icon='images/fish.png',
                name=pretty_result,description=f"enter to copy {result.magnitude} to clipboard",
                on_enter=CopyToClipboardAction(number_to_str(result.magnitude))
            ))

        else:
            items.append(ExtensionResultItem(icon='images/fish-dead.png',name=result,on_enter=HideWindowAction()))

        return RenderResultListAction(items)
    



if __name__ == '__main__':
    DemoExtension().run()