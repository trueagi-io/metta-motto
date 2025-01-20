import json
import time

from hyperon import MeTTa
from motto.agents import MettaScriptAgent, DialogAgent
from motto.thread_agents import ListeningAgent
from motto import get_sentence_from_stream_response
from motto.utils import encode_image

def test_stream_response():
    m = MeTTa()
    # we can run metta code from python directly and motto works
    m.run('!(import! &self motto)')
    result = m.run('!((chat-gpt-agent "gpt-3.5-turbo" True) (user "Who is John Lennon?"))', True)
    assert hasattr(result[0].get_object().content, "__stream__")


def test_no_stream_response():
    m = MeTTa()
    # we can run metta code from python directly and motto works
    m.run('!(import! &self motto)')
    result = m.run('!((chat-gpt-agent "gpt-3.5-turbo" False True) (user "Say meow"))', True)
    assert "meow" in str(result[0].get_object().content).lower()


def test_chat_gpt_additional_info():
    agent = MettaScriptAgent(path="basic_stream_call.msa")
    v = agent('(Messages (system  "You are Grace, you are in London")(user "Say meow"))',
              additional_info=[("model_name", "gpt-3.5-turbo", 'String'), ("is_stream", False, 'Bool'),
                               ("media_msg", "", 'String')]).content
    result = v[0].get_object().content
    assert "meow" in result.lower()


def test_chat_gpt_media():
    import importlib.util
    if importlib.util.find_spec('base64') is not None:
        base64_image = encode_image("data/peace.jpg")
        agent = MettaScriptAgent(path="basic_stream_call.msa")
        media_messages = {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "low"
                    }
                },
            ],
        }
        media = ('media_msg', json.dumps(media_messages), 'String')
        v = agent('(Messages (system  "You are Grace, you are in London")(user "What do you see on image"))',
                  additional_info=[("system_msg", "please answer with one sentence", 'String'),
                                   ("model_name", "gpt-4o", 'String'), ("is_stream", False, 'Bool'), media]).content
        result = v[0].get_object().content
        assert "dove" in result.lower()


def thread1(agent: DialogAgent):
    # Wait until value2 is updated by thread2
    time.sleep(1)
    agent.perform_canceling = True

def test_stream_response_processer():
    agent = DialogAgent(code='''
        (= (respond)((chat-gpt-agent "gpt-3.5-turbo" True True) (Messages (history)  (messages))) )
        (= (response) (respond))
    ''')
    agent('(Messages (system  "Who made significant advancements in the fields of electromagnetism?"))')

    for v in agent.process_last_stream_response():
        print(v)


def test_canceling():
    agent = ListeningAgent(code='''
        (= (respond)((chat-gpt-agent "gpt-3.5-turbo" True True) (Messages (history)  (messages))) )
        (= (response) (respond))
    ''')
    agent('(Messages (system  "Who made significant advancements in the fields of electromagnetism?"))')
    time.sleep(3)
    agent.stop()
    assert agent.has_output()

    agent('(Messages (system  "Who made significant advancements in the fields of electromagnetism?"))')

    agent.set_canceling_variable(True)
    time.sleep(3)
    agent.stop()
    assert (not agent.has_output())

def test_open_router_stream_sentence():
    code = '''
        (= (respond)
            ((open-router-agent "openai/gpt-3.5-turbo" True) (messages))
        )
        (= (response) (respond))
    '''
    agent = MettaScriptAgent(code=code)
    v = agent('(Messages (system  "You are Grace, you are in London")(user "Who was the 22nd President of France?"))')
    stream = get_sentence_from_stream_response(v.content)
    for chunk in stream:
        print(chunk)
        assert "president" in chunk.lower()

def test_chat_gpt_stream_sentence():
    code = '''
        (= (respond)
            ((chat-gpt-agent "gpt-3.5-turbo" True) (messages))
        )
          (= (response) (respond))
    '''
    agent = MettaScriptAgent(code=code)
    v = agent('(Messages (system  "You are Grace, you are in London")(user "Who was the 22nd President of France?"))')
    stream = get_sentence_from_stream_response(v.content)
    for chunk in stream:
        print(chunk)
        assert "president" in chunk.lower()
