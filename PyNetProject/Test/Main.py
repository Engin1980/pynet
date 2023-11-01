from Lib.sending import Sender
from Test.bodies import TestFullBody

print("Starting listener")



sender = Sender("localhost", 7007)
body = TestFullBody()

sender.send_object(body)

