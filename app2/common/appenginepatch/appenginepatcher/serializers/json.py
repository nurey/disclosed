from django.core.serializers import json
from python import Deserializer
json.PythonDeserializer = Deserializer
from django.core.serializers.json import *
