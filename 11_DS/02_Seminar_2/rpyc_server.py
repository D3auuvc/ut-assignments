import rpyc
from rpyc.utils.server import ThreadedServer
import datetime

date_time = datetime.datetime.now()


class MonitorService(rpyc.Service):
  def on_connect(self, conn):
    print("\nconnected on {}".format(date_time))

  def on_disconnect(self, conn):
    print("disconnected on {}\n".format(date_time))

  def exposed_bubble_sort(self, arr):
    import json
    try:
      print(f'Unsorted Array: {arr}')
      elements = json.loads(arr)
      # Looping from size of array from last index[-1] to index [0]
      for n in range(len(elements)-1, 0, -1):
         for i in range(n):
            if elements[i] > elements[i + 1]:
               # swapping data if the element is less than next element in the array
               elements[i], elements[i + 1] = elements[i + 1], elements[i]

      print(f'Sorted Array: {elements}')
    except Exception as e:
      print(f'[Error]: {e} ')


if __name__ == '__main__':

  t = ThreadedServer(MonitorService, port=18812)
  t.start()
