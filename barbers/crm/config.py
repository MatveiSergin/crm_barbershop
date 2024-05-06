from datetime import timedelta
from datetime import time
DURATION_OF_SERVICE = timedelta(minutes=30)

START_WORKING = time(hour=9, minute=0)
END_WORKING = time(hour=21, minute=0)

#Positions for providing services to clients
EMPLOYEE_POSITIONS = ('парикмахер', 'старший_парикмахер', 'стажер')