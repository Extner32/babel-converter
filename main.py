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
from pint.errors import UndefinedUnitError, DimensionalityError, OffsetUnitCalculusError
from decimal import Decimal, getcontext
import re


# Set precision of decimal from 28 to 50
getcontext().prec = 50

ureg = UnitRegistry(non_int_type=Decimal, autoconvert_offset_to_baseunit=True)

MAX_DISPLAY_PRECISION = 5

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
    except OffsetUnitCalculusError:
        src = ureg.parse_expression(src, case_sensitive=False)
        dst = ureg.parse_expression(dst, case_sensitive=False)
        return src.to(dst)

    except UndefinedUnitError as e:
        e_value = str(e).split("'")[1]
        return f"I don't know the unit \"{e_value}\""
    except DimensionalityError as e:
        #e.g.: Cannot convert from 'centimeter' ([length]) to 'speed_of_light' ([length] / [time])
        e_values = re.split(r'\(|\)', str(e))
        e_values = [e_values[1], e_values[3]]
        return f"Dimension mismatch: {e_values[0]} to {e_values[1]}."
    
    
    except Exception as e:
        #return "I can't convert that!?"
        return str(e)



def format_quantity(q, digits):
    mag = round(q.magnitude, digits)

    # Format magnitude nicely
    if mag == int(mag):
        mag_str = str(int(mag))
    else:
        mag_str = f"{mag:.{digits}f}".rstrip('0').rstrip('.')

    unit_str = f"{q.units:~P}"

    return f"{mag_str} {unit_str}"


def number_to_clean_str(number, digits):
    if "." not in str(number):
        return str(int(number))
    
    if len(str(number)) > digits:
        s = str(round(number, digits)).rstrip("0")
        if s[-1] == ".":
            s = s[:-1]
        
        return s
    else:
        s = str(number).rstrip("0")
        if s[-1] == ".":
            s = s[:-1]
        
        return s 


class BabelExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        result = convert_units(event.get_argument())
        
        if type(result) != str:
            pretty_result = format_quantity(result, MAX_DISPLAY_PRECISION)
            str_result = number_to_clean_str(result.magnitude, MAX_DISPLAY_PRECISION)
            items.append(ExtensionResultItem(

                icon='images/fish.png',
                name=pretty_result,description=f"enter to copy {str_result} to clipboard",
                on_enter=CopyToClipboardAction(str_result)
            ))

        else:
            items.append(ExtensionResultItem(icon='images/fish-dead.png',name=result,on_enter=HideWindowAction()))

        return RenderResultListAction(items)
    



if __name__ == '__main__':
    BabelExtension().run()