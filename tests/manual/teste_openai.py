import openai
import traceback
from openai import OpenAI

print("Testando conexão com OpenAI...")

try:
    client = OpenAI()               # reads OPENAI_API_KEY from the environment
    resultado = client.models.list()
    print("Conexão estabelecida!")
    print("Modelos acessíveis:", len(resultado.data))
except openai.APIConnectionError as e:
    print("\nERRO DE CONEXÃO")
    print("Mensagem:", repr(e))
    print("Causa original:", repr(e.__cause__))
    traceback.print_exc()
except openai.APIError as e:
    print("\nERRO DA API")
    print("Tipo:", type(e).__name__)
    print("Mensagem:", str(e))
    print("Status:", getattr(e, "status_code", None))
except Exception as e:
    print("\nOUTRO ERRO")
    print(type(e).__name__, str(e))
    traceback.print_exc()