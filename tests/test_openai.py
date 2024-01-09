import unittest
from openai import OpenAI
import os

class TestOpenAI(unittest.TestCase):
  def test_openai_conn(self):
    api_key = os.environ["OPENAI_KEY"]
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
      ]
    )
    print(completion.choices[0].message)
    
  def test_openai_assistant(self):
    api_key = os.environ["OPENAI_KEY"]
    client = OpenAI(api_key=api_key)
    
    assistant = client.beta.assistants.create(
      instructions='''Выбрать категорию автомобильной запчасти из следующего списка: 
      'Тормозная система',
      'Запчасти двигателя',
      'Подвеска',
      'Коробка передач',
      'Охлаждение и отопление',
      'Электрика',
      'Кузов',
      'Смазки и жидкости',
      'Система выхлопа',
      'Рулевое управление',
      'Освещение'
      ''',
      model="gpt-3.5-turbo-0613",
      #model="gpt-3.5-turbo",
      tools=[{"type": "code_interpreter"}]
    )
    print(f"This is the assistant object: {assistant} \n")
    
    thread = client.beta.threads.create()
    print(f"This is the thread object: {thread} \n")
    
    thread_message = client.beta.threads.messages.create(
      thread_id=thread.id,
      role="user",
      content="верни только категорию без лишних слов - Диск сцепления",
    )
    
    run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
    )
    print(f"This is the run object: {run} \n")
    
    while run.status in ["queued", "in_progress"]:
      keep_retrieving_run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
      )
      print(f"Run status: {keep_retrieving_run.status}")

      if keep_retrieving_run.status == "completed":
        print("\n")

        all_messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        print("------------------------------------------------------------ \n")

        print(f"User: {thread_message.content[0].text.value}")
        print(f"Assistant: {all_messages.data[0].content[0].text.value}")

        break
      elif keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
        pass
      else:
        print(f"Run status: {keep_retrieving_run.status}")
        break
  
    

if __name__ == "__main__":
  unittest.main()