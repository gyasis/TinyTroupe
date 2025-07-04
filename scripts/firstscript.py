# %%
import json
import sys
sys.path.append('..')
import tinytroupe
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld, TinySocialNetwork
from tinytroupe.factory import TinyPersonFactory
from tinytroupe.extraction import default_extractor as extractor
from tinytroupe.extraction import ResultsReducer
import tinytroupe.control as control

from dotenv import load_dotenv

# Load environment variables from the specified .env file
load_dotenv(
    "/media/gyasis/Blade 15 SSD/Users/gyasi/Google Drive (not syncing)/Collection/chatrepository/.env",
    override=True,
)

# %%
#creating a fake banking environment

factory = TinyPersonFactory("One of the largest banks in Brazil, full of bureaucracy and legacy systems.")

#creating AI persona

customer = factory.generate_person(
    """
    The vice-president of one product innovation. Has a degree in engineering and a MBA in finance. 
    Is facing a lot of pressure from the board of directors to fight off the competition from the fintechs.    
    """
)
# %%

print(customer.minibio())
# %%
