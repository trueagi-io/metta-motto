import inspect
import json
from hyperon import *

assistant_role = 'assistant'

def get_grounded_atom_value(atom):
    return atom.get_object().content if isinstance(atom, GroundedAtom) else atom

def get_string(atom) -> str:
    item = str(atom)
    if len(item) > 2 and (item[0] == '"' and item[-1] == '"'):
        item = item[1:-1]
    return item

def get_string_value(atom) -> str:
    if isinstance(atom, str):
        return atom
    if isinstance(atom, GroundedAtom) and atom.get_grounded_type() == S('String'):
        return atom.get_object().content
    if isinstance(atom, SymbolAtom):
        return atom.get_name()
    return str(atom)


def contains_str(value, substring) -> bool:
    str1 = get_string_value(value)
    substring = get_string_value(substring)
    return substring.lower() in str1.lower()


def concat_str(left, right) -> str:
    str1 = get_string_value(left)
    str2 = get_string_value(right)
    return str1 + str2


def process_inner(inner_children):
    if len(inner_children) == 2:
        return (get_string_value(inner_children[0]), get_string_value(inner_children[1]))
    raise ValueError()


def message2tuple(msg_atom):
    messages = []
    if hasattr(msg_atom, 'get_children'):
        children = msg_atom.get_children()
        if (len(children) > 1) and repr(children[0]) == "Messages":
            for ch in children[1:]:
                if hasattr(ch, 'get_children'):
                    inner_children = ch.get_children()
                    messages.append(process_inner(inner_children))
        else:
            messages.append(process_inner(children))
    return messages

def process_openrouter_stream(response):
    if response.status_code == 200:
        for chunk in response.iter_lines():
            decoded_chunk = chunk.decode("utf-8")
            if (
                    "data:" in decoded_chunk
                    and decoded_chunk.split("data:")[1].strip()
            ):  # Check if the chunk is not empty
                try:
                    chunk_dict = json.loads(
                        decoded_chunk.split("data:")[1].strip()
                    )
                    yield chunk_dict["choices"][0]["delta"].get("content", "")
                except json.JSONDecodeError:
                    pass
    else:
        print(f"Error: {response.status_code}, {response.text}")
        raise Exception("Internal Server Error")

def process_openai_stream(response):
    for chunk in response:
        rez = chunk.choices[0].delta.content
        if rez != '' and rez is not None:
            yield rez

def get_token_from_stream_response(response):
    if isinstance(response, str):
        return response
    if isinstance(response, list):
        return get_token_from_stream_response(response[0])
    if isinstance(response, GroundedAtom):
        return get_token_from_stream_response(response.get_object().content)
    if hasattr(response, "status_code"):
        return process_openrouter_stream(response)
    return process_openai_stream(response)

def get_sentence_from_stream_response(response):
    it  =  get_token_from_stream_response(response)
    if isinstance(it, str):
        yield it
    else:
        sentence = ""
        for token in it:
            sentence += token
            sentence_strip = sentence.strip()
            if len(sentence_strip) > 0 and sentence_strip[-1] in ['.', '!', '?']:
                yield sentence_strip
                sentence = ""
        sentence_strip = sentence.strip()
        if len(sentence_strip) > 0:
            yield sentence_strip


def has_argument(func, arg_name):
    """
    Checks if a function has a given argument.

    :param func: The function to check.
    :param arg_name: The name of the argument to check for.
    :return: True if the argument exists, otherwise False.
    """
    try:
        signature = inspect.signature(func)
        return arg_name in signature.parameters
    except (TypeError, ValueError):
        return False

def get_ai_client(client_constructor, proxy):
    import httpx
    if proxy is not None:
        if has_argument(httpx.Client, "proxies"):
            client = client_constructor(http_client=httpx.Client(proxies=proxy))
        else:
            client = client_constructor(http_client=httpx.Client(proxy=proxy))
    else:
        client = client_constructor()
    return client