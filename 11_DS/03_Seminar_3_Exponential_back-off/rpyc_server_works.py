import rpyc
from rpyc.utils.server import ThreadedServer
import datetime
import time
from functools import wraps
import random

date_time = datetime.datetime.now()


class MonitorService(rpyc.Service):
  def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
      def deco_retry(f):
          @wraps(f)
          def f_retry(*args, **kwargs):
              mtries, mdelay = tries, delay
              while mtries > 1:
                  try:
                      return f(*args, **kwargs)
                  #except ExceptionToCheck, e:
                  except ExceptionToCheck as e :
                      msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                      if logger:
                          logger.warning(msg)
                      else:
                          print(msg)
                      time.sleep(mdelay)
                      mtries -= 1
                      mdelay *= backoff
              return f(*args, **kwargs)

          return f_retry  

      return deco_retry # true decorator

  @retry(Exception, tries=4)
  def exposed_test_random(self):
      x = random.random()
      if x < 0.5:
          raise Exception("Fail")
      else:
          print("\nconnected on {}".format(date_time))

if __name__ == '__main__':

  t = ThreadedServer(MonitorService, port=18812)
  t.start()
